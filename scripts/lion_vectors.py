"""Compact lion built from reference-measured locks and facial components.

The mane has separate curved locks, with continuous material gradients;
the cream muzzle is a softly blended triangle, not a circular face patch.
All coordinates refer to the original 192-pixel PNG, which is unchanged.
"""
import hashlib
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MANE = ('M96 26C103 19 112 15 120 15Q127 14 122 23'
        'C133 21 143 22 148 27Q154 31 146 35'
        'C158 37 168 45 172 57Q174 62 166 60'
        'C176 70 182 84 182 101Q182 107 177 103L174 100'
        'C179 115 176 131 169 140Q166 145 163 137'
        'C161 150 153 162 141 167Q135 171 135 164'
        'C127 173 118 179 109 178L109 175Q105 179 99 178'
        'L86 178Q84 178 83 174L82 178C71 179 63 172 56 165'
        'Q57 171 51 168C38 164 30 151 28 137Q25 144 22 139'
        'C14 128 13 114 17 101Q10 108 10 102'
        'C10 84 16 69 27 59Q20 61 23 55C29 43 40 37 48 35'
        'Q39 32 44 28C54 22 63 22 74 24Q67 14 74 15'
        'C83 16 90 20 96 26Z')

# Locks extend behind the head. Their visible ends and overlapping ridges
# are independent components, rather than hundreds of traced colour areas.
LOCKS = [
    ('bottom', 'M55 132C70 130 82 139 96 153C99 163 101 173 109 178'
     'C106 180 96 178 86 178Q84 178 83 174L82 178C70 179 58 170 52 158Z',
     (79, 152, 28, 38, -24)),
    ('bottom-right', 'M90 153C103 139 119 134 137 133L138 155'
     'C133 170 121 179 109 178Q109 175 111 171C100 178 96 167 90 153Z',
     (115, 150, 27, 38, 28)),
    ('low-left', 'M50 97C41 103 30 116 29 134C29 149 37 163 51 168'
     'Q57 171 55 164C55 149 64 143 76 140Z',
     (43, 129, 19, 43, -25)),
    ('low-right', 'M141 99C151 110 162 122 163 136C161 151 153 163 140 168'
     'Q134 171 135 164C135 150 126 143 114 139Z',
     (148, 128, 19, 43, 25)),
    ('side-left', 'M42 76C25 84 17 99 16 113C13 124 18 136 22 140'
     'Q25 144 28 137C34 123 41 113 53 107Z',
     (28, 107, 17, 38, 14)),
    ('side-right', 'M150 77C167 86 177 99 177 114C178 127 173 137 169 141'
     'Q166 145 163 137C156 123 150 114 139 106Z',
     (164, 107, 17, 38, -14)),
    ('upper-left', 'M56 52C36 49 23 61 17 76C12 87 10 94 10 102'
     'Q10 108 16 102C27 92 32 93 46 88L63 66Z',
     (27, 78, 17, 38, 35)),
    ('upper-right', 'M136 52C156 50 170 64 177 80C182 91 182 99 182 103'
     'Q181 107 177 103C165 93 159 92 146 88L129 67Z',
     (165, 79, 17, 38, -35)),
    ('brow-left', 'M79 53C65 36 48 31 37 40C30 45 25 50 23 56'
     'Q21 61 28 59C43 57 51 60 64 71Z',
     (48, 45, 30, 16, -27)),
    ('brow-right', 'M114 53C126 36 145 32 156 40C164 46 169 51 172 57'
     'Q174 62 166 60C151 58 142 61 130 70Z',
     (145, 46, 30, 16, 27)),
    ('crown-left', 'M95 54C92 39 78 24 61 24C54 23 45 25 43 29'
     'Q41 32 48 35C64 39 70 51 76 58Z',
     (67, 35, 30, 14, 27)),
    ('crown-right', 'M97 55C101 40 116 24 132 24C140 23 148 26 150 29'
     'Q152 32 145 36C129 40 122 51 117 58Z',
     (126, 35, 30, 14, -27)),
    ('forelock-left', 'M96 53C97 36 87 22 75 17Q66 13 72 23'
     'C76 32 81 45 87 55Z',
     (86, 34, 11, 26, -33)),
    ('forelock-right', 'M91 53C94 34 107 19 119 16Q127 13 123 21'
     'C119 31 112 47 105 56Z',
     (106, 33, 12, 27, 39)),
]

