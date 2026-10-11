"""Compare this quality pass to saved SVGs, and audit compaction visually.

Pass --baseline a saved repository containing svg/ and manifest.json.
Pass --unoptimised the masters saved immediately before running SVGO.
The report distinguishes intentional redraws from optimiser pixel error.
"""
import argparse
import gzip
import hashlib
import io
import json
import statistics
import subprocess
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--baseline', required=True, type=Path)
parser.add_argument('--unoptimised', required=True, type=Path)
args = parser.parse_args()
output = ROOT / 'review/vectors'
output.mkdir(parents=True, exist_ok=True)
manifest = json.loads((ROOT / 'manifest.json').read_text())
baseline = json.loads((args.baseline / 'manifest.json').read_text())
definitions = {d['emoji']: d for d in manifest['definitions']}
assets = manifest['vectorArtwork']
optimised = [a for a in assets if definitions[a['baseEmoji']].get('kind') != 'custom' and a['slug'] != 'happy']


def render(path, size=192):
    data = subprocess.check_output(['rsvg-convert', '-w', str(size), '-h', str(size), str(path)])
    return Image.open(io.BytesIO(data)).convert('RGBA')


def measure(asset):
    before = np.asarray(render(args.unoptimised / f'{asset["slug"]}.svg')).astype(float) / 255
    after = np.asarray(render(ROOT / asset['file'])).astype(float) / 255
    errors = []
    for background in [0, 1]:
        a = before[:, :, :3] * before[:, :, 3, None] + background * (1 - before[:, :, 3, None])
        b = after[:, :, :3] * after[:, :, 3, None] + background * (1 - after[:, :, 3, None])
        errors.append(np.abs(a - b) * 255)
    error = np.maximum(*errors)
    return {'slug': asset['slug'], 'meanAbsoluteChannelError': round(float(error.mean()), 4),
            'p99ChannelError': round(float(np.percentile(error, 99)), 3),
            'maxChannelError': round(float(error.max()), 3)}


with ThreadPoolExecutor(max_workers=4) as pool:
    compaction = list(pool.map(measure, optimised))
maximum = max(c['meanAbsoluteChannelError'] for c in compaction)
assert maximum < 2, f'Compaction changed the artwork materially: {maximum}'
print(f'Compaction raster comparison: worst mean channel error {maximum}/255.', flush=True)

for art in baseline['artwork']:
    assert hashlib.sha256((ROOT / art['file']).read_bytes()).hexdigest() == art['sha256'], f'Original PNG changed: {art["slug"]}'
for art in assets:
    if definitions[art['baseEmoji']].get('kind') == 'custom':
        assert (ROOT / art['file']).read_bytes() == (args.baseline / art['file']).read_bytes(), f'Brand SVG changed: {art["slug"]}'

rows = []
for art in assets:
    data = (ROOT / art['file']).read_bytes()
    rows.append({'slug': art['slug'], 'category': definitions[art['baseEmoji']]['category'],
                 'beforeBytes': (args.baseline / art['file']).stat().st_size,
                 'afterBytes': len(data), 'gzipBytes': len(gzip.compress(data, mtime=0))})
before_bytes = sum(r['beforeBytes'] for r in rows)
after_bytes = sum(r['afterBytes'] for r in rows)
report = {
    'scope': 'Owner feedback pass: reference-fitted animals, hands, food and objects, vegetarian pizza, DONKEY engraving, enlarged star eyes and photographic spider/stone. Compaction error compares the new masters before/after optimisation; the separate reference comparison measures design fidelity.',
    'beforeBytes': before_bytes, 'afterBytes': after_bytes,
    'reductionPercent': round((1 - after_bytes / before_bytes) * 100, 2),
    'medianBytes': statistics.median(r['afterBytes'] for r in rows),
    'gzipBytesSum': sum(r['gzipBytes'] for r in rows),
    'changedVectors': sum((ROOT / a['file']).read_bytes() != (args.baseline / a['file']).read_bytes() for a in assets),
    'originalPngsPreserved': len(baseline['artwork']), 'brandVectorsPreserved': 9,
    'categories': {}, 'compactionRenderComparison192px': compaction, 'assets': rows,
}
for category in sorted({r['category'] for r in rows}):
    group = [r for r in rows if r['category'] == category]
    report['categories'][category] = {'count': len(group), 'beforeBytes': sum(r['beforeBytes'] for r in group),
                                     'afterBytes': sum(r['afterBytes'] for r in group),
                                     'medianBytes': statistics.median(r['afterBytes'] for r in group),
                                     'maxBytes': max(r['afterBytes'] for r in group)}
