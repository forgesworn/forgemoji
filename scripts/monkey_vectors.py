"""Compact Monkey: editable contours in the original 192-pixel canvas.

Separate ear cups, warm fur, heart-shaped skin, glossy eyes and mouth.
Lighting remains at the upper left for both ears; no reflected paint fields.
"""
import hashlib
import html
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
HEAD = ('M85.8 37.8C89.8 32.3 95.7 25.8 99 28.3C101.8 30.2 100 34.2 98.8 36.1'
        'C102.7 32.6 108.8 30.7 110.7 34.1Q112.1 36.8 109.4 39'
        'C134.7 43 152.3 61.4 155.6 85C158.2 104.1 155.8 129.5 145.8 143.4'
        'C135.1 158.2 114.4 165.3 96 165.2C76.7 165.3 56.9 158.8 46.1 144.9'
        'C36.4 132.3 34.5 109.5 36.1 89.3C37.9 62.5 57.2 40.5 85.8 37.8Z')
FACE = ('M95.9 78.2C85.9 64.9 75.1 62.9 64.9 66.5C52.3 71.1 47.4 87.1 48.2 101.7'
        'Q48.4 107.9 51.5 113.3C46.4 122.5 46.8 133.5 53.7 143.5'
        'C62.2 155.5 78.2 161.9 95.8 161.8C112.4 161.9 129.4 155.3 137.2 143.3'
        'C144.1 133.1 144.8 122 139.5 113.2C143.8 104.8 144.3 94.8 141.4 85.4'
        'C138.3 75.6 132.8 68.3 122.6 65.7C112.3 63 102.7 68.6 95.9 78.2Z')
MOUTH = ('M77.6 120.1C86.5 125 104.6 125.2 113.8 120.1Q116.6 118.5 116.1 123'
         'C114.5 138.6 107.6 149.2 95.8 149.4C84 149.3 77.6 138.3 75.5 123Q74.6 118.5 77.6 120.1Z')

