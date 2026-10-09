import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { definitions, artwork, withSkinTone } from '../index.mjs';
test('manifest has a unique canonical everyday collection', () => {
 assert.equal(definitions.length,120); assert.equal(artwork.length,150);
 assert.equal(new Set(definitions.map(item=>item.emoji)).size,120);
 assert.equal(new Set(artwork.map(item=>item.file)).size,150);
 assert.equal(new Set(artwork.map(item=>item.emoji)).size,150);
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
  assert.equal(data[25],6,'RGBA PNG');
  assert.ok(definitions.some(item=>item.emoji===image.baseEmoji));
 }
});
