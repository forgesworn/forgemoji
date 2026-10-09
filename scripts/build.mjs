import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { sheets, definitions } from './definitions.mjs';
const root = fileURLToPath(new URL('../', import.meta.url));
const artwork = [];
await mkdir(`${root}png`, { recursive: true });
async function crop(source, columns, rows, index, definition, tone = 0) {
 const dimensions = JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',source])).streams[0];
 const x0 = Math.floor(index % columns * dimensions.width / columns);
 const y0 = Math.floor(Math.floor(index / columns) * dimensions.height / rows);
 const width = Math.floor((index % columns + 1) * dimensions.width / columns) - x0;
 const height = Math.floor((Math.floor(index / columns) + 1) * dimensions.height / rows) - y0;
 const slug = definition.slug + (tone ? `-tone${tone}` : '');
 const file = `png/${slug}.png`;
 execFileSync('ffmpeg',['-v','error','-y','-i',source,'-vf',`crop=${width}:${height}:${x0}:${y0},scale=176:176:force_original_aspect_ratio=decrease:flags=lanczos,pad=192:192:(ow-iw)/2:(oh-ih)/2:color=0x00000000`,'-frames:v','1',`${root}${file}`]);
 const bytes = await readFile(`${root}${file}`);
 const emoji = tone ? definition.emoji.replaceAll('\uFE0F','') + String.fromCodePoint(0x1F3FA + tone) : definition.emoji;
 artwork.push({ emoji, baseEmoji: definition.emoji, slug, tone, file, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
}
for (const sheet of sheets) {
 try { await readFile(`${root}sources/${sheet.file}`); } catch { if (process.argv.includes('--partial')) continue; throw new Error(`Missing ${sheet.file}`); }
 for (const [index, definition] of sheet.entries.entries()) await crop(`${root}sources/${sheet.file}`,sheet.cols,sheet.rows,index,definition);
}
const hands = definitions.filter(definition => definition.toneable);
for (let tone = 1; tone <= 5; tone++) for (let index = 0; index < hands.length; index++) await crop(`${root}sources/human-hands.png`,6,5,(tone-1)*6+index,hands[index],tone);
const manifest = { version:'0.1.0', creator:'TheCryptoDonkey', model:'gpt-image-2.5-sunburst', license:'MIT', definitions:[...hands,...definitions.filter(definition => !definition.toneable)], artwork };
await writeFile(`${root}manifest.json`,JSON.stringify(manifest,null,2)+'\n');
console.log(`Built ${artwork.length} PNGs; ${definitions.length} base definitions.`);
