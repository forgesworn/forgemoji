"""Rebuild ForgeMoji artwork as smooth material shapes and continuous shading.

Requires Pillow, NumPy, SciPy and OpenCV. This is an authoring operation;
normal package builds copy the checked-in vector masters without Python.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import re
import xml.etree.ElementTree as ET
import cv2
import numpy as np
from PIL import Image
from vector_details import star_eyes, thinking_hand, stone
from clean_vectors import CLEAN_SLUGS, rebuild as rebuild_clean
from familiar_vectors import supports as supports_familiar, rebuild as rebuild_familiar
from detailed_vectors import supports as supports_detailed, rebuild as rebuild_detailed
from scipy.interpolate import splprep, splev, PchipInterpolator
from scipy.ndimage import binary_fill_holes, distance_transform_edt, gaussian_filter

cv2.setNumThreads(1)
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'sources/vectors'
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
parser = argparse.ArgumentParser()
parser.add_argument('--only', help='Comma-separated artwork slugs')
args = parser.parse_args()
selected = set(args.only.split(',')) if args.only else None
pack = json.loads((ROOT / 'manifest.json').read_text())
definitions = {d['emoji']:d for d in pack['definitions']}
OUT.mkdir(parents=True, exist_ok=True)
accepted_happy = OUT / 'happy.svg'
if not accepted_happy.exists(): accepted_happy = ROOT / 'experiments/quality-study/happy-rebuilt.svg'
happy_root = ET.fromstring(accepted_happy.read_text())
gold_ids = {'gold','edge-color','edge-mask','sphere-shading','top-shine','cheek','right-cheek'}
gold_defs = ''.join(ET.tostring(n, encoding='unicode') for n in happy_root.find(f'{{{NS}}}defs') if n.get('id') in gold_ids)
single_sources = {'crypto-donkey':'crypto-donkey.png','jumping-spider':'jumping-spider.png','bitcoin':'bitcoin.png','sacred-stone':'sacred-stone.png','fs-forgesworn':'brands/fs-forgesworn.png'}
brand_sources = {p.stem:p for p in (ROOT/'sources/brands').glob('*.svg')}

def fmt(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.')

def colour(values):
    return '#' + ''.join(f'{int(np.clip(round(x),0,255)):02x}' for x in values)

def path_for(mask, scale, fine=False):
    contours, hierarchy = cv2.findContours(mask.astype(np.uint8),cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
    paths=[]
    for contour in contours:
        points=contour[:,0,:].astype(float)
        if len(points)<3 or abs(cv2.contourArea(contour))*scale**2<.30:
            continue
        points=(points+.5)*scale
        if len(points)<8:
            paths.append('M'+'L'.join(f'{fmt(x)} {fmt(y)}' for x,y in points)+'Z')
            continue
        closed=np.vstack([points,points[0]])
        try:
            tck,_=splprep(closed.T,s=len(points)*(.045 if fine else .28)*scale**2,per=True)
            knots=np.unique(np.clip(tck[0],0,1))
            start=np.array(splev(0,tck))
            result=f'M{fmt(start[0])} {fmt(start[1])}'
            for a,b in zip(knots[:-1],knots[1:]):
                p0,p3=np.array(splev(a,tck)),np.array(splev(b,tck))
                p1=p0+np.array(splev(a,tck,der=1))*(b-a)/3
                p2=p3-np.array(splev(b,tck,der=1))*(b-a)/3
                result+='C'+' '.join(fmt(v) for v in np.r_[p1,p2,p3])
            paths.append(result+'Z')
        except ValueError:
            simple=cv2.approxPolyDP(contour,.35/scale,True)[:,0,:]*scale+.5*scale
            paths.append('M'+'L'.join(f'{fmt(x)} {fmt(y)}' for x,y in simple)+'Z')
    return ''.join(paths)

def load_art(slug, filename):
    source=ROOT/filename
    image=Image.open(source).convert('RGBA')
    if slug in single_sources:
        source=ROOT/'sources'/single_sources[slug]
        original=Image.open(source).convert('RGBA')
        alpha=np.array(original)[:,:,3]
        ys,xs=np.where(alpha>=32)
        original=original.crop((xs.min(),ys.min(),xs.max()+1,ys.max()+1))
        original.thumbnail((352,352),Image.Resampling.LANCZOS)
        image=Image.new('RGBA',(384,384))
        image.paste(original,((384-original.width)//2,(384-original.height)//2))
    return np.array(image),source

def material_labels(rgba, category):
    rgb=rgba[:,:,:3].astype(float)
    hsv=cv2.cvtColor(rgb.astype(np.float32)/255,cv2.COLOR_RGB2HSV)
    hue,saturation=hsv[:,:,0],hsv[:,:,1]
    light=np.max(rgb,axis=2)
    visible=rgba[:,:,3]>=90
    labels=np.zeros(visible.shape,dtype=np.uint8)
    labels[(hue<15)|(hue>=345)]=1
    labels[(hue>=15)&(hue<75)]=2
    labels[(hue>=75)&(hue<160)]=3
    labels[(hue>=160)&(hue<205)]=4
    labels[(hue>=205)&(hue<255)]=5
    labels[(hue>=255)&(hue<300)]=6
    labels[(hue>=300)&(hue<345)]=7
    labels[saturation<.15]=8
    labels[(hue<75)&(light<145)&(saturation>=.15)]=9
    labels[light<65]=10
    if category=='Hands':
        labels[(hue<75)&(saturation>=.09)]=2
    golden=False
    if category=='Faces':
        labels[(hue<75)&(light<180)&(saturation>=.15)]=9
        gold=(hue>=15)&(hue<75)&(light>185)&(saturation>=.14)&visible
        golden=np.sum(gold)>np.sum(visible)*.28
        if golden: labels[gold]=2
        labels[labels==10]=9
        labels[labels==7]=1
    labels[~visible]=0
    return labels,visible,golden

def shading_field(identifier, sample_mask, geometry_mask, rgba, scale, detail_step=None):
    """A smooth vector colour surface, with a coarse set of colour controls.

    The SVG holds ordinary coloured paths and a Gaussian filter, not a bitmap.
    Colour controls are independent of output resolution; the filter scales
    with the artwork and keeps the fitted field continuous when enlarged.
    """
    ys,xs=np.where(geometry_mask)
    x0,x1=(xs.min()+.5)*scale,(xs.max()+.5)*scale
    y0,y1=(ys.min()+.5)*scale,(ys.max()+.5)*scale
    step=detail_step or max(2,min(5,max(x1-x0,y1-y0)/38))
    _,nearest=distance_transform_edt(~sample_mask,return_indices=True)
    rgb=rgba[nearest[0],nearest[1],:3].astype(float)
    rgb=gaussian_filter(rgb,((.22 if detail_step else .65)/scale,(.22 if detail_step else .65)/scale,0))
    groups={}
    for y in np.arange(y0-step,y1+step,step):
        for x in np.arange(x0-step,x1+step,step):
            px=int(np.clip((x+step/2)/scale,0,rgba.shape[1]-1))
            py=int(np.clip((y+step/2)/scale,0,rgba.shape[0]-1))
            value=colour(np.round(rgb[py,px]/3)*3)
            groups.setdefault(value,[]).append(f'M{fmt(x)} {fmt(y)}h{fmt(step+.04)}v{fmt(step+.04)}h-{fmt(step+.04)}Z')
    shader=f'<g id="{identifier}-paint" filter="url(#{identifier}-smooth)">'+''.join(f'<path fill="{value}" d="'+''.join(paths)+'"/>' for value,paths in groups.items())+'</g>'
    definition=f'<filter id="{identifier}-smooth" filterUnits="userSpaceOnUse" x="0" y="0" width="192" height="192" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="{fmt(step*.55)}"/></filter>'+shader
    return definition,f'<use href="#{identifier}-paint" mask="url(#{identifier}-mask)"/>'

def gradient_for(identifier, mask, rgba, scale):
    ys,xs=np.where(mask)
    data=rgba[ys,xs,:3].astype(float)
    if len(xs)<22 or np.mean(np.std(data,axis=0))<2.4:
        return '',colour(np.median(data,axis=0)),0.
    # Bound the fitting workload while retaining deterministic sample locations.
    take=np.linspace(0,len(xs)-1,min(len(xs),2400)).astype(int)
    x,y=(xs[take]+.5)*scale,(ys[take]+.5)*scale
    pixels=data[take]
    cx,cy=(x.min()+x.max())/2,(y.min()+y.max())/2
    rx,ry=max((x.max()-x.min())/2,1),max((y.max()-y.min())/2,1)
    candidates=[]
    for angle in [0,math.pi/4,math.pi/2,3*math.pi/4]:
        u=x*math.cos(angle)+y*math.sin(angle)
        lo,hi=np.percentile(u,[0,100]);span=max(hi-lo,1)
        candidates.append(('linear',(u-lo)/span,(cx,cy,math.cos(angle),math.sin(angle),lo,hi)))
    lum=pixels@np.array([.2126,.7152,.0722])
    bright=np.argsort(lum)[-max(3,len(x)//12):]
    for ox,oy in [(cx,cy),(cx,cy-ry*.55),(cx-rx*.35,cy-ry*.35),(np.mean(x[bright]),np.mean(y[bright]))]:
        u=np.sqrt(((x-ox)/rx)**2+((y-oy)/ry)**2)
        span=max(np.max(u),.1)
        candidates.append(('radial',u/span,(ox,oy,rx*span,ry*span)))
    node_positions=np.linspace(0,1,6)
    best=None
    for kind,t,geometry in candidates:
        # Continuous colour fit, regularised against abrupt changes in shading.
        basis=np.column_stack([np.maximum(0,1-np.abs(t-pos)*5) for pos in node_positions])
        penalty=np.diff(np.eye(6),n=2,axis=0)*math.sqrt(len(t)*.003)
        coefficients=np.linalg.lstsq(np.vstack([basis,penalty]),np.vstack([pixels,np.zeros((4,3))]),rcond=None)[0]
        coefficients=np.clip(coefficients,0,255)
        error=np.mean((basis@coefficients-pixels)**2)
        if best is None or error<best[0]: best=(error,kind,geometry,coefficients)
    error,kind,geometry,coefficients=best
    stops=[]
    curve=PchipInterpolator(node_positions,coefficients,axis=0)
    for pos in np.linspace(0,1,17):
        stops.append(f'<stop offset="{fmt(pos)}" stop-color="{colour(curve(pos))}"/>')
    if kind=='linear':
        cx,cy,dx,dy,lo,hi=geometry
        centre=cx*dx+cy*dy
        x1,y1=cx+(lo-centre)*dx,cy+(lo-centre)*dy
        x2,y2=cx+(hi-centre)*dx,cy+(hi-centre)*dy
        definition=f'<linearGradient id="{identifier}" gradientUnits="userSpaceOnUse" x1="{fmt(x1)}" y1="{fmt(y1)}" x2="{fmt(x2)}" y2="{fmt(y2)}">'+''.join(stops)+'</linearGradient>'
    else:
        ox,oy,rx,ry=geometry
        definition=f'<radialGradient id="{identifier}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="1" gradientTransform="translate({fmt(ox)} {fmt(oy)}) scale({fmt(rx)} {fmt(ry)})">'+''.join(stops)+'</radialGradient>'
    return definition,f'url(#{identifier})',math.sqrt(error)

def wrap_brand(source,title):
    original=ET.fromstring(source.read_text())
    original.set('x','8');original.set('y','8');original.set('width','176');original.set('height','176')
    return f'<svg xmlns="{NS}" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="{title}">'+ET.tostring(original,encoding='unicode')+'</svg>\n'

records=[]
for art in pack['artwork']:
    slug=art['slug']
    if selected and slug not in selected: continue
    definition=definitions[art['baseEmoji']]
    title=definition['title'] + (f" · skin tone {art['tone']}" if art['tone'] else '')
    if slug=='happy':
        svg=accepted_happy.read_text()
        source=accepted_happy
        strategy='approved-reference-reconstruction'
        path_count=len(re.findall(r'<path\b',svg))
    elif supports_detailed(slug):
        svg,detail_record=rebuild_detailed(slug,title)
        source=detail_record['source']
        strategy=detail_record['strategy']
        path_count=len(re.findall(r'<path\b',svg))
    elif supports_familiar(slug):
        source=ROOT/art['file']
        svg=rebuild_familiar(slug,title)
        strategy='component-authored-familiar-geometry-and-compact-continuous-shading'
        path_count=len(re.findall(r'<path\b|<ellipse\b',svg))
    elif slug in CLEAN_SLUGS:
        source=ROOT/art['file']
        svg=rebuild_clean(slug,title,gold_defs)
        strategy='component-authored-native-geometry-and-continuous-shading'
        path_count=len(re.findall(r'<path\b|<ellipse\b',svg))
    elif slug in brand_sources:
        source=brand_sources[slug]
        svg=wrap_brand(source,title)
        strategy='preserved-owned-vector-master'
        path_count=len(re.findall(r'<path\b',svg))
    else:
        rgba,source=load_art(slug,art['file'])
        scale=192/rgba.shape[0]
        labels,visible,golden=material_labels(rgba,definition['category'])
        if slug in {'angry','furious','hot-face','mind-blown'}: golden=False
        silhouette=path_for(visible,scale,fine=slug in ['sacred-stone','fs-forgesworn'])
        if not silhouette: raise ValueError(f'Empty silhouette: {slug}')
        counts=np.bincount(labels[visible],minlength=11)
        primary=2 if golden else int(np.argmax(counts[1:])+1)
        primary_mask=labels==primary
        defs=[f'<path id="face" d="{silhouette}" fill-rule="evenodd"/>', '<clipPath id="silhouette"><use href="#face"/></clipPath>', '<clipPath id="padding"><rect x="8" y="8" width="176" height="176"/></clipPath>', '<filter id="feather" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation=".32"/></filter>']
        paint=[]
        if golden:
            defs.append(gold_defs)
            paint=['<use href="#face" fill="url(#gold)"/>','<use href="#face" fill="url(#edge-color)" mask="url(#sphere-shading)"/>','<use href="#face" fill="url(#top-shine)"/>','<use href="#face" fill="url(#cheek)"/>','<use href="#face" fill="url(#right-cheek)"/>']
        else:
            grad,fill,error=gradient_for('base',primary_mask,rgba,scale)
            defs.append(grad)
            paint.append(f'<use href="#face" fill="{fill}"/>')
        path_count=1;material_errors=[]
        # Reconstruct separate physical surfaces instead of colour-band paths.
        for family in ([2,1,3,4,5,6,7,8,9,10] if definition['category']=='Faces' else [9,10,2,1,3,4,5,6,7,8]):
            if golden and family==primary: continue
            mask=labels==family
            if definition['category'] in {'Food','Objects','Symbols'}:
                mask=cv2.morphologyEx(mask.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)).astype(bool) & visible
            count,components,stats,_=cv2.connectedComponentsWithStats(mask.astype(np.uint8),8)
            for component in range(1,count):
                area=stats[component,cv2.CC_STAT_AREA]*scale**2
                if area<(1.5 if definition['category'] in {'Food','Objects','Symbols'} else .55): continue
                region=components==component
                if slug=='star-eyes' and family in [9,10] and np.mean(np.where(region)[0])*scale<112: continue
                geometry=region
                if definition['category']=='Faces':
                    geometry=cv2.morphologyEx(region.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((3,3),np.uint8)).astype(bool)
                if family in [9,10] and definition['category']!='Faces':
                    filled=binary_fill_holes(region)
                    if np.sum(filled & ~region) <= np.sum(region)*2.5+50/scale**2:
                        geometry=filled
                path=path_for(geometry,scale,fine=slug in ['sacred-stone','fs-forgesworn'])
                if not path: continue
                identifier=f'm{path_count}'
                grad,fill,error=gradient_for(identifier,region,rgba,scale)
                feather_width=.55 if definition['category']=='Faces' else .9
                defs.append(f'<mask id="{identifier}-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="192"><path d="{path}" fill="white" stroke="white" stroke-width="{feather_width}" stroke-linejoin="round" fill-rule="evenodd" filter="url(#feather)"/></mask>')
                bounds=stats[component]
                if definition['category']!='Faces' and max(bounds[cv2.CC_STAT_WIDTH],bounds[cv2.CC_STAT_HEIGHT])*scale>30 and (error>5 or definition['category']=='Hands'):
                    shading,layer=shading_field(identifier,region,geometry,rgba,scale)
                    defs.append(shading);paint.append(layer)
                else:
                    defs.append(grad)
                    paint.append(f'<rect x="0" y="0" width="192" height="192" fill="{fill}" mask="url(#{identifier}-mask)"/>')
                material_errors.append(error)
                path_count+=1
        if slug=='cold-face':
            defs.append('<clipPath id="cold-teeth"><rect x="46" y="106" width="101" height="33" rx="14"/></clipPath>')
            paint.append('<g clip-path="url(#cold-teeth)" fill="none" stroke="#6a829a" stroke-width=".8"><path d="M46 122H147M65 106V139M85 106V139M105 106V139M125 106V139"/></g>')
        if slug=='grin':
            paint.append('<path d="M55 136Q96 147 137 136" fill="none" stroke="#b2aaa0" stroke-width=".6" opacity=".7"/>')
        if slug=='money-face':
            paint.append('<path d="M104 139C99 133 85 135 86 143C86 151 104 147 105 156C106 164 87 166 85 158M96 132V169" fill="none" stroke="#095020" stroke-width="3" stroke-linecap="round"/>')
        if slug in {'star-eyes','thinking'}:
            detail_defs, detail_paint = star_eyes() if slug=='star-eyes' else thinking_hand()
            defs.append(detail_defs); paint.append(detail_paint)
        if slug=='sacred-stone':
            defs=defs[:4]
            detail_defs,detail_paint=stone(rgba,scale,path_for,silhouette)
            defs.append(detail_defs);paint=[detail_paint];path_count=3
        if slug=='jumping-spider':
            defs=defs[:4]
            defs.append(f'<mask id="fur-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="192"><path d="{silhouette}" fill="white" fill-rule="evenodd"/></mask>')
            detail_defs,detail_paint=shading_field('fur',visible,visible,rgba,scale,detail_step=.9)
            defs.append(detail_defs);paint=[detail_paint];path_count=1
        escaped=title.replace('&','&amp;').replace('<','&lt;').replace('"','&quot;')
        svg=f'<svg xmlns="{NS}" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="{escaped}"><defs>'+''.join(defs)+'</defs><g clip-path="url(#padding)"><g clip-path="url(#silhouette)">'+''.join(paint)+'</g></g></svg>\n'
        strategy={'star-eyes':'shared-face-shading-with-native-star-geometry','thinking':'shared-face-shading-with-native-hand-geometry','sacred-stone':'native-stone-shading-procedural-granite-and-fitted-number-paths','jumping-spider':'fitted-silhouette-and-fine-continuous-vector-colour-surface'}.get(slug,'smooth-material-reconstruction-with-continuous-gradients')
    if re.search(r'<image\b|data:image|<script\b',svg): raise ValueError(f'Not genuine vector artwork: {slug}')
    (OUT/f'{slug}.svg').write_text(svg)
    record={'slug':slug,'emoji':art['emoji'],'strategy':strategy,'bytes':len(svg.encode()),'materialPaths':path_count}
    if supports_detailed(slug):record.update(detail_record)
    else:record.update({'source':str(source.relative_to(ROOT)),'sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()})
    records.append(record)
    print(f"{slug}: {len(svg.encode()):,} bytes, {path_count} material paths",flush=True)

if selected:
    old=json.loads((ROOT/'sources/vector-provenance.json').read_text())
    merged={a['slug']:a for a in old['artwork']}
    merged.update({a['slug']:a for a in records})
    records=[merged[a['slug']] for a in pack['artwork']]
if records:
    (ROOT/'sources/vector-provenance.json').write_text(json.dumps({'creator':'TheCryptoDonkey / ForgeSworn','reference':'User-approved happy face reconstruction and original PNG artwork','method':'PNG-fitted contours and continuous measured colour surfaces for reviewed animals, hands, food and objects; detailed spider source and primary community stone photograph; component-authored vegetarian pizza, symbols and selected faces; measured smooth contours and continuous shading elsewhere; preserved original SVG brand masters. No raster embedding or image-generation API.','authoringTools':{'python':platform.python_version(),'Pillow':Image.__version__,'numpy':np.__version__,'opencv':cv2.__version__},'artwork':records},indent=2)+'\n')
print(f'Reconstructed {len(selected) if selected else len(records)} vectors.',flush=True)