HEAD = ('M96 50C86 48 77 50 68 53C58 58 50 67 45 80'
        'C40 91 38 105 40 116C42 132 54 143 72 150'
        'C81 153.5 89 155.8 96 155.8C105 154 115 151.5 125 147'
        'C143 138 151 130 152 116C155 102 151 88 146 77'
        'C139 64 131 57 122 53C113 50 103 48 96 50Z')
CREAM = ('M96 89C90 89 85 98 78 106C73 112 63 117 59 123'
         'C54 131 59 140 71 147C80 152 88 154.8 96 155.6'
         'C106 154 116 150 126 144C136 138 139 132 134 125'
         'C130 119 119 113 113 106C107 99 102 89 96 89Z')
EAR = ('M75 55C72 46 64 40 57 41C43 40 35 52 37 65'
       'C38 73 42 78 49 80L76 62Z')
EAR_INNER = ('M66 56C62 51 57 51 53 53C46 57 46 68 52 72'
             'C57 68 61 62 66 58Z')
MOUTH = ('M74 120C77 124 83 126 89 124Q94 123 96 120'
         'Q99 125 105 125C110 125 114 123 117 119'
         'C114 133 110 142 102 145C96 148 89 145 85 140'
         'C79 134 77 128 74 120Z')
LIPS = ('M74 120C77 124 83 126 89 124Q94 123 96 120'
        'Q99 125 105 125C110 125 114 123 117 119')
NOSE = ('M85 106C88 104 104 104 106 107C110 112 102 116 97 118'
        'Q95 119 93 117C88 114 82 110 85 106Z')

