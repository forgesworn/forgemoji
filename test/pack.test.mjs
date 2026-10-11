import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { inflateSync, gzipSync } from 'node:zlib';
import { definitions, artwork, vectorArtwork, version, withSkinTone } from '../index.mjs';
function decodeRgba(data) {
 const chunks=[];for(let offset=8;offset<data.length;) {
  const length=data.readUInt32BE(offset),kind=data.subarray(offset+4,offset+8).toString();
  if(kind==='IDAT')chunks.push(data.subarray(offset+8,offset+8+length));offset+=length+12;
 }
 const packed=inflateSync(Buffer.concat(chunks)),stride=192*4,pixels=Buffer.alloc(192*stride);
 const paeth=(a,b,c)=>{const p=a+b-c,pa=Math.abs(p-a),pb=Math.abs(p-b),pc=Math.abs(p-c);return pa<=pb&&pa<=pc?a:pb<=pc?b:c};
 for(let y=0;y<192;y++) {
  const filter=packed[y*(stride+1)];assert.ok(filter<=4);
  for(let x=0;x<stride;x++) {
   const index=y*stride+x,a=x>=4?pixels[index-4]:0,b=y?pixels[index-stride]:0,c=y&&x>=4?pixels[index-stride-4]:0;
   const delta=[0,a,b,Math.floor((a+b)/2),paeth(a,b,c)][filter];pixels[index]=(packed[y*(stride+1)+1+x]+delta)&255;
  }
 }return pixels;
}
test('manifest has a unique canonical everyday collection', async () => {
 assert.equal(version,JSON.parse(await readFile(new URL('../package.json',import.meta.url),'utf8')).version);
 assert.equal(definitions.length,133); assert.equal(artwork.length,163);
 assert.equal(new Set(definitions.map(item=>item.emoji)).size,133);
 assert.equal(new Set(artwork.map(item=>item.file)).size,163);
 assert.equal(new Set(artwork.map(item=>item.emoji)).size,163);
 assert.ok(definitions.every(item=>!item.title.toLowerCase().includes('flag')));
});
test('every PNG entry has a scalable vector with the same Unicode and tone', async () => {
 assert.equal(vectorArtwork.length,artwork.length);
 assert.deepEqual(vectorArtwork.map(({emoji,baseEmoji,slug,tone})=>({emoji,baseEmoji,slug,tone})),artwork.map(({emoji,baseEmoji,slug,tone})=>({emoji,baseEmoji,slug,tone})));
 for(const image of vectorArtwork) {
  assert.match(image.file,/^svg\/[a-z0-9-]+\.svg$/);
  const data=await readFile(new URL('../'+image.file,import.meta.url));
  assert.equal(data.length,image.bytes,image.file);
  assert.equal(createHash('sha256').update(data).digest('hex'),image.sha256,image.file);
  assert.deepEqual(data,await readFile(new URL('../sources/vectors/'+image.slug+'.svg',import.meta.url)));
  const svg=data.toString('utf8');
  assert.match(svg,/viewBox="0 0 192 192"/);
  assert.doesNotMatch(svg,/<image\b|data:image|<script\b|<foreignObject\b|<!ENTITY|(?:xlink:)?href\s*=\s*["'](?!#)/i,image.file);
  const ids=[...svg.matchAll(/\bid="([^"]+)"/g)].map(match=>match[1]);
  assert.equal(new Set(ids).size,ids.length,`${image.file}: duplicate SVG identifiers`);
  for(const reference of svg.matchAll(/(?:url\(#([^\)]+)\)|(?:xlink:)?href="#([^"]+)")/g)) {
   assert.ok(ids.includes(reference[1]??reference[2]),`${image.file}: missing paint, mask or shape ${reference[1]??reference[2]}`);
  }
 }
});
test('currency and brands are explicit symbols and known shortcodes', () => {
 const currency=definitions.find(item=>item.slug==='bitcoin');assert.equal(currency.emoji,'₿');assert.equal(currency.kind,'symbol');
 const spider=definitions.find(item=>item.slug==='jumping-spider');assert.equal(spider.emoji,'🕷️');
 const expected=['forgesworn','kindred','kithmoot','mysignet','vitark','vitark_den','vitark_train','vitark_still','vitark_record'].map(name=>`:fs_${name}:`);
 const custom=definitions.filter(item=>item.kind==='custom');assert.deepEqual(custom.map(item=>item.emoji),expected);
 for(const item of custom){assert.equal(item.category,'forgesworn');assert.equal(item.toneable,false);assert.equal(withSkinTone(item.emoji,5),item.emoji)}
 assert.equal(withSkinTone(':fs_unknown:',3),':fs_unknown:');assert.equal(withSkinTone('₿',4),'₿');
});
test('detailed familiar vectors stay within plain and compressed download budgets', async () => {
 const custom = new Set(definitions.filter(item=>item.kind==='custom').map(item=>item.slug));
 const rawLimits = {'monkey':16*1024,'tiger':16*1024,'lion':16*1024,'jumping-spider':768*1024,'sacred-stone':32*1024};
 const gzipLimits = {'monkey':4*1024,'tiger':4*1024,'lion':4*1024,'jumping-spider':192*1024,'sacred-stone':8*1024};
 const familiar=vectorArtwork.filter(item=>!custom.has(item.slug));
 let compressedTotal=0;
 for(const image of familiar) {
  assert.ok(image.bytes<=(rawLimits[image.slug]??256*1024),`${image.file}: plain SVG exceeds its detail budget`);
  const gzipBytes=gzipSync(await readFile(new URL('../'+image.file,import.meta.url)),{level:9}).length;
  assert.ok(gzipBytes<=(gzipLimits[image.slug]??48*1024),`${image.file}: compressed SVG exceeds its download budget`);
  compressedTotal+=gzipBytes;
 }
 assert.ok(familiar.reduce((sum,image)=>sum+image.bytes,0)<=10*1024*1024,'familiar SVG collection exceeds 10 MiB');
 assert.ok(compressedTotal<=1.8*1024*1024,'compressed familiar SVG collection exceeds 1.8 MiB');
});
test('the sacred stone uses interoperable rock Unicode and the exact community number', () => {
 const stone=definitions.find(item=>item.slug==='sacred-stone');
 assert.equal(stone.emoji,'🪨');assert.equal(stone.title,'Sacred stone');
 assert.ok(stone.keywords.includes('600000000000'));assert.ok(stone.keywords.includes('600.wtf'));
 assert.equal(withSkinTone('🪨',5),'🪨');
 assert.equal(artwork.find(item=>item.slug==='sacred-stone').file,'png/sacred-stone.png');
});
test('all six hand gestures have five human tones and a yellow default', () => {
 const hands = definitions.filter(item=>item.toneable); assert.equal(hands.length,6);
 for (const hand of hands) for(let tone=0;tone<=5;tone++) {
  const image=artwork.find(item=>item.baseEmoji===hand.emoji&&item.tone===tone);
  assert.ok(image,`${hand.emoji} tone ${tone}`);
  assert.equal(image.emoji,withSkinTone(hand.emoji,tone));
 }
 assert.equal(withSkinTone('👍🏿',3),'👍🏽'); assert.equal(withSkinTone('✌',2),'✌🏼');
 assert.equal(withSkinTone('✌🏽',0),'✌️'); assert.equal(withSkinTone('😂',4),'😂');
 assert.equal(withSkinTone('👽',3),'👽'); assert.throws(()=>withSkinTone('👍',6),RangeError);
});
test('every manifest image is a local transparent PNG with pinned bytes and hash', async () => {
 for(const image of artwork) {
  assert.match(image.file,/^png\/[a-z0-9-]+\.png$/);
  const data=await readFile(new URL('../'+image.file,import.meta.url));
  assert.equal(data.length,image.bytes,image.file);
  assert.equal(createHash('sha256').update(data).digest('hex'),image.sha256,image.file);
  assert.equal(data.subarray(0,8).toString('hex'),'89504e470d0a1a0a');
  assert.equal(data.readUInt32BE(16),192); assert.equal(data.readUInt32BE(20),192);
  assert.equal(data[24],8,'8-bit PNG');
  assert.equal(data[25],6,'RGBA PNG');
  const rgba=decodeRgba(data);let visible=0;
  for(let y=0;y<192;y++)for(let x=0;x<192;x++) {
   const alpha=rgba[(y*192+x)*4+3];if(alpha>32)visible++;
   if(x<8||x>=184||y<8||y>=184)assert.equal(alpha,0,`${image.file}: transparent 8px margin`);
  }
  assert.ok(visible>2000,`${image.file}: nonempty readable silhouette`);
  assert.ok(definitions.some(item=>item.emoji===image.baseEmoji));
 }
});
