import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('manifest.json', root), 'utf8'));
manifest.version = JSON.parse(await readFile(new URL('package.json', root), 'utf8')).version;
await mkdir(new URL('svg/', root), { recursive: true });
const vectors = [];
for (const original of manifest.artwork) {
  const source = new URL(`sources/vectors/${original.slug}.svg`, root);
  const data = await readFile(source);
  const svg = data.toString('utf8');
  if (/<image\b|data:image|<script\b|<!ENTITY/i.test(svg)) throw new Error(`Unexpected raster or active content: ${original.slug}`);
  if (!svg.includes('viewBox="0 0 192 192"')) throw new Error(`Missing scalable viewBox: ${original.slug}`);
  const file = `svg/${original.slug}.svg`;
  await writeFile(new URL(file, root), data);
  vectors.push({ emoji: original.emoji, baseEmoji: original.baseEmoji, slug: original.slug, tone: original.tone, file, bytes: data.length, sha256: createHash('sha256').update(data).digest('hex') });
}
manifest.vectorArtwork = vectors;
await writeFile(new URL('manifest.json', root), JSON.stringify(manifest, null, 2) + '\n');
console.log(`Built ${vectors.length} SVGs from checked-in vector masters.`);