# Low-dimensional fits of opaque interior PNG pixels. Hidden gradient stops
# retain the same material palette instead of unconstrained extrapolation.
MATERIALS = {'bottom': ((70.276, 140.0, 25.62, 52.694, -42.0),
            [(0.0, '#a44a0c'),
             (0.3, '#a04a0b'),
             (0.6, '#943e05'),
             (0.82, '#8b3705'),
             (1.0, '#6e2300')]),
 'bottom-right': ((117.047, 138.0, 29.646, 56.417, 46.0),
                  [(0.0, '#a44a0c'),
                   (0.3, '#a04a0b'),
                   (0.6, '#8d3803'),
                   (0.82, '#8f3903'),
                   (1.0, '#742800')]),
 'low-left': ((40.895, 129.042, 13.41, 37.84, -18.434),
              [(0.0, '#853201'),
               (0.3, '#97400a'),
               (0.6, '#923c06'),
               (0.82, '#843102'),
               (1.0, '#712501')]),
 'low-right': ((151.262, 130.913, 11.99, 38.341, 21.838),
               [(0.0, '#8c3600'),
                (0.3, '#964007'),
                (0.6, '#8f3a04'),
                (0.82, '#812e00'),
                (1.0, '#6e2401')]),
 'side-left': ((28.141, 100.067, 12.824, 36.625, 5.709),
               [(0.0, '#a94d15'),
                (0.3, '#a14811'),
                (0.6, '#943d06'),
                (0.82, '#853201'),
                (1.0, '#6d2300')]),
 'side-right': ((161.912, 104.217, 11.321, 33.111, -5.96),
                [(0.0, '#9c4208'),
                 (0.3, '#9d4209'),
                 (0.6, '#903904'),
                 (0.82, '#843001'),
                 (1.0, '#712501')]),
 'upper-left': ((27.443, 75.884, 20.779, 35.202, 18.601),
                [(0.0, '#ac531b'),
                 (0.3, '#9a420a'),
                 (0.6, '#8d3702'),
                 (0.82, '#7f2d03'),
                 (1.0, '#692300')]),
 'upper-right': ((164.161, 77.853, 20.722, 29.012, -17.0),
                 [(0.0, '#a24a0f'),
                  (0.3, '#963e06'),
                  (0.6, '#8a3401'),
                  (0.82, '#802d00'),
                  (1.0, '#682000')]),
 'brow-left': ((41.825, 44.435, 26.338, 9.6, -27.486),
               [(0.0, '#af5414'),
                (0.3, '#9e460b'),
                (0.6, '#8c3801'),
                (0.82, '#762800'),
                (1.0, '#873900')]),
 'brow-right': ((145.438, 40.209, 31.504, 9.6, 37.674),
                [(0.0, '#a4470b'),
                 (0.3, '#9e4308'),
                 (0.6, '#923c06'),
                 (0.82, '#812f01'),
                 (1.0, '#5f1b04')]),
 'crown-left': ((70.658, 33.353, 43.503, 11.961, 21.477),
                [(0.0, '#be6326'),
                 (0.3, '#ad5216'),
                 (0.6, '#9d4307'),
                 (0.82, '#863502'),
                 (1.0, '#7e3000')]),
 'crown-right': ((123.566, 32.321, 44.358, 13.658, -24.135),
                 [(0.0, '#bd6127'),
                  (0.3, '#a94e11'),
                  (0.6, '#953d03'),
                  (0.82, '#7a2b00'),
                  (1.0, '#6a2500')]),
 'forelock-left': ((88.41, 22.352, 18.7, 33.045, -24.274),
                   [(0.0, '#a55329'),
                    (0.3, '#bb5e22'),
                    (0.6, '#9d4106'),
                    (0.82, '#8b3603'),
                    (1.0, '#7c2a00')]),
 'forelock-right': ((105.66, 24.554, 16.259, 45.9, 36.989),
                    [(0.0, '#bc6732'),
                     (0.3, '#af561a'),
                     (0.6, '#953c00'),
                     (0.82, '#933b05'),
                     (1.0, '#8e3902')]),
 'gold': ((93.021, 90.0, 61.219, 70.938, -12.154),
          [(0.0, '#fdc22b'), (0.35, '#feca32'), (0.6, '#fcb218'), (0.8, '#f2a210'), (1.0, '#c06400')]),
 'cream': ((95.724, 111.193, 57.321, 53.075, -18.0),
           [(0.0, '#fdf5c0'), (0.35, '#fadb9c'), (0.6, '#f5d291'), (0.8, '#ce9345'), (1.0, '#b67c2b')])}


def radial(identifier, geometry, stops):
    """A centred elliptical field, rotated about the material's highlight."""
    x, y, rx, ry, angle = geometry
    transform = f'rotate({angle} {x} {y}) translate(0 {y * (1-ry/rx):.4f}) scale(1 {ry/rx:.5f})'
    return (f'<radialGradient id="{identifier}" gradientUnits="userSpaceOnUse" '
            f'cx="{x}" cy="{y}" r="{rx}" gradientTransform="{transform}">'
            + ''.join(f'<stop offset="{offset}" stop-color="{colour}"/>' for offset, colour in stops)
            + '</radialGradient>')


