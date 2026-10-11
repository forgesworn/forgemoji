"""Native vector details whose meaning is lost by colour segmentation."""
import math
import random
import numpy as np
import cv2


def star_eyes():
    def star(cx):
        points = [(cx + (42 if i % 2 == 0 else 21.5) * math.sin(i * math.pi / 5),
                   77 - (42 if i % 2 == 0 else 21.5) * math.cos(i * math.pi / 5)) for i in range(10)]
        d = ''
        for i, point in enumerate(points):
            previous, following = points[(i-1) % 10], points[(i+1) % 10]
            before = [point[j] * .91 + previous[j] * .09 for j in range(2)]
            after = [point[j] * .91 + following[j] * .09 for j in range(2)]
            d += ('M' if i == 0 else 'L') + ' '.join(f'{x:.3f}' for x in before)
            d += 'Q' + ' '.join(f'{x:.3f}' for x in [*point, *after])
        return d + 'Z'
    defs = '<linearGradient id="stars-gold" x1="0" y1="37" x2="0" y2="115" gradientUnits="userSpaceOnUse"><stop stop-color="#fffbd0"/><stop offset=".34" stop-color="#fff47a"/><stop offset=".68" stop-color="#ffd72b"/><stop offset="1" stop-color="#e69100"/></linearGradient><filter id="stars-shadow" x="-20%" y="-20%" width="140%" height="145%"><feGaussianBlur in="SourceAlpha" stdDeviation="1.3" result="height"/><feSpecularLighting in="height" surfaceScale="3" specularConstant=".55" specularExponent="18" lighting-color="#fff7c0" result="light"><feDistantLight azimuth="225" elevation="48"/></feSpecularLighting><feComposite in="light" in2="SourceAlpha" operator="in" result="rim"/><feComposite in="SourceGraphic" in2="rim" operator="arithmetic" k2="1" k3=".6" result="bevel"/><feDropShadow in="bevel" dx="0" dy="1.2" stdDeviation="1.1" flood-color="#8b4200" flood-opacity=".55"/></filter>'
    paint = '<g fill="url(#stars-gold)" stroke="#bc7504" stroke-width="1" filter="url(#stars-shadow)">' + ''.join(f'<path d="{star(cx)}"/>' for cx in [54, 140]) + '</g>'
    return defs, paint


def thinking_hand():
    defs = '<linearGradient id="thinking-hand-gold" x1="34" y1="133" x2="94" y2="169" gradientUnits="userSpaceOnUse"><stop stop-color="#ffdc45"/><stop offset=".35" stop-color="#ffd128"/><stop offset=".8" stop-color="#f1ae12"/><stop offset="1" stop-color="#d58707"/></linearGradient><radialGradient id="thinking-hand-shine" cx=".3" cy=".25" r=".6"><stop stop-color="#fffab8" stop-opacity=".65"/><stop offset="1" stop-color="#ffed78" stop-opacity="0"/></radialGradient><filter id="thinking-hand-shadow" x="-20%" y="-20%" width="140%" height="145%"><feDropShadow dx=".5" dy=".5" stdDeviation=".8" flood-color="#a46200" flood-opacity=".5"/></filter>'
    shape = 'M34 176C28 173 28 163 28 153C28 144 32 136 37 129L38 118C38 107 50 106 52 117L52 130C58 135 61 132 66 131L96 124C106 122 109 130 103 136C100 139 91 141 83 144C94 144 94 151 84 154C93 156 91 164 80 167C88 171 82 179 72 180L44 180C40 180 36 178 34 176Z'
    paint = f'<g filter="url(#thinking-hand-shadow)"><path d="{shape}" fill="url(#thinking-hand-gold)" stroke="#c68809" stroke-width=".7"/><path d="{shape}" fill="url(#thinking-hand-shine)"/><g fill="none" stroke="#c17c09" stroke-width=".8" stroke-linecap="round" opacity=".58"><path d="M83 144Q74 146 70 147M84 154Q77 155 73 155M80 167Q75 167 72 166"/></g><path d="M43 117Q43 112 47 114M65 134Q79 130 94 129" fill="none" stroke="#fff09a" stroke-width="1.5" stroke-linecap="round" opacity=".65"/></g>'
    return defs, paint


def stone(rgba, scale, path_for, silhouette):
    # Extract the twelve engraved glyphs, closing the photographic flecks.
    gray = cv2.cvtColor(rgba[:,:,:3], cv2.COLOR_RGB2GRAY)
    yy, xx = np.indices(gray.shape)
    ink = (gray < 94) & (xx*scale > 55) & (xx*scale < 139) & (yy*scale > 35) & (yy*scale < 159)
    ink = cv2.morphologyEx(ink.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((3,3),np.uint8))
    ink = cv2.medianBlur(ink, 3)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(ink, 8)
    glyphs = np.zeros(ink.shape, dtype=bool)
    candidates=sorted(range(1,count),key=lambda i:stats[i,cv2.CC_STAT_AREA],reverse=True)[:12]
    assert len(candidates)==12, 'The stone must retain all twelve digits'
    for i in candidates:
        glyphs |= labels==i
    numbers = path_for(glyphs,scale)
    defs = '<radialGradient id="stone-light" cx=".36" cy=".26" r=".78"><stop stop-color="#e4dfd3"/><stop offset=".42" stop-color="#c6c1b6"/><stop offset=".75" stop-color="#97978b"/><stop offset="1" stop-color="#55594e"/></radialGradient><radialGradient id="stone-edge" cx=".48" cy=".44" r=".65"><stop offset=".55" stop-color="#44423c" stop-opacity="0"/><stop offset="1" stop-color="#30332d" stop-opacity=".48"/></radialGradient><filter id="granite" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="3" seed="600" result="grain"/><feColorMatrix in="grain" type="saturate" values="0"/><feComponentTransfer><feFuncA type="linear" slope=".32"/></feComponentTransfer><feBlend in="SourceGraphic" mode="soft-light"/></filter><filter id="engraving" x="-5%" y="-5%" width="110%" height="110%"><feDropShadow dx=".15" dy=".45" stdDeviation=".28" flood-color="#eeebe1" flood-opacity=".8"/></filter><linearGradient id="ink" x1="0" y1="0" x2=".7" y2="1"><stop stop-color="#25241f"/><stop offset="1" stop-color="#373831"/></linearGradient>'
    rng=random.Random(600)
    flecks=[]
    for i in range(1650):
        x,y=rng.uniform(25,165),rng.uniform(8,184)
        rx,ry=rng.uniform(.12,.58),rng.uniform(.1,.5)
        ink=rng.choice(['#f7f1df','#fffefa','#746b5b','#8f897a','#494941','#d2c6aa'])
        flecks.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{rx:.2f}" ry="{ry:.2f}" fill="{ink}" opacity="{rng.uniform(.2,.7):.2f}"/>')
    grain=''.join(flecks)
    paint = f'<path d="{silhouette}" fill="url(#stone-light)" filter="url(#granite)" fill-rule="evenodd"/><path d="{silhouette}" fill="url(#stone-edge)" fill-rule="evenodd"/>{grain}<path d="{numbers}" fill="url(#ink)" fill-rule="evenodd" filter="url(#engraving)"/>'
    return defs,paint
