"""Reference-fitted contours and continuous SVG colour surfaces.

A contour is measured at source resolution and fitted to cubic curves. Shading
is a bounded set of horizontal colour ramps, interpolated vertically with an
alpha mask. Detailed photographs use merged vector colour regions instead.
Both representations contain ordinary SVG paths/gradients/filters, never an
embedded bitmap. Source detail remains finite; these are fitted reconstructions.
"""
from pathlib import Path
import hashlib
import html
import math
import numpy as np
import cv2
from PIL import Image
from scipy.interpolate import splprep, splev
from scipy.ndimage import distance_transform_edt, gaussian_filter

ROOT = Path(__file__).resolve().parent.parent
NATURE = {'tiger','lion','cow','chicken','monkey','duck','whale','octopus','turtle','bee','rose','star'}
FOOD = {'banana','apple','strawberry','watermelon','lemon','avocado','burger','fries','popcorn','cake','doughnut','cookie','cheers','coffee','ice-cream','pizza'}
OBJECTS = {'key','camera','rocket','gamepad','football','trophy'}
HANDS = {'thumbs-up','thumbs-down','wave','clap','thanks','peace'}
PHOTO = {'sacred-stone','jumping-spider'}
SLUGS = NATURE | FOOD | OBJECTS | PHOTO
STONE_URL = 'https://600.wtf/img/sacred-stone.webp'
# Pin the consulted community photograph, without adding it to the package.
STONE_SHA256 = '317add9f9e026abc66ffd42474956e8b14d109e930f879bf62522240f5276b06'


def supports(slug):
    return slug in SLUGS or slug.split('-tone')[0] in HANDS


def number(x):
    return f'{x:.2f}'.rstrip('0').rstrip('.')


def colour(rgb):
    return '#'+''.join(f'{int(c):02x}' for c in np.clip(np.round(rgb),0,255))