def rebuild(title):
    defs = [radial('mane', (94, 83, 99, 114, 0),
                   [(0, '#a74d08'), (.45, '#9e4405'), (.78, '#883702'), (1, '#652300')])]
    for name, _, _ in LOCKS:
        defs.append(radial(name, *MATERIALS[name]))
    defs.extend([
        radial('gold', *MATERIALS['gold']),
        radial('cream', *MATERIALS['cream']),
        '<radialGradient id="forehead-light"><stop stop-color="#fff2a0" stop-opacity=".16"/><stop offset=".6" stop-color="#fff2a0" stop-opacity=".07"/><stop offset="1" stop-color="#fff2a0" stop-opacity="0"/></radialGradient>',
        '<radialGradient id="mane-light"><stop stop-color="#d47825" stop-opacity=".13"/><stop offset="1" stop-color="#d47825" stop-opacity="0"/></radialGradient>',
        '''<radialGradient id="ear" cx=".49" cy=".55" r=".55"><stop stop-color="#b25400"/><stop offset=".35" stop-color="#b86200"/><stop offset=".52" stop-color="#f6ab15"/><stop offset=".68" stop-color="#ffd24b"/><stop offset=".82" stop-color="#f7b01a"/><stop offset="1" stop-color="#985100"/></radialGradient>
<radialGradient id="ear-inner" cx=".56" cy=".94" r=".95"><stop stop-color="#c1701e"/><stop offset=".5" stop-color="#b35911"/><stop offset=".85" stop-color="#8e3000"/><stop offset="1" stop-color="#742501"/></radialGradient>
<radialGradient id="eye" cx=".48" cy=".3" r=".75"><stop stop-color="#3d281c"/><stop offset=".34" stop-color="#261103"/><stop offset=".62" stop-color="#160800"/><stop offset="1" stop-color="#0a0400"/></radialGradient>
<radialGradient id="eye-shine"><stop stop-color="#fffef5"/><stop offset=".3" stop-color="#ffeecd" stop-opacity=".85"/><stop offset="1" stop-color="#fff1d5" stop-opacity="0"/></radialGradient>
<radialGradient id="nose" cx=".48" cy=".15" r=".94"><stop stop-color="#61462b"/><stop offset=".32" stop-color="#2c1707"/><stop offset="1" stop-color="#0c0601"/></radialGradient>
<radialGradient id="nose-shine"><stop stop-color="#dbcdb2" stop-opacity=".74"/><stop offset=".55" stop-color="#b9a48a" stop-opacity=".35"/><stop offset="1" stop-color="#a99270" stop-opacity="0"/></radialGradient>
<linearGradient id="mouth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#160100"/><stop offset=".65" stop-color="#4b0100"/><stop offset="1" stop-color="#820805"/></linearGradient>
<radialGradient id="tongue" cx=".53" cy=".75" r=".75"><stop stop-color="#ff6866"/><stop offset=".48" stop-color="#eb4a48"/><stop offset=".78" stop-color="#be191d"/><stop offset="1" stop-color="#760204"/></radialGradient>
<filter id="edge-soft" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".35"/></filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".65"/></filter>
<filter id="crease-soft" x="-30%" y="-10%" width="160%" height="120%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.1"/></filter>
<filter id="cream-soft" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.8"/></filter>
<filter id="mane-depth" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.7"/></filter>
<filter id="face-depth" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB"><feGaussianBlur in="SourceAlpha" stdDeviation="1.6" result="inset"/><feComposite in="SourceAlpha" in2="inset" operator="out" result="edge"/><feFlood flood-color="#784001" flood-opacity=".8"/><feComposite in2="edge" operator="in"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode/></feMerge></filter>
<filter id="face-shadow" x="-12%" y="-12%" width="124%" height="124%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.8"/></filter>''',
        f'<clipPath id="mane-clip"><path d="{MANE}"/></clipPath>',
        f'<clipPath id="head-clip"><path d="{HEAD}"/></clipPath>',
        f'<clipPath id="mouth-clip"><path d="{MOUTH}"/></clipPath>',
        f'<g id="left-ear"><path d="{EAR}" fill="url(#ear)" filter="url(#face-depth)"/><path d="{EAR_INNER}" fill="url(#ear-inner)" filter="url(#soft)"/></g>',
        '<clipPath id="padding"><path d="M8 8H184V184H8Z"/></clipPath>',
    ])
    parts = ['<g filter="url(#edge-soft)">', f'<path d="{MANE}" fill="url(#mane)" filter="url(#edge-soft)"/>',
             '<g clip-path="url(#mane-clip)">']
    parts.extend(f'<path d="{path}" fill="url(#{name})" filter="url(#mane-depth)"/>' for name, path, _ in LOCKS)
    parts.extend([
        '<ellipse cx="96" cy="165" rx="25" ry="14" fill="url(#mane-light)"/>',
        '<path d="M51 150C52 158 54 163 55 168Q50 163 49 158ZM77 156C78 165 82 171 83 178Q78 175 74 164ZM116 156C113 165 111 171 109 178Q108 173 112 164ZM140 150C139 158 136 163 135 168Q140 163 142 158Z" fill="#552000" opacity=".52" filter="url(#crease-soft)"/>',
    ])
    parts.extend(['</g></g>', '<use href="#left-ear"/><use href="#left-ear" transform="translate(192 0) scale(-1 1)"/>',
                  f'<path d="{HEAD}" fill="#522000" opacity=".6" transform="translate(0 1.4)" filter="url(#face-shadow)"/>',
                  '<g filter="url(#face-depth)">', f'<path d="{HEAD}" fill="url(#gold)"/>',
                  f'<g clip-path="url(#head-clip)"><ellipse cx="94" cy="68" rx="39" ry="24" fill="url(#forehead-light)"/><path d="{CREAM}" fill="url(#cream)" filter="url(#cream-soft)"/></g></g>'])
    for x in [69.8, 121.5]:
        parts.extend([f'<ellipse cx="{x}" cy="96.4" rx="7.65" ry="10.65" fill="url(#eye)" stroke="#a17112" stroke-width=".5" filter="url(#edge-soft)"/>',
                      f'<ellipse cx="{x-.2}" cy="90.8" rx="2.75" ry="3.45" fill="url(#eye-shine)" filter="url(#edge-soft)"/>'])
    parts.extend([
        f'<path d="{MOUTH}" fill="none" stroke="#fff2c6" stroke-width="2.4" opacity=".75" filter="url(#soft)"/>',
        f'<path d="{MOUTH}" fill="url(#mouth)" stroke="#7c390f" stroke-width=".55"/>',
        '<g clip-path="url(#mouth-clip)"><ellipse cx="96" cy="141" rx="12.9" ry="9.2" fill="url(#tongue)" filter="url(#soft)"/></g>',
        f'<path d="{LIPS}M96 117V121" fill="none" stroke="#83521d" stroke-width="1.9" stroke-linecap="round" opacity=".7" filter="url(#soft)"/>',
        f'<path d="{LIPS}M96 117V121" fill="none" stroke="#281100" stroke-width=".85" stroke-linecap="round"/>',
        f'<path d="{NOSE}" fill="none" stroke="#fdf0c4" stroke-width="2.3" filter="url(#soft)"/>',
        f'<path d="{NOSE}" fill="url(#nose)" stroke="#533110" stroke-width=".4"/>',
        '<ellipse cx="95.3" cy="107.4" rx="8.8" ry="1.7" fill="url(#nose-shine)"/>',
    ])
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="'
           + html.escape(title, quote=True) + '"><defs>' + ''.join(defs) + '</defs><g clip-path="url(#padding)">'
           + ''.join(parts) + '</g></svg>\n')
    return svg, {'source': 'png/lion.png', 'sourceSha256': hashlib.sha256((ROOT/'png/lion.png').read_bytes()).hexdigest(),
                 'strategy': 'component-authored-reference-fitted-lion-with-overlapping-mane-locks-and-compact-material-gradients'}


if __name__ == '__main__':
    import sys
    Path(sys.argv[1]).write_text(rebuild('Lion')[0])
