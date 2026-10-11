import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { gzipSync } from 'node:zlib';

const root = new URL('../', import.meta.url);
export async function buildCompactReview({slug, title, previousBytes, referenceFile,
  referenceLabel = 'PNG reference', description = 'Original PNG beside the compact SVG, with matching scale and background.', sourceUrl}) {
if (!/^[a-z0-9-]+$/.test(slug) || !/^[A-Za-z ]+$/.test(title) || !(previousBytes > 0)) throw new Error('Invalid compact review description');
const svg = await readFile(new URL(`svg/${slug}.svg`, root));
const reference = referenceFile ? new URL(referenceFile, root) : new URL(`png/${slug}.png`, root);
const png = await readFile(reference);
const referenceHref = referenceFile ? reference.href : `../../png/${slug}.png`;
const version = createHash('sha256').update(svg).digest('hex').slice(0, 12);
const statistics = {
  bytes: svg.length,
  gzipBytes: gzipSync(svg, { level: 9 }).length,
  previousBytes,
  paths: (svg.toString().match(/<path\b/g) || []).length,
  gradients: (svg.toString().match(/<(?:linear|radial)Gradient\b/g) || []).length,
  stops: (svg.toString().match(/<stop\b/g) || []).length,
};
const pngVersion = createHash('sha256').update(png).digest('hex').slice(0, 12);
const reduction = (100 * (1 - statistics.bytes / statistics.previousBytes)).toFixed(1);
const html = `<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ForgeMoji · ${title} comparison</title>
<style>
:root{color-scheme:dark;--bg:#191b23;--panel:#222630;--ink:#f1eee6;--line:#444857}
body.light{color-scheme:light;--bg:#f5f3ed;--panel:#fffdf7;--ink:#29251d;--line:#d7d2c7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif}
main{max-width:1200px;margin:auto;padding:28px}h1{margin:0;font-size:28px}p{margin:8px 0 18px}a{color:inherit}
nav{display:flex;flex-wrap:wrap;align-items:center;gap:16px;margin:24px 0}button,select{font:inherit;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:7px 12px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:20px}figure{margin:0;background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;text-align:center}
figcaption{font-weight:650;margin-bottom:16px}.art{width:384px;height:auto;aspect-ratio:1;max-width:100%;object-fit:contain}.overlay{margin:24px auto 0;max-width:600px}.stack{position:relative;width:384px;aspect-ratio:1;max-width:100%;margin:auto}.stack img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain}#overlay-svg{opacity:.5}input{width:min(100%,340px);vertical-align:middle}small{display:block;margin-top:12px}
@media(max-width:720px){main{padding:16px}.pair{grid-template-columns:1fr}.art{height:auto;aspect-ratio:1}}
</style>
<main><h1>${title}</h1><p>${description}${sourceUrl ? ` <a href="${sourceUrl}">Reference source</a>.` : ''}</p>
<p><strong>${(statistics.bytes / 1000).toFixed(2)} KB SVG</strong> · ${(statistics.gzipBytes / 1000).toFixed(2)} KB compressed · ${reduction}% smaller · ${statistics.paths} paths and ${statistics.gradients} gradients</p>
<nav><label>Size <select id="size"><option>32</option><option>64</option><option>192</option><option selected>384</option><option>512</option><option>1024</option></select> px</label><button id="theme">Light background</button><a href="../../svg/${slug}.svg?v=${version}" download="${slug}.svg">Download SVG</a><a href="../../vector-review.html">Full collection</a></nav>
<section class="pair"><figure><figcaption>${referenceLabel}</figcaption><img class="art" src="${referenceHref}?v=${pngVersion}" alt="${referenceLabel}"></figure><figure><figcaption>Compact SVG</figcaption><img class="art" src="../../svg/${slug}.svg?v=${version}" alt="Rebuilt ${title} SVG"></figure></section>
<figure class="overlay"><figcaption>Overlay comparison</figcaption><div class="stack"><img src="${referenceHref}?v=${pngVersion}" alt="Reference beneath overlay"><img id="overlay-svg" src="../../svg/${slug}.svg?v=${version}" alt="SVG overlay"></div><label>SVG opacity <input id="blend" type="range" min="0" max="100" value="50"><output id="opacity">50%</output></label><small>0% shows the reference. 100% shows the SVG.</small></figure>
</main><script>
const size=document.querySelector('#size');size.addEventListener('change',()=>{for(const el of document.querySelectorAll('.art,.stack')){el.style.width=size.value+'px'}});
document.querySelector('#theme').addEventListener('click',()=>{const light=document.body.classList.toggle('light');document.querySelector('#theme').textContent=light?'Dark background':'Light background'});
document.querySelector('#blend').addEventListener('input',event=>{document.querySelector('#overlay-svg').style.opacity=event.target.value/100;document.querySelector('#opacity').value=event.target.value+'%'});
</script></html>\n`;
await mkdir(new URL('review/vectors/', root), { recursive: true });
await writeFile(new URL(`review/vectors/${slug}-review.html`, root), html);
console.log(`Built focused ${slug} comparison: ${statistics.bytes} bytes, ${reduction}% smaller.`);
}
