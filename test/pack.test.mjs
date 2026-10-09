import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { inflateSync } from 'node:zlib';
import { definitions, artwork, withSkinTone } from '../index.mjs';
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
test('manifest has a unique canonical everyday collection', () => {
 assert.equal(definitions.length,121); assert.equal(artwork.length,151);
 assert.equal(new Set(definitions.map(item=>item.emoji)).size,121);
 assert.equal(new Set(artwork.map(item=>item.file)).size,151);
 assert.equal(new Set(artwork.map(item=>item.emoji)).size,151);
 assert.ok(definitions.every(item=>!item.title.toLowerCase().includes('flag')));
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
