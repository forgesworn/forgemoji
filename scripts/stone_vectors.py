"""Reference-measured sacred stone with compact, procedural mineral texture.

Its outline and twelve irregular painted glyphs follow the pinned community
photograph. Gradients and deterministic turbulence recreate the material;
they do not encode the photograph's individual grains. No raster is embedded.
"""
import hashlib
import html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_URL = 'https://600.wtf/img/sacred-stone.webp'
SOURCE_SHA256 = '317add9f9e026abc66ffd42474956e8b14d109e930f879bf62522240f5276b06'
INSCRIPTION = ('600', '000', '000', '000')

# Curves measured from the outline and each painted glyph. Every zero has
# a counter, including the two whose photographed paint is most worn.
OUTLINE = 'M94.857 8.081C84.537 8.701 74.456 11.832 65.860 17.174C55.896 23.367 47.930 32.531 42.296 42.657C37.302 51.632 34.142 61.362 31.528 71.406C29.119 80.667 27.175 90.196 26.664 99.837C25.588 120.135 30.863 140.935 43.441 156.568C56.701 173.049 78.077 183.786 99.309 183.211C120.994 182.624 142.529 170.238 153.802 152.032C163.840 135.822 165.741 114.999 164.262 95.292C162.715 74.695 157.475 55.317 146.961 38.009C140.924 28.071 133.148 18.816 123.003 13.525C114.627 9.157 104.635 7.493 94.857 8.081Z'
# A one-unit clearance at the left of rows one/two keeps the painted six
# separate from the zero below it at the native reaction size.
GLYPHS = ('M68.221 27.474C62.181 26.272 58.233 36.964 57.749 42.569C57.520 45.216 58.064 46.729 59.893 48.627C61.713 '
 '50.516 64.804 52.787 67.782 52.528C73.838 51.999 79.426 41.007 74.636 36.871C73.370 35.778 71.377 35.164 '
 '69.617 34.754C68.012 34.380 66.600 34.176 67.054 33.431C67.552 32.614 70.292 31.145 70.775 29.906C71.233 '
 '28.731 69.667 27.762 68.221 27.474ZM66.821 38.604C68.837 38.027 70.364 42.748 68.316 43.131C67.331 43.315 '
 '65.518 42.495 65.182 41.352C64.861 40.259 65.892 38.870 66.821 38.604Z',
 'M87.060 27.388C82.250 27.936 77.858 35.448 78.343 41.408C78.804 47.070 83.667 51.331 88.269 50.879C93.081 '
 '50.406 97.608 44.782 97.245 38.851C96.888 33.000 91.773 26.851 87.060 27.388ZM86.660 31.728C87.598 31.232 '
 '89.577 32.533 90.060 34.511C90.518 36.387 89.631 38.873 88.710 39.296C86.859 40.147 84.871 32.673 86.660 '
 '31.728Z',
 'M110.938 26.110C117.334 27.328 120.659 41.557 115.606 47.244C113.196 49.956 108.882 50.726 105.372 '
 '49.296C101.504 47.721 98.614 43.475 98.728 39.022C98.900 32.320 105.879 25.146 110.938 26.110ZM112.679 '
 '36.747C112.679 38.945 111.065 41.143 109.667 41.143C108.270 41.143 107.088 38.945 107.088 36.747C107.088 '
 '34.549 108.270 32.351 109.667 32.351C111.065 32.351 112.679 34.549 112.679 36.747Z',
 'M66.051 55.329C61.726 55.843 56.353 63.570 56.441 70.390C56.527 76.989 61.724 82.740 66.919 82.010C72.256 '
 '81.261 77.590 73.672 76.580 67.180C76.073 63.923 73.969 60.942 71.967 58.713C70.013 56.538 68.156 55.079 '
 '66.051 55.329ZM66.258 61.742C68.173 61.224 68.962 69.371 67.039 70.090C66.063 70.455 64.388 68.907 64.158 '
 '66.850C63.919 64.709 65.246 62.016 66.258 61.742Z',
 'M86.427 54.182C81.180 54.857 77.889 62.613 77.827 68.649C77.797 71.612 78.544 74.160 80.572 76.218C82.726 '
 '78.405 86.326 80.039 89.342 79.770C95.390 79.232 99.094 71.047 98.234 64.683C97.836 61.733 96.456 59.174 '
 '94.267 57.212C92.050 55.225 89.003 53.851 86.427 54.182ZM86.897 59.997C88.104 59.500 90.353 60.876 90.655 '
 '62.852C90.941 64.731 89.466 67.151 88.269 67.468C85.966 68.077 84.690 60.905 86.897 59.997Z',
 'M107.252 53.441C102.927 54.839 98.988 62.086 99.869 68.412C100.758 74.800 106.558 80.249 112.633 '
 '78.602C115.824 77.737 119.091 74.915 119.987 71.790C120.843 68.809 119.540 65.553 118.683 62.532C117.755 '
 '59.257 117.351 56.258 114.360 56.154C113.589 56.126 112.645 56.292 111.937 55.902C111.272 55.537 110.814 '
 '54.681 110.311 54.126C109.386 53.107 108.308 53.100 107.252 53.441ZM109.024 58.052C110.143 56.967 112.636 '
 '57.713 113.328 59.811C113.952 61.703 113.111 64.696 112.067 65.702C110.973 66.756 109.656 65.625 108.902 '
 '63.723C108.140 61.800 107.954 59.089 109.024 58.052Z',
 'M62.961 84.779C59.715 86.371 56.238 91.371 56.464 94.503C56.561 95.839 57.332 96.834 58.024 97.469C58.387 '
 '97.802 58.728 98.036 58.907 98.306C59.094 98.589 59.103 98.913 58.998 99.384C58.582 101.248 56.377 105.413 '
 '57.461 108.406C58.590 111.521 63.281 113.367 66.839 112.668C70.646 111.921 73.155 108.261 74.497 '
 '104.960C75.730 101.929 75.978 99.201 75.205 95.953C73.756 89.867 68.724 81.953 62.961 84.779ZM64.851 '
 '89.551C66.793 88.777 69.578 91.081 69.839 92.733C69.958 93.490 69.548 94.109 69.083 95.064C68.602 96.050 '
 '68.063 97.394 67.303 98.120C65.746 99.606 63.260 98.504 62.583 96.146C61.916 93.826 63.000 90.289 64.851 '
 '89.551Z',
 'M84.271 85.086C81.250 86.598 79.956 90.378 79.165 93.975C78.423 97.347 78.123 100.559 79.274 '
 '103.699C79.903 105.416 80.967 107.112 81.774 107.815C82.460 108.411 82.961 108.292 83.468 108.759C84.041 '
 '109.287 84.620 110.564 85.970 111.132C87.192 111.647 89.047 111.580 90.655 111.146C97.664 109.254 99.995 '
 '100.382 98.572 93.444C97.885 90.095 96.324 87.196 93.374 85.606C90.688 84.158 86.850 83.796 84.271 '
 '85.086ZM87.011 89.326C88.194 88.751 90.353 90.275 90.718 92.622C91.082 94.969 89.654 98.140 88.461 '
 '98.657C86.119 99.671 84.687 90.455 87.011 89.326Z',
 'M104.941 85.060C102.198 86.850 101.509 90.368 100.748 93.934C100.027 97.306 99.242 100.721 101.164 '
 '102.451C102.202 103.385 104.029 103.827 104.753 104.336C105.134 104.604 105.209 104.891 105.155 '
 '105.432C105.108 105.898 104.964 106.552 105.034 107.135C105.352 109.777 110.068 110.940 113.623 '
 '110.130C120.618 108.537 123.126 99.313 121.168 92.213C120.179 88.626 118.050 85.581 114.497 84.319C111.461 '
 '83.241 107.385 83.464 104.941 85.060ZM111.107 86.758C113.605 86.361 114.819 95.671 112.397 96.137C111.122 '
 '96.382 108.838 94.174 108.597 91.713C108.374 89.441 109.892 86.951 111.107 86.758Z',
 'M63.772 115.926C58.146 117.574 53.731 125.692 54.622 133.200C55.488 140.499 61.371 147.221 67.279 '
 '145.387C70.486 144.392 73.700 140.877 74.917 137.174C76.006 133.861 75.495 130.398 74.680 127.372C74.244 '
 '125.752 73.720 124.257 72.793 123.129C71.866 122.000 70.535 121.238 69.676 120.033C68.780 118.775 68.398 '
 '117.035 67.394 116.229C66.496 115.508 65.100 115.537 63.772 115.926ZM64.570 121.215C67.035 120.059 68.245 '
 '130.282 65.721 131.203C64.526 131.639 62.496 129.993 62.178 127.589C61.847 125.094 63.360 121.783 64.570 '
 '121.215Z',
 'M86.137 114.836C82.801 116.363 80.237 120.564 79.022 124.288C78.050 127.267 77.940 129.941 78.400 '
 '133.196C78.934 136.970 80.232 141.525 82.935 143.791C85.552 145.985 89.486 146.032 92.452 144.641C98.429 '
 '141.837 100.472 133.192 98.901 126.500C98.084 123.020 96.289 120.068 94.036 117.437C92.886 116.095 91.617 '
 '114.836 90.083 114.403C88.844 114.053 87.432 114.243 86.137 114.836ZM87.084 120.400C87.758 119.984 88.766 '
 '120.515 89.518 121.481C90.247 122.417 90.737 123.762 90.899 125.089C91.223 127.743 90.238 130.325 88.710 '
 '131.189C87.872 131.663 86.870 131.621 86.502 130.881C86.156 130.184 86.370 128.869 86.337 127.563C86.302 '
 '126.217 86.005 124.880 86.037 123.509C86.068 122.179 86.409 120.816 87.084 120.400Z',
 'M113.058 113.191C119.625 113.821 124.344 124.985 123.743 133.341C123.525 136.376 122.604 139.041 120.716 '
 '141.205C118.072 144.237 113.528 146.285 109.897 145.682C104.827 144.840 101.537 138.829 100.926 '
 '132.456C100.275 125.672 102.661 118.477 107.199 115.085C108.985 113.750 111.103 113.004 113.058 '
 '113.191ZM113.676 125.820C113.676 128.740 112.024 131.661 110.588 131.661C109.152 131.661 107.931 128.740 '
 '107.931 125.820C107.931 122.899 109.152 119.979 110.588 119.979C112.024 119.979 113.676 122.899 113.676 '
 '125.820Z')


