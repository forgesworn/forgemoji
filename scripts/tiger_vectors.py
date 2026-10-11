"""Compact, component-authored tiger, measured against png/tiger.png.

The ears, cheek tufts, brow, stripes and muzzle are editable cubic curves.
Material gradients replace the previous dense, sampled colour surface.
"""
import hashlib
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Coordinates are in the reference PNG's 192-pixel canvas. Preserve its
# slightly asymmetric tufts instead of turning the cheeks into a circle.
FUR = ('M96 33C125 31 149 48 163 73'
       'C171 86 181 108 180 122Q179 126 176 122'
       'C177 133 174 144 169 148Q167 150 164 145'
       'C160 153 153 159 145 160Q142 162 138 160'
       'C132 164 126 163 123 162C116 165 109 170 97 171'
       'C86 171 77 169 69 164Q61 164 57 162'
       'Q55 165 48 162C38 160 31 153 29 146'
       'Q27 151 23 147C17 140 16 131 16 122'
       'Q11 126 11 119C12 103 20 88 29 74'
       'C45 49 66 32 96 33Z')
HEAD = ('M96 33C127 31 149 49 162 72C167 79 169 85 171 92'
        'C165 92 158 80 154 72C156 87 155 99 144 110'
        'C140 115 133 116 127 113C121 111 116 106 111 103'
        'Q109 102 108 107C107 111 106 113 104 114Q96 119 87 114'
        'C84 111 84 106 83 103Q82 101 80 103C75 107 68 113 62 115'
        'C55 117 49 115 44 110C36 101 35 87 39 72'
        'C33 79 28 92 21 95C26 80 34 66 44 54'
        'C58 39 77 32 96 33Z')
EAR = ('M69 38C66 30 57 19 46 19C32 18 22 30 20 43'
       'C17 55 23 65 32 72C41 57 53 46 69 38Z')
EAR_STRIPE = ('M55 25C47 19 37 21 30 26C21 33 18 46 21 55'
              'C21 42 25 33 34 28C42 24 47 24 55 26Z')
EAR_INNER = ('M54 44C51 37 45 34 40 36C31 39 30 49 33 56'
             'Q35 61 39 63C44 56 48 50 54 47Z')
CHEEK_STRIPES = ('M38 74C34 79 31 85 30 92C30 102 39 112 49 113'
                 'Q55 114 51 111C40 102 36 88 38 74Z'
                 'M29 94C26 99 24 106 24 113C24 126 33 135 44 137'
                 'C48 138 52 136 51 133C51 131 47 130 43 127'
                 'C32 119 27 108 29 94Z')
BROW_STRIPES = ('M96 35Q99 35 101 40C112 40 124 44 127 48'
                'Q129 51 123 49C116 46 109 46 101 46L101 53'
                'C113 54 123 58 128 63Q130 68 124 65'
                'C117 62 109 60 101 60L100 68'
                'C107 70 113 72 114 76Q115 79 111 78'
                'Q105 75 100 75L97 79Q96 81 94 78L92 75'
                'Q86 75 82 77Q77 79 79 75C81 72 86 70 92 69'
                'L92 60C84 60 76 62 69 65Q64 68 65 63'
                'C69 58 80 54 92 53L92 46C83 45 75 47 68 49'
                'Q63 51 66 47C70 43 81 40 92 40Q94 35 96 35Z')
MOUTH = ('M70 121C73 126 78 128 84 128C90 128 94 125 96 122'
         'C98 125 102 128 108 128C114 128 119 125 122 121'
         'C119 135 115 145 108 150C101 157 88 156 81 148'
         'C75 141 73 132 70 122Z')
MUZZLE = ('M70 121C73 126 78 128 84 128C90 128 94 125 96 122'
          'C98 125 102 128 108 128C114 128 119 125 122 121')
NOSE = ('M84 108C86 105 92 105 96 105C101 105 107 106 108 109'
        'C108 112 100 118 96 119C92 119 84 113 84 110Z')


