import { access } from 'node:fs/promises';
import { buildCompactReview } from './build-compact-review.mjs';

// Explicit reauthoring creates this pinned, aligned photographic reference
// outside the repository. A normal SVG build needs neither Python nor a photo.
const referenceFile = 'file:///private/tmp/forgemoji-sacred-stone-review-reference.png';
let cached = process.env.FORGEMOJI_LOCAL_STONE_REFERENCE === '1';
if (cached) {
  try { await access(new URL(referenceFile)); } catch { cached = false; }
}
await buildCompactReview({
  slug: 'sacred-stone', title: 'Sacred stone', previousBytes: 413657,
  referenceFile: cached ? referenceFile : undefined,
  referenceLabel: cached ? 'Real stone photograph' : 'Earlier illustrated PNG',
  description: cached
    ? 'The real stone beside its compact SVG. Gradients and procedural grain recreate its weathered material; individual photographic grains are not copied.'
    : 'The compact SVG follows the real community stone, linked below. This portable comparison shows the earlier illustration beside the new SVG.',
  sourceUrl: 'https://600.wtf/',
});
