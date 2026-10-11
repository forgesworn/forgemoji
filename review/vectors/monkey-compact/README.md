# Monkey compact reconstruction

Reference: unchanged `png/monkey.png`, original 192×192 canvas.
Authoring: `scripts/monkey_vectors.py`, dispatched before the dense fallback.

Current SVG: 6,005 bytes plain, 1,770 bytes gzip (level 9), 9 paths,
11 gradients, 40 stops, four bounded filters. Previous: 104,041 bytes
plain, 15,633 bytes gzip. Plain size reduced 94.2%.

The ears, hair tuft, heart-shaped skin, eyes, nostrils and smiling mouth
are editable components. Broad material fields and restrained inset
shadows replace sampled colour rows. Shading is simplified; the source
PNG retains finer soft surface transitions.

`comparison.html` presents before/reference/after, overlay, silhouettes,
light/dark backgrounds and 24/32/64/native/512/1024 pixel views.
`chrome-checks.json` records actual Chrome checks at 32/64/192/512/1024.
Unoptimised and compact Chrome pixels match through 192 px. Differences
at larger sizes are confined to rendering/curve rounding and reviewed
visually in the compaction sheets. Owner visual acceptance is pending.

Validation: all seven existing package tests passed; internal references,
canvas and eight-pixel padding passed focused review. Original PNGs and
unrelated distributed SVGs retain their baseline SHA-256 hashes. The
review ZIP was refreshed and every SVG entry checked against distribution.