def rebuild(title):
    defs = '''
<radialGradient id="fur" gradientUnits="userSpaceOnUse" cx="94.4" cy="107" r="105" gradientTransform="translate(0 41.11) scale(1 .6158)">
 <stop stop-color="#fbe9c5"/><stop offset=".4" stop-color="#fae1b0"/><stop offset=".6" stop-color="#f4d7a5"/><stop offset=".75" stop-color="#e5c48f"/><stop offset=".85" stop-color="#d1a76f"/><stop offset=".95" stop-color="#ca9b5f"/><stop offset="1" stop-color="#c38d52"/>
</radialGradient>
<linearGradient id="orange" gradientUnits="userSpaceOnUse" x1="0" y1="33" x2="0" y2="115">
 <stop stop-color="#c79502"/><stop offset=".073" stop-color="#fbc201"/><stop offset=".195" stop-color="#feca0b"/><stop offset=".354" stop-color="#febe11"/><stop offset=".561" stop-color="#feb113"/><stop offset=".805" stop-color="#fdaf14"/><stop offset="1" stop-color="#febc1a"/>
</linearGradient>
<radialGradient id="brow-light" gradientUnits="userSpaceOnUse" cx="94.14" cy="90" r="66.9" gradientTransform="translate(0 16.293) scale(1 .81896)">
 <stop offset=".35" stop-color="#ea0000" stop-opacity="0"/><stop offset=".5" stop-color="#ea0000" stop-opacity=".017"/><stop offset=".65" stop-color="#ea0000" stop-opacity=".068"/><stop offset=".8" stop-color="#ea0000" stop-opacity=".153"/><stop offset="1" stop-color="#ea0000" stop-opacity=".32"/>
</radialGradient>
<radialGradient id="ear" cx=".49" cy=".52" r=".53">
 <stop stop-color="#ffc331"/><stop offset=".58" stop-color="#ffad15"/><stop offset=".78" stop-color="#f68b00"/><stop offset="1" stop-color="#703500"/>
</radialGradient>
<radialGradient id="ear-inside" cx=".34" cy=".92" r=".92">
 <stop stop-color="#ffe8b7"/><stop offset=".55" stop-color="#e3b16a"/><stop offset="1" stop-color="#9c6321"/>
</radialGradient>
<linearGradient id="stripe" gradientUnits="userSpaceOnUse" x1="0" y1="40" x2="0" y2="137">
 <stop stop-color="#0d0701"/><stop offset=".68" stop-color="#211304"/><stop offset="1" stop-color="#170b01"/>
</linearGradient>
<linearGradient id="brow-stripe" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#3a240f"/><stop offset=".48" stop-color="#573b23"/><stop offset="1" stop-color="#4b311b"/></linearGradient>
<radialGradient id="chin-light"><stop stop-color="#fff6dc" stop-opacity=".58"/><stop offset=".55" stop-color="#fff0cf" stop-opacity=".24"/><stop offset="1" stop-color="#fff0cf" stop-opacity="0"/></radialGradient>
<radialGradient id="eye" cx=".5" cy=".72" r=".75" gradientTransform="translate(0 .14) scale(1 .8)">
 <stop stop-color="#241400"/><stop offset=".6" stop-color="#0e0800"/><stop offset="1" stop-color="#030200"/>
</radialGradient>
<radialGradient id="eye-shine"><stop stop-color="#fff"/><stop offset=".3" stop-color="#fce7d3" stop-opacity=".9"/><stop offset="1" stop-color="#ffd7b2" stop-opacity="0"/></radialGradient>
<linearGradient id="mouth" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#210100"/><stop offset=".7" stop-color="#4b0100"/><stop offset="1" stop-color="#810b09"/></linearGradient>
<radialGradient id="tongue" cx=".52" cy=".74" r=".74"><stop stop-color="#f55952"/><stop offset=".56" stop-color="#db3f3a"/><stop offset="1" stop-color="#940b0c"/></radialGradient>
<radialGradient id="nose" cx=".5" cy=".17" r=".87"><stop stop-color="#ff6860"/><stop offset=".28" stop-color="#ed3930"/><stop offset=".62" stop-color="#c81510"/><stop offset="1" stop-color="#6c0300"/></radialGradient>
<radialGradient id="nose-shine"><stop stop-color="#ffb39a" stop-opacity=".76"/><stop offset="1" stop-color="#ff826c" stop-opacity="0"/></radialGradient>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".65"/></filter>
<filter id="head-soft" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".35"/></filter>
<filter id="fur-soft" x="-30%" y="-30%" width="160%" height="160%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation="1.25"/></filter>
<filter id="bevel" x="-15%" y="-15%" width="130%" height="130%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation=".55" result="height"/><feSpecularLighting in="height" surfaceScale="1.4" specularConstant=".3" specularExponent="18" lighting-color="#d2a26f" result="shine"><feDistantLight azimuth="235" elevation="50"/></feSpecularLighting><feComposite in="shine" in2="SourceAlpha" operator="in" result="rim"/><feComposite in="SourceGraphic" in2="rim" operator="arithmetic" k2="1" k3=".5"/>
</filter>
<filter id="fur-depth" x="-5%" y="-5%" width="110%" height="110%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="2.5" result="inset"/><feComposite in="SourceAlpha" in2="inset" operator="out" result="edge"/><feFlood flood-color="#734417" flood-opacity=".9"/><feComposite in2="edge" operator="in"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode/></feMerge>
</filter>
<filter id="ear-depth" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB">
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.5" result="inset"/><feComposite in="SourceAlpha" in2="inset" operator="out" result="edge"/><feFlood flood-color="#702900" flood-opacity=".85"/><feComposite in2="edge" operator="in"/><feMerge><feMergeNode in="SourceGraphic"/><feMergeNode/></feMerge>
</filter>
'''
    defs += f'<clipPath id="fur-clip"><path d="{FUR}"/></clipPath><clipPath id="mouth-clip"><path d="{MOUTH}"/></clipPath>'
    defs += (f'<g id="left-ear"><path d="{EAR}" fill="url(#ear)" filter="url(#ear-depth)"/>'
             f'<path d="{EAR_STRIPE}" fill="#251305" filter="url(#bevel)"/>'
             f'<path d="{EAR_INNER}" fill="url(#ear-inside)" filter="url(#soft)"/></g>')
    parts = ['<use href="#left-ear"/><use href="#left-ear" transform="translate(192 0) scale(-1 1)"/>',
             f'<path d="{FUR}" fill="url(#fur)" filter="url(#fur-depth)"/>',
             '<g clip-path="url(#fur-clip)">',
             # Subtle depressions between the individual cheek tufts. All
             # eight share one paint and one small blur, rather than tiles.
             '<path d="M17 120Q21 132 25 145Q16 133 17 120ZM27 133Q31 147 41 155Q29 152 27 133ZM43 143Q48 154 58 161Q45 158 43 143ZM58 153Q65 159 71 163Q60 164 58 153ZM175 120Q171 132 167 145Q176 133 175 120ZM165 133Q161 147 151 155Q163 152 165 133ZM149 143Q144 154 134 161Q147 158 149 143ZM134 153Q127 159 121 163Q132 164 134 153Z" fill="#87571e" opacity=".25" filter="url(#fur-soft)"/>',
             '<ellipse cx="96" cy="145" rx="35" ry="26" fill="url(#chin-light)"/>',
             '</g>', '<g filter="url(#head-soft)">',
             f'<path d="{HEAD}" fill="url(#orange)"/>',
             f'<path d="{HEAD}" fill="url(#brow-light)"/>', '</g>',
             f'<path d="{CHEEK_STRIPES}" fill="url(#stripe)" filter="url(#bevel)"/>',
             f'<path d="{CHEEK_STRIPES}" fill="url(#stripe)" filter="url(#bevel)" transform="translate(192 0) scale(-1 1)"/>',
             f'<path d="{BROW_STRIPES}" fill="url(#brow-stripe)" filter="url(#bevel)"/>']
    for x in [65.8,126.5]:
        parts += [f'<ellipse cx="{x}" cy="96" rx="8.5" ry="12.1" fill="url(#eye)" stroke="#90540a" stroke-width=".5"/>',
                  f'<ellipse cx="{x-1}" cy="89.6" rx="3.35" ry="4" fill="url(#eye-shine)"/>']
    parts += [f'<path d="{MOUTH}" fill="url(#mouth)" stroke="#8c4f20" stroke-width=".45"/>',
              '<g clip-path="url(#mouth-clip)"><ellipse cx="95.6" cy="146.6" rx="15.3" ry="9.5" fill="url(#tongue)" filter="url(#soft)"/></g>',
              f'<path d="{MUZZLE}" fill="none" stroke="#98642e" stroke-width="2.3" stroke-linecap="round" filter="url(#soft)" opacity=".48"/>',
              f'<path d="{MUZZLE}M96 117V123" fill="none" stroke="#351700" stroke-width=".9" stroke-linecap="round"/>',
              f'<path d="{NOSE}" fill="url(#nose)" stroke="#9b270f" stroke-width=".4"/>',
              '<ellipse cx="95.5" cy="108.2" rx="8.5" ry="1.75" fill="url(#nose-shine)"/>']
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="'
           + html.escape(title,quote=True) + '"><defs>' + defs + '</defs>' + ''.join(parts) + '</svg>\n')
    source = ROOT/'png/tiger.png'
    return svg, {'source':'png/tiger.png','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'strategy':'component-authored-reference-fitted-tiger-with-compact-material-gradients'}


if __name__ == '__main__':
    import sys
    Path(sys.argv[1]).write_text(rebuild('Tiger')[0])