def rebuild(title):
    defs = '''
<radialGradient id="fur" gradientUnits="userSpaceOnUse" cx="92" cy="67" r="70" gradientTransform="translate(0 -13.4) scale(1 1.2)">
<stop stop-color="#db8d43"/><stop offset=".43" stop-color="#b96d27"/><stop offset=".77" stop-color="#995014"/><stop offset=".93" stop-color="#773707"/><stop offset="1" stop-color="#542401"/>
</radialGradient>
<radialGradient id="skin" gradientUnits="userSpaceOnUse" cx="94" cy="94" r="57" gradientTransform="translate(0 -11.28) scale(1 1.12)">
<stop stop-color="#ffd28c"/><stop offset=".48" stop-color="#fac980"/><stop offset=".73" stop-color="#f3bd73"/><stop offset=".9" stop-color="#dfa45b"/><stop offset="1" stop-color="#b67a37"/>
</radialGradient>
<radialGradient id="ear" cx="42%" cy="35%" r="68%" gradientTransform="translate(0 -.09) scale(1 1.2)">
<stop stop-color="#ffda96"/><stop offset=".47" stop-color="#f8c57e"/><stop offset=".75" stop-color="#e4a35c"/><stop offset=".91" stop-color="#bc773a"/><stop offset="1" stop-color="#9c5924"/>
</radialGradient>
<radialGradient id="cup" cx="66%" cy="71%" r="83%">
<stop stop-color="#e2a060"/><stop offset=".55" stop-color="#d08a49"/><stop offset=".8" stop-color="#aa5d26"/><stop offset="1" stop-color="#8e4716"/>
</radialGradient>
<radialGradient id="eye" cx="43%" cy="30%" r="76%">
<stop stop-color="#392310"/><stop offset=".53" stop-color="#170d02"/><stop offset="1" stop-color="#080700"/>
</radialGradient>
<radialGradient id="shine"><stop stop-color="#fffbed"/><stop offset=".35" stop-color="#fff5df" stop-opacity=".9"/><stop offset="1" stop-color="#ffe2b5" stop-opacity="0"/></radialGradient>
<radialGradient id="nose" cx="48%" cy="17%" r="86%"><stop stop-color="#ffd899"/><stop offset=".6" stop-color="#e6a55b"/><stop offset="1" stop-color="#c8873f"/></radialGradient>
<radialGradient id="nostril"><stop stop-color="#351500"/><stop offset=".48" stop-color="#602900"/><stop offset="1" stop-color="#a75b1a" stop-opacity="0"/></radialGradient>
<linearGradient id="mouth" x2="0" y2="1"><stop stop-color="#160500"/><stop offset=".5" stop-color="#370300"/><stop offset="1" stop-color="#660b04"/></linearGradient>
<radialGradient id="tongue" cx="50%" cy="77%" r="78%"><stop stop-color="#f34e3f"/><stop offset=".45" stop-color="#da362d"/><stop offset=".8" stop-color="#a41814"/><stop offset="1" stop-color="#650805"/></radialGradient>
<radialGradient id="chin"><stop stop-color="#ffe0a3" stop-opacity=".25"/><stop offset="1" stop-color="#ffdb9a" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-.2" y="-.2" width="1.4" height="1.4" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".5"/></filter>
<filter id="cup-soft" x="-.2" y="-.2" width="1.4" height="1.4" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.2"/></filter>
'''
    defs += ''.join(f'<filter id="{name}" x="-.1" y="-.1" width="1.2" height="1.2" color-interpolation-filters="sRGB"><feGaussianBlur in="SourceAlpha" stdDeviation="{blur}" result="inset"/><feComposite in="SourceAlpha" in2="inset" operator="out" result="edge"/><feFlood flood-color="{colour}" flood-opacity="{opacity}"/><feComposite in2="edge" operator="in"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode/></feMerge></filter>' for name,blur,colour,opacity in [('fur-depth',2,'#562400',.85),('ear-depth',2,'#9c5924',.85)])
    defs += f'<clipPath id="mouth-clip"><path d="{MOUTH}"/></clipPath>'
    parts=[]
    for side in [False, True]:
        # Geometry is mirrored, but the independently placed ear gradient keeps
        # upper-left illumination in both local coordinate systems.
        outer='M39.3 80.1C25.6 72.9 13.9 80.5 10.7 94.4C6.3 111.8 13.9 125.3 27.1 128.5Q34.9 130.2 41.3 126.9Z'
        cup='M36.8 92.3C27.9 86.7 20.8 91.9 21.1 103.2C21.2 113 27 118.9 36.8 117.2Z'
        if side:
            # Mirror coordinates only rather than the lighting/filter group.
            import re
            def mirror(path):
                tokens=re.findall(r'[A-Za-z]|-?\d+(?:\.\d+)?',path); axis=0;out=[]
                for token in tokens:
                    if token.isalpha():out.append(token);axis=0
                    else:
                        val=float(token);out.append(f'{192-val:g}' if axis%2==0 else token);axis+=1
                return ' '.join(out)
            outer,cup=mirror(outer),mirror(cup)
        parts += [f'<path d="{outer}" fill="url(#ear)" filter="url(#ear-depth)"/>',f'<path d="{cup}" fill="url(#cup)" filter="url(#cup-soft)"/>']
    parts += [f'<path d="{HEAD}" fill="url(#fur)" filter="url(#fur-depth)" stroke="#874410" stroke-width=".65"/>',
              f'<path d="{FACE}" fill="url(#skin)" filter="url(#soft)"/>',
              '<ellipse cx="94" cy="150" rx="30" ry="9" fill="url(#chin)"/>']
    for x in [70.8,120.4]:
        parts += [f'<ellipse cx="{x}" cy="97.2" rx="8.1" ry="11.4" fill="url(#eye)" stroke="#8d6028" stroke-width=".5"/>',
                  f'<ellipse cx="{x-1.2}" cy="91.4" rx="3.1" ry="3.8" fill="url(#shine)"/>']
    parts += ['<path d="M87.6 109.2C88.4 102.9 102.6 102.7 104 109Q103.5 112.6 96 116Q88.9 112.8 87.6 109.2Z" fill="url(#nose)" filter="url(#soft)"/>',
              '<ellipse cx="90.6" cy="109.7" rx="3.3" ry="3.5" transform="rotate(-35 90.6 109.7)" fill="url(#nostril)"/>',
              '<ellipse cx="101" cy="109.5" rx="3.2" ry="3.6" transform="rotate(35 101 109.5)" fill="url(#nostril)"/>',
              f'<path d="{MOUTH}" fill="url(#mouth)" stroke="#a66a26" stroke-width=".7"/>',
              '<g clip-path="url(#mouth-clip)"><ellipse cx="95.8" cy="142.8" rx="14.4" ry="9.6" fill="url(#tongue)" filter="url(#soft)"/></g>']
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="'+html.escape(title,quote=True)+'"><defs>'+defs+'</defs>'+''.join(parts)+'</svg>\n')
    return svg, {'source':'png/monkey.png','sourceSha256':hashlib.sha256((ROOT/'png/monkey.png').read_bytes()).hexdigest(),'strategy':'component-authored-reference-fitted-monkey-with-compact-material-gradients'}

if __name__ == '__main__':
    import sys
    Path(sys.argv[1]).write_text(rebuild('Monkey')[0])