def rebuild(title):
    # Keep the same source pin as the photographic master. Normal package
    # builds copy the SVG; only explicit reauthoring consults this cache.
    cache = Path('/private/tmp/forgemoji-sacred-stone-reference.webp')
    if not cache.exists():
        import urllib.request
        cache.write_bytes(urllib.request.urlopen(SOURCE_URL, timeout=30).read())
    if hashlib.sha256(cache.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('The stone reference changed; inspect it before rebuilding')
    # The local comparison can show the pinned photograph without copying it
    # into the repository or distributable package.
    from PIL import Image
    photo = Image.open(cache).convert('RGBA')
    bounds = photo.getchannel('A').point(lambda a: 255 if a >= 32 else 0).getbbox()
    photo = photo.crop(bounds)
    fitted = photo.copy()
    fitted.thumbnail((205, 205), Image.Resampling.LANCZOS)
    # Retain the photograph's original detail for enlarged visual review,
    # using the same framing as the previous 224-unit photographic author.
    scale = 1024 / 224
    width, height = (round(v * scale) for v in fitted.size)
    photo = photo.resize((width, height), Image.Resampling.LANCZOS)
    reference = Image.new('RGBA', (1024, 1024))
    reference.alpha_composite(photo, (round((224-fitted.width)//2 * scale),
                                     round((224-fitted.height)//2 * scale)))
    reference.save('/private/tmp/forgemoji-sacred-stone-review-reference.png')
    defs = '''
<radialGradient id="stone" gradientUnits="userSpaceOnUse" cx="110.794" cy="63.775" r="117.86" gradientTransform="translate(0 -9.028) scale(1 1.141562)">
 <stop stop-color="#918e86"/><stop offset=".35" stop-color="#a9a59f"/><stop offset=".6" stop-color="#928984"/><stop offset=".82" stop-color="#756b6b"/><stop offset="1" stop-color="#282828"/>
</radialGradient>
<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="84" y1="25" x2="92" y2="148"><stop stop-color="#2a2927"/><stop offset=".55" stop-color="#252525"/><stop offset="1" stop-color="#332c2b"/></linearGradient>
<radialGradient id="warm-mineral"><stop stop-color="#aa8276" stop-opacity=".4"/><stop offset=".6" stop-color="#b69586" stop-opacity=".17"/><stop offset="1" stop-color="#bda591" stop-opacity="0"/></radialGradient>
<radialGradient id="quartz"><stop stop-color="#e5e4db" stop-opacity=".42"/><stop offset="1" stop-color="#d9d7cb" stop-opacity="0"/></radialGradient>
<filter id="granite" filterUnits="userSpaceOnUse" x="22" y="5" width="148" height="182" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency=".13 .16" numOctaves="2" seed="600" result="mottle"/>
 <feColorMatrix in="mottle" type="matrix" values="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 1"/>
 <feComponentTransfer result="mottle-shade"><feFuncR type="linear" slope="2.4" intercept="-.7"/><feFuncG type="linear" slope="2.4" intercept="-.7"/><feFuncB type="linear" slope="2.4" intercept="-.7"/><feFuncA type="table" tableValues=".6 .6"/></feComponentTransfer>
 <feBlend in="mottle-shade" in2="SourceGraphic" mode="soft-light" result="weathered"/>
 <feTurbulence type="fractalNoise" baseFrequency=".85 .75" numOctaves="2" seed="601" result="grain"/>
 <feColorMatrix in="grain" type="matrix" values="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 0 0 0 0 1"/>
 <feComponentTransfer result="grain-shade"><feFuncR type="linear" slope="2.25" intercept="-.625"/><feFuncG type="linear" slope="2.25" intercept="-.625"/><feFuncB type="linear" slope="2.25" intercept="-.625"/><feFuncA type="table" tableValues=".65 .65"/></feComponentTransfer>
 <feBlend in="grain-shade" in2="weathered" mode="soft-light" result="texture"/>
 <feComposite in="texture" in2="SourceAlpha" operator="in" result="surface"/>
 <feGaussianBlur in="SourceAlpha" stdDeviation="1.35" result="inset"/><feComposite in="SourceAlpha" in2="inset" operator="out" result="rim"/>
 <feFlood flood-color="#262722" flood-opacity=".52"/><feComposite in2="rim" operator="in" result="edge"/><feMerge><feMergeNode in="surface"/><feMergeNode in="edge"/></feMerge>
</filter>
<filter id="paint-wear" filterUnits="userSpaceOnUse" x="48" y="20" width="80" height="131" color-interpolation-filters="sRGB">
 <feTurbulence type="fractalNoise" baseFrequency=".68 .82" numOctaves="2" seed="602" result="wear"/>
 <feColorMatrix in="wear" type="matrix" values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0"/>
 <feComponentTransfer><feFuncA type="table" tableValues=".98 .95 .88 .7 .2 0"/></feComponentTransfer>
 <feComposite in="SourceGraphic" operator="in"/>
</filter>
<filter id="soft" x="-10%" y="-10%" width="120%" height="120%" color-interpolation-filters="sRGB"><feGaussianBlur stdDeviation=".35"/></filter>
'''
    defs += f'<clipPath id="rock-clip"><path d="{OUTLINE}"/></clipPath><clipPath id="padding"><path d="M8 8H184V184H8Z"/></clipPath>'
    components = [f'<path d="{OUTLINE}" fill="url(#stone)"/>',
                  '<ellipse cx="43" cy="81" rx="14" ry="22" fill="url(#warm-mineral)"/>',
                  '<ellipse cx="53" cy="143" rx="14" ry="22" fill="url(#warm-mineral)"/>',
                  '<ellipse cx="132" cy="133" rx="17" ry="10" fill="url(#warm-mineral)"/>',
                  '<ellipse cx="153" cy="97" rx="9" ry="21" fill="url(#quartz)"/>',
                  '<ellipse cx="112" cy="32" rx="10" ry="6" fill="url(#quartz)"/>',
                  '<ellipse cx="83" cy="159" rx="13" ry="9" fill="url(#quartz)"/>',
                  '<path d="M42 67Q47 63 49 57M37 99L42 96M40 137Q42 140 43 143M73 174L81 179M134 162L137 157M151 125L157 113M139 39L144 45M85 17L88 20" fill="none" stroke="#d8d5c8" stroke-width=".45" opacity=".4" stroke-linecap="round"/>']
    parts = ['<g clip-path="url(#rock-clip)">', '<g filter="url(#granite)">', ''.join(components), '</g>',
             '<path d="M29 117C29 140 44 162 60 171C73 179 86 183 99 182C119 180 135 173 148 159" fill="none" stroke="#333330" stroke-width=".7" opacity=".52" filter="url(#soft)"/>',
             '<path d="M102 179Q104 177 108 178L113 176L115 174M47 151Q51 155 54 159" fill="none" stroke="#b5aba5" stroke-width=".65" opacity=".55" stroke-linecap="round"/>',
             '<g id="inscription" data-inscription="600000000000" fill="url(#ink)" fill-rule="evenodd" filter="url(#paint-wear)">']
    for row, text in enumerate(INSCRIPTION):
        paths = ''.join(GLYPHS[row*3:row*3+3])
        # A text prefix protects leading zeroes from numeric SVG optimisers.
        parts.append(f'<path id="row-{row+1}" data-digits="digits:{text}" d="{paths}"/>')
    parts.extend(['</g>', '</g>'])
    label = html.escape(title + ', ' + ' '.join(INSCRIPTION), quote=True)
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="'
           + label + '"><defs>' + defs + '</defs><g clip-path="url(#padding)">' + ''.join(parts) + '</g></svg>\n')
    return svg, {'source': SOURCE_URL, 'sourceSha256': SOURCE_SHA256, 'referenceRedistributed': False,
                 'strategy': 'reference-measured-stone-and-hand-painted-digit-curves-with-fitted-gradients-and-procedural-granite',
                 'inscription': list(INSCRIPTION), 'textureFidelity': 'procedural material reconstruction; individual photographic grains are not encoded'}


if __name__ == '__main__':
    import sys
    Path(sys.argv[1]).write_text(rebuild('Sacred stone')[0])