def contour(mask, scale, smooth=.055, minimum=.08):
    curves,_ = cv2.findContours(mask.astype('uint8'),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
    paths=[]
    for c in curves:
        if len(c)<3 or abs(cv2.contourArea(c))*scale**2<minimum: continue
        points=(c[:,0,:].astype(float)+.5)*scale
        if len(c)<7:
            paths.append('M'+'L'.join(f'{number(x)} {number(y)}' for x,y in points)+'Z');continue
        try:
            tck,_=splprep(np.vstack([points,points[0]]).T,s=len(points)*smooth*scale**2,per=True)
            knots=np.unique(np.clip(tck[0],0,1));p=np.array(splev(0,tck));d=f'M{number(p[0])} {number(p[1])}'
            for a,b in zip(knots[:-1],knots[1:]):
                p0,p3=np.array(splev(a,tck)),np.array(splev(b,tck))
                p1=p0+np.array(splev(a,tck,der=1))*(b-a)/3
                p2=p3-np.array(splev(b,tck,der=1))*(b-a)/3
                d+='C'+' '.join(number(v) for v in np.r_[p1,p2,p3])
            paths.append(d+'Z')
        except ValueError:
            points=cv2.approxPolyDP(c,.25/scale,True)[:,0,:]*scale+.5*scale
            paths.append('M'+'L'.join(f'{number(x)} {number(y)}' for x,y in points)+'Z')
    return ''.join(paths)


def stop_indices(row, tolerance):
    selected={0,len(row)-1};pending=[(0,len(row)-1)]
    while pending:
        a,b=pending.pop()
        if b<=a+1:continue
        t=np.linspace(0,1,b-a+1)[:,None]
        error=np.max(abs(row[a:b+1]-row[a]*(1-t)-row[b]*t),axis=1)
        k=int(np.argmax(error))
        if error[k]>tolerance:
            selected.add(a+k);pending.extend([(a,a+k),(a+k,b)])
    return sorted(selected)


def colour_field(image):
    rgba=np.array(image);alpha=rgba[:,:,3]
    _,nearest=distance_transform_edt(alpha<180,return_indices=True)
    rgb=rgba[:,:,:3].astype(float)
    rgb[alpha<180]=rgb[nearest[0][alpha<180],nearest[1][alpha<180]]
    return rgb,alpha


def ramps(image, resolution=144):
    image=image.resize((resolution,resolution),Image.Resampling.LANCZOS)
    rgb,alpha=colour_field(image);rgb=gaussian_filter(rgb,(.28,.28,0))
    ys,xs=np.where(alpha>=32);x0=max(0,int(xs.min())-2);x1=min(resolution,int(xs.max())+3)
    y0=max(0,int(ys.min())-2);y1=min(resolution-1,int(ys.max())+2)
    scale=192/resolution;defs=[];paint=[]
    for y in range(y0,y1+1):
        line=rgb[y,x0:x1];key=f'r{y}'
        # Off-outline samples never paint a visible pixel. Interpolate through
        # those gaps instead of storing nearest-neighbour shading there.
        valid=np.flatnonzero(alpha[y,x0:x1]>=64)
        if len(valid):
            line=np.stack([np.interp(np.arange(len(line)),valid,line[valid,c]) for c in range(3)],axis=1)
        else:line=np.broadcast_to(line.mean(axis=0),line.shape)
        nodes=stop_indices(line,6)
        defs.append(f'<linearGradient id="{key}" gradientUnits="userSpaceOnUse" x1="{number(x0+.5)}" y1="0" x2="{number(x1-.5)}" y2="0">'+''.join(f'<stop offset="{number(i/(len(line)-1)*100)}%" stop-color="{colour(line[i])}"/>' for i in nodes)+'</linearGradient>')
    defs.append('<linearGradient id="fade" x2="0" y2="1"><stop stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff"/></linearGradient><mask id="lerp" maskContentUnits="objectBoundingBox"><path d="M0 0H1V1H0Z" fill="url(#fade)"/></mask>')
    for y in range(y0,y1):
        d=f'M{x0} {y}H{x1}v1H{x0}Z'
        paint.append(f'<path d="{d}" fill="url(#r{y})"/><path d="{d}" fill="url(#r{y+1})" mask="url(#lerp)"/>')
    # Integer colour bands share boundaries. Crisp edges prevent transparent
    # renderer seams; the vertical mask blends neighbouring continuous ramps.
    return ''.join(defs),f'<g transform="scale({scale:.6f})" shape-rendering="crispEdges">'+''.join(paint)+'</g>'


def photograph(image, quantum=8):
    rgb,alpha=colour_field(image);size=alpha.shape[0]
    rgb=gaussian_filter(rgb,(.18,.18,0))
    quant=np.clip(np.round(rgb/quantum)*quantum,0,255).astype('uint32')
    labels=(quant[:,:,0]<<16)+(quant[:,:,1]<<8)+quant[:,:,2]
    visible=cv2.dilate((alpha>=32).astype('uint8'),np.ones((5,5),'uint8')).astype(bool)
    # Merge equal-colour horizontal runs vertically. This preserves texture,
    # while removing repeated coordinates and per-pixel SVG elements.
    rows={}
    for y in range(size):
        line=labels[y];change=np.where(np.diff(line)!=0)[0]+1;edges=np.r_[0,change,size]
        for x,end in zip(edges[:-1],edges[1:]):
            if np.any(visible[y,x:end]):rows.setdefault(int(line[x]),{}).setdefault(y,[]).append((int(x),int(end-x)))
    parts=[]
    for value,lines in sorted(rows.items()):
        active={};rects=[]
        for y in range(min(lines),max(lines)+2):
            current=set(lines.get(y,[]));new={}
            for key in sorted(current):new[key]=(active[key][0],active[key][1]+1) if key in active else (y,1)
            rects.extend((*key,*val) for key,val in active.items() if key not in current);active=new
        d=''.join(f'M{x} {y}h{w}v{h}h-{w}Z' for x,w,y,h in rects)
        parts.append(f'<path fill="#{value:06x}" d="{d}"/>')
    scale=192/size
    defs='<filter id="colour-soften" x="0" y="0" width="192" height="192" filterUnits="userSpaceOnUse" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".16"/></filter>'
    return defs,f'<g filter="url(#colour-soften)"><g transform="scale({scale:.6f})" shape-rendering="crispEdges">'+''.join(parts)+'</g></g>'


def photo_source(slug):
    if slug=='jumping-spider':
        source=ROOT/'sources/jumping-spider.png'
        original=Image.open(source).convert('RGBA')
        metadata={'source':'sources/jumping-spider.png','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
        size=352
    else:
        import urllib.request
        cache=Path('/private/tmp/forgemoji-sacred-stone-reference.webp')
        if not cache.exists():cache.write_bytes(urllib.request.urlopen(STONE_URL,timeout=30).read())
        digest=hashlib.sha256(cache.read_bytes()).hexdigest()
        if STONE_SHA256 and digest!=STONE_SHA256:raise ValueError('The stone reference changed; inspect it before rebuilding')
        original=Image.open(cache).convert('RGBA')
        metadata={'source':STONE_URL,'sourceSha256':digest,'referenceRedistributed':False}
        size=224
    alpha=np.array(original)[:,:,3];ys,xs=np.where(alpha>=32)
    original=original.crop((int(xs.min()),int(ys.min()),int(xs.max())+1,int(ys.max())+1))
    original.thumbnail((int(size*176/192),int(size*176/192)),Image.Resampling.LANCZOS)
    image=Image.new('RGBA',(size,size));image.paste(original,((size-original.width)//2,(size-original.height)//2))
    return image,metadata


def rebuild(slug,title):
    if slug == 'monkey':
        from monkey_vectors import rebuild as rebuild_monkey
        return rebuild_monkey(title)
    if slug == 'tiger':
        from tiger_vectors import rebuild as rebuild_tiger
        return rebuild_tiger(title)
    if slug == 'lion':
        from lion_vectors import rebuild as rebuild_lion
        return rebuild_lion(title)
    if slug == 'sacred-stone':
        from stone_vectors import rebuild as rebuild_stone
        return rebuild_stone(title)
    photo=slug in PHOTO
    if photo:image,metadata=photo_source(slug)
    else:
        source=ROOT/'png'/f'{slug}.png';image=Image.open(source).convert('RGBA')
        metadata={'source':f'png/{slug}.png','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    rgba=np.array(image);scale=192/image.width
    # Keep low-opacity fur and fine detached shapes, as well as the main body.
    defs=['<clipPath id="padding"><rect x="8" y="8" width="176" height="176"/></clipPath>']
    mask=[];previous=0
    levels=[(32,.25),(128,.7),(230,1)] if photo else [(64,.35),(170,1)]
    for threshold,level in levels:
        path=contour(rgba[:,:,3]>=threshold,scale,smooth=.025 if photo else .06)
        if path:
            opacity=(level-previous)/(1-previous)
            mask.append(f'<path d="{path}" fill="#fff" opacity="{number(opacity)}" fill-rule="evenodd"/>')
        previous=level
    defs.append('<mask id="outline" maskUnits="userSpaceOnUse" x="0" y="0" width="192" height="192" style="mask-type:alpha">'+''.join(mask)+'</mask>')
    resolution=128 if slug in {'tiger','lion','rose','strawberry','popcorn','cake','cookie','lemon','ice-cream','pizza'} else 96
    shading,paint=photograph(image) if photo else ramps(image,resolution)
    if slug=='pizza':
        from owner_details import vegetarian_overlay
        vegetable_defs,vegetables=vegetarian_overlay()
        shading+=vegetable_defs
        paint+=vegetables
    if slug=='trophy':
        from owner_details import trophy_engraving
        paint+=trophy_engraving()
    defs.append(shading)
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="'+html.escape(title,quote=True)+'"><defs>'+''.join(defs)+'</defs><g clip-path="url(#padding)"><g mask="url(#outline)">'+paint+'</g></g></svg>\n'
    metadata['strategy']='photo-reference-fitted-contours-and-merged-native-vector-colour-regions' if photo else 'png-reference-fitted-cubic-contours-and-continuous-native-vector-colour-ramps'
    if slug=='pizza':metadata['strategy']='fitted-baked-pizza-crust-and-cheese-with-native-tomato-mushroom-pepper-onion-and-olive-toppings'
    metadata['colourResolution']=image.width if photo else resolution
    return svg,metadata
