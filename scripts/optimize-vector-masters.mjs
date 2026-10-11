import { readFile, writeFile } from 'node:fs/promises';
import { optimize } from 'svgo';

const root = new URL('../', import.meta.url);
const manifest = JSON.parse(await readFile(new URL('manifest.json', root), 'utf8'));
const provenance = JSON.parse(await readFile(new URL('sources/vector-provenance.json', root), 'utf8'));
provenance.authoringTools.svgo = '4.1.0';
const selected = process.argv.find(arg => arg.startsWith('--only='))?.slice(7).split(',');
const custom = new Set(manifest.definitions.filter(d => d.kind === 'custom').map(d => d.slug));

// Fitted ramps often have more stops than their smooth colour curve needs.
// Preserve sharp transitions; remove a stop only within a one-channel error
// of 0.8/255, including alpha. Retain names used by the face authoring script.
const simplifyRamps = {
  name: 'simplifyMeasuredRamps',
  fn: () => ({ element: { enter(node) {
    if (!['linearGradient', 'radialGradient'].includes(node.name)) return;
    if (node.children.some(child => child.type !== 'element' || child.name !== 'stop')) return;
    const stops = node.children;
    if (stops.length < 3) return;
    const samples = stops.map(stop => {
      const a = stop.attributes, raw = a['stop-color'];
      if (!/^#[\da-f]{3}(?:[\da-f]{3})?$/i.test(raw || '')) return null;
      const hex = raw.length === 4 ? [...raw.slice(1)].map(c => c + c).join('') : raw.slice(1);
      const offset = a.offset?.endsWith('%') ? parseFloat(a.offset) / 100 : Number(a.offset || 0);
      return { offset, value: [0, 2, 4].map(i => parseInt(hex.slice(i, i + 2), 16)).concat(Math.max(0, Math.min(1, Number(a['stop-opacity'] ?? 1))) * 255) };
    });
    if (samples.some(s => !s) || samples.some((s, i) => i && s.offset <= samples[i - 1].offset)) return;
    const keep = new Set([0, stops.length - 1]), pending = [[0, stops.length - 1]];
    while (pending.length) {
      const [start, end] = pending.pop();
      let maximum = 0.8, split;
      for (let i = start + 1; i < end; i++) {
        const t = (samples[i].offset - samples[start].offset) / (samples[end].offset - samples[start].offset);
        const error = Math.max(...samples[i].value.map((v, c) => Math.abs(v - samples[start].value[c] * (1 - t) - samples[end].value[c] * t)));
        if (error > maximum) { maximum = error; split = i; }
      }
      if (split !== undefined) { keep.add(split); pending.push([start, split], [split, end]); }
    }
    node.children = stops.filter((_, i) => keep.has(i));
  } } }),
};

let before = 0, after = 0, count = 0;
for (const art of manifest.artwork) {
  if (custom.has(art.slug) || art.slug === 'happy' || (selected && !selected.includes(art.slug))) continue;
  const source = new URL(`sources/vectors/${art.slug}.svg`, root);
  const input = await readFile(source, 'utf8');
  const result = optimize(input, {
    path: source.pathname, multipass: true, floatPrecision: 3,
    plugins: [simplifyRamps, { name: 'preset-default', params: { overrides: { cleanupIds: false } } }],
  });
  const candidate = result.data + '\n';
  const output = Buffer.byteLength(candidate) <= Buffer.byteLength(input) ? candidate : input;
  if (!output.includes('viewBox="0 0 192 192"')) throw new Error(`${art.slug}: lost scalable viewBox`);
  // Some densely fitted ramps are already shorter than SVGO's normalisation.
  // Keep that smaller master, without blocking optimisation of other artwork.
  await writeFile(source, output);
  const record = provenance.artwork.find(item => item.slug === art.slug);
  record.bytes = Buffer.byteLength(output);
  record.optimisation = 'SVGO 4.1.0; three-decimal geometry; colour/alpha ramp error bounded at 0.8/255';
  before += Buffer.byteLength(input); after += record.bytes; count++;
}
await writeFile(new URL('sources/vector-provenance.json', root), JSON.stringify(provenance, null, 2) + '\n');
console.log(`Compacted ${count} familiar SVG masters: ${before.toLocaleString()} → ${after.toLocaleString()} bytes.`);