# Measure the reviewed assets against their actual references. Keep intended
# semantic changes separate: veggie toppings, engraving and larger star eyes.
from detailed_vectors import supports, photo_source
reviewed = [a for a in assets if supports(a['slug']) or a['slug'] in {'pizza','star-eyes'}]
reference_comparisons = []
for art in reviewed:
    slug=art['slug']
    if slug in {'pizza','trophy','star-eyes'}: continue
    if slug=='sacred-stone':
        reference,_=photo_source(slug)
        reference=reference.resize((192,192),Image.Resampling.LANCZOS)
        reference_name='https://600.wtf/img/sacred-stone.webp'
    else:
        reference=Image.open(ROOT/'png'/f'{slug}.png').convert('RGBA')
        reference_name=f'png/{slug}.png'
    images=[reference,render(args.baseline/art['file']),render(ROOT/art['file'])]
    values=[np.asarray(im).astype(float)/255 for im in images]
    errors=[]
    for value in values[1:]:
        backgrounds=[]
        for bg in [0,1]:
            ref=values[0][:,:,:3]*values[0][:,:,3,None]+bg*(1-values[0][:,:,3,None])
            candidate=value[:,:,:3]*value[:,:,3,None]+bg*(1-value[:,:,3,None])
            backgrounds.append(abs(ref-candidate)*255)
        errors.append(float(np.maximum(*backgrounds).mean()))
    reference_comparisons.append({'slug':slug,'reference':reference_name,
        'beforeMeanAbsoluteChannelError':round(errors[0],4),
        'afterMeanAbsoluteChannelError':round(errors[1],4)})
report['referenceComparison192px']=reference_comparisons
report['referenceComparisonSummary']={
    'count':len(reference_comparisons),
    'improved':sum(r['afterMeanAbsoluteChannelError']<r['beforeMeanAbsoluteChannelError'] for r in reference_comparisons),
    'beforeMeanAbsoluteChannelError':round(statistics.mean(r['beforeMeanAbsoluteChannelError'] for r in reference_comparisons),4),
    'afterMeanAbsoluteChannelError':round(statistics.mean(r['afterMeanAbsoluteChannelError'] for r in reference_comparisons),4),
    'note':'Two background whole-image channel comparison at 192px; not a claim of aesthetic acceptance or unlimited source detail.'}
archive=output/'forgemoji-svg.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as bundle:
    for art in assets:bundle.write(ROOT/art['file'],art['file'])
with zipfile.ZipFile(archive) as bundle:
    assert len(bundle.namelist())==163
    assert bundle.testzip() is None
    for art in assets:assert bundle.read(art['file'])==(ROOT/art['file']).read_bytes()
report['svgArchive']={'file':'review/vectors/forgemoji-svg.zip','bytes':archive.stat().st_size,'entries':163,
    'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}
(output / 'quality-pass.json').write_text(json.dumps(report, indent=2) + '\n')

slugs = ['tiger','lion','cow','chicken','monkey','duck','whale','octopus','turtle','bee','rose','star','banana','apple','strawberry','watermelon','lemon','avocado','burger','fries','pizza','popcorn','cake','doughnut','cookie','cheers','coffee','ice-cream','key','camera','rocket','gamepad','football','trophy','sacred-stone','jumping-spider','thumbs-up','thumbs-down','wave','clap','thanks','peace','thumbs-up-tone5','peace-tone1']
lookup = {a['slug']: a for a in assets}
pngs = {a['slug']: a for a in manifest['artwork']}
panel, row_height = 600, 246
for theme, background, ink in [('dark', '#171a1f', '#fff'), ('light', '#faf8f2', '#272720')]:
    sheet = Image.new('RGB', (panel * 2, row_height * ((len(slugs)+1)//2) + 56), background)
    draw = ImageDraw.Draw(sheet)
    draw.text((18, 12), 'ForgeMoji quality pass · PNG reference / previous SVG / updated SVG', fill=ink)
    for i, slug in enumerate(slugs):
        art = lookup[slug]
        x, y = i % 2 * panel, i // 2 * row_height + 42
        draw.text((x + 12, y), slug, fill=ink)
        images = [Image.open(ROOT / pngs[slug]['file']).convert('RGBA'),
                  render(args.baseline / art['file']), render(ROOT / art['file'])]
        for col, (image, label) in enumerate(zip(images, ['PNG reference', 'Previous SVG', 'Updated SVG'])):
            sheet.paste(image, (x + col * 200 + 4, y + 20), image)
            draw.text((x + col * 200 + 8, y + 214), label, fill=ink)
    sheet.save(output / f'quality-pass-{theme}.png')
print('Reference comparison:',report['referenceComparisonSummary'],flush=True)
print('SVG archive:',report['svgArchive'],flush=True)
print(f'Saved quality report and side-by-side comparisons: {before_bytes:,} → {after_bytes:,} bytes.', flush=True)
