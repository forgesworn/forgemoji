import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { sheets, definitions } from './definitions.mjs';
const root = fileURLToPath(new URL('../', import.meta.url));
const onlyIndex=process.argv.indexOf('--only');
const onlySource=onlyIndex<0?null:process.argv[onlyIndex+1]?.split(',');
if(onlyIndex>=0 && (!onlySource || onlySource.some(source=>!sheets.some(sheet=>sheet.file===source))))throw new Error('--only requires recorded source sheet filenames, separated by commas');
const changedBases=new Set(onlySource?sheets.filter(sheet=>onlySource.includes(sheet.file)).flatMap(sheet=>sheet.entries.map(item=>item.emoji)):[]);
const artwork = onlySource ? JSON.parse(await readFile(`${root}manifest.json`)).artwork.filter(item=>!changedBases.has(item.baseEmoji)) : [];
const sourceDimensions = new Map();
await mkdir(`${root}png`, { recursive: true });
// Isolate the central icon from disconnected fragments of neighbouring grid cells.
// Keep nearby detached details such as tears, applause strokes and confetti.
function isolate(rgba, width, height) {
 const labels=new Uint32Array(width*height);const components=[];let label=0;
 for(let pixel=0;pixel<labels.length;pixel++) {
  if(labels[pixel] || rgba[pixel*4+3]<32)continue;
  label++;const queue=[pixel];labels[pixel]=label;let minX=width,minY=height,maxX=0,maxY=0,sx=0,sy=0;
  for(let head=0;head<queue.length;head++) {
   const current=queue[head],x=current%width,y=Math.floor(current/width);sx+=x;sy+=y;minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y);
   for(const [nx,ny] of [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]) {
    if(nx<0||nx>=width||ny<0||ny>=height)continue;const next=ny*width+nx;
    if(!labels[next]&&rgba[next*4+3]>=32){labels[next]=label;queue.push(next)}
   }
  }
  components.push({label,area:queue.length,cx:sx/queue.length,cy:sy/queue.length,minX,minY,maxX,maxY});
 }
 const main=components.reduce((largest,item)=>!largest||item.area>largest.area?item:largest,null);
 if(!main)throw new Error('Empty icon cell');
 const retained=new Set(components.filter(item=>item===main || (item.area>=3 && Math.hypot(item.cx-main.cx,item.cy-main.cy)<Math.min(width,height)*0.46 && item.minX>1 && item.minY>1 && item.maxX<width-2 && item.maxY<height-2)).map(item=>item.label));
 let mask=Uint8Array.from(labels,item=>retained.has(item)?1:0);
 // Extend only three pixels to preserve smooth low-alpha antialiasing.
 for(let pass=0;pass<3;pass++) {
  const next=mask.slice();for(let pixel=0;pixel<mask.length;pixel++)if(mask[pixel]) {
   const x=pixel%width,y=Math.floor(pixel/width);
   for(let dx=-1;dx<=1;dx++)for(let dy=-1;dy<=1;dy++){const nx=x+dx,ny=y+dy;if(nx>=0&&nx<width&&ny>=0&&ny<height)next[ny*width+nx]=1}
  }mask=next;
 }
 let minX=width,minY=height,maxX=0,maxY=0;
 for(let pixel=0;pixel<mask.length;pixel++) {
  if(!mask[pixel])rgba[pixel*4+3]=0;
  if(rgba[pixel*4+3]){const x=pixel%width,y=Math.floor(pixel/width);minX=Math.min(minX,x);maxX=Math.max(maxX,x);minY=Math.min(minY,y);maxY=Math.max(maxY,y)}
 }
 return {rgba,minX,minY,width:maxX-minX+1,height:maxY-minY+1};
}
async function crop(source, columns, rows, index, definition, tone = 0, rowEdges = null) {
 if(!sourceDimensions.has(source)) sourceDimensions.set(source,JSON.parse(execFileSync('ffprobe',['-v','error','-select_streams','v:0','-show_entries','stream=width,height','-of','json',source])).streams[0]);
 const dimensions=sourceDimensions.get(source);
 const x0 = Math.floor(index % columns * dimensions.width / columns);
 const row = Math.floor(index / columns);
 const y0 = rowEdges ? rowEdges[row] : Math.floor(row * dimensions.height / rows);
 const width = Math.floor((index % columns + 1) * dimensions.width / columns) - x0;
 const height = (rowEdges ? rowEdges[row+1] : Math.floor((row+1) * dimensions.height / rows)) - y0;
 const slug = definition.slug + (tone ? `-tone${tone}` : '');
 const file = `png/${slug}.png`;
 const raw=execFileSync('ffmpeg',['-v','error','-i',source,'-vf',`crop=${width}:${height}:${x0}:${y0}`,'-frames:v','1','-f','rawvideo','-pix_fmt','rgba','pipe:1'],{maxBuffer:16*1024*1024});
 const icon=isolate(raw,width,height);
 execFileSync('ffmpeg',['-v','error','-y','-f','rawvideo','-pixel_format','rgba','-video_size',`${width}x${height}`,'-i','pipe:0','-vf',`crop=${icon.width}:${icon.height}:${icon.minX}:${icon.minY},scale=176:176:force_original_aspect_ratio=decrease:flags=lanczos,pad=192:192:(ow-iw)/2:(oh-ih)/2:color=0x00000000`,'-frames:v','1',`${root}${file}`],{input:icon.rgba});
 const bytes = await readFile(`${root}${file}`);
 const emoji = tone ? definition.emoji.replaceAll('\uFE0F','') + String.fromCodePoint(0x1F3FA + tone) : definition.emoji;
 artwork.push({ emoji, baseEmoji: definition.emoji, slug, tone, file, bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex') });
}
async function renderBrand(sheet) {
 const definition=sheet.entries[0],file=`png/${definition.slug}.png`,source=`${root}sources/${sheet.file}`;
 if(sheet.file.endsWith('.svg')) {
  const rendered=execFileSync('rsvg-convert',['--width','176','--height','176',source],{maxBuffer:16*1024*1024});
  execFileSync('ffmpeg',['-v','error','-y','-i','pipe:0','-vf','format=rgba,pad=192:192:(ow-iw)/2:(oh-ih)/2:color=0x00000000','-frames:v','1',`${root}${file}`],{input:rendered});
 } else execFileSync('ffmpeg',['-v','error','-y','-i',source,'-vf','format=rgba,scale=176:176:force_original_aspect_ratio=decrease:flags=lanczos,pad=192:192:(ow-iw)/2:(oh-ih)/2:color=0x00000000','-frames:v','1',`${root}${file}`]);
 const bytes=await readFile(`${root}${file}`);artwork.push({emoji:definition.emoji,baseEmoji:definition.emoji,slug:definition.slug,tone:0,file,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
}
for (const sheet of sheets) {
 if(onlySource && !onlySource.includes(sheet.file))continue;
 try { await readFile(`${root}sources/${sheet.file}`); } catch { if (process.argv.includes('--partial')) continue; throw new Error(`Missing ${sheet.file}`); }
 if(sheet.preserve)await renderBrand(sheet);
 else for (const [index, definition] of sheet.entries.entries()) await crop(`${root}sources/${sheet.file}`,sheet.cols,sheet.rows,index,definition,0,sheet.rowEdges);
}
const hands = definitions.filter(definition => definition.toneable);
if(!onlySource)for (let tone = 1; tone <= 5; tone++) for (let index = 0; index < hands.length; index++) await crop(`${root}sources/human-hands.png`,6,5,(tone-1)*6+index,hands[index],tone);
const manifest = { version:'0.1.2', creator:'TheCryptoDonkey', model:'gpt-image-2.5-sunburst', license:'MIT', definitions:[...hands,...definitions.filter(definition => !definition.toneable)], artwork };
await writeFile(`${root}manifest.json`,JSON.stringify(manifest,null,2)+'\n');
console.log(`Built ${artwork.length} PNGs; ${definitions.length} base definitions.`);
