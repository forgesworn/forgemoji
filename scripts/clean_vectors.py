"""Component-authored emoji: explicit geometry, rather than hue fragments.

The originals remain the design references. Every visible contour here is an
intentional feature, with continuous, resolution-independent SVG shading.
"""
import html
import math
import random

NS = 'http://www.w3.org/2000/svg'


class Drawing:
    def __init__(self, title):
        self.title = title
        self.defs = []
        self.parts = []
        self.counter = 0
        self.materials = {}
        self.defs.extend([
            '<radialGradient id="volume-rim" cx=".5" cy=".45" r=".6"><stop offset=".55" stop-color="#3a2113" stop-opacity="0"/><stop offset=".84" stop-color="#3a2113" stop-opacity=".08"/><stop offset="1" stop-color="#3a2113" stop-opacity=".33"/></radialGradient>',
            '<radialGradient id="volume-shine" cx=".42" cy=".13" r=".65"><stop stop-color="#fff" stop-opacity=".56"/><stop offset=".32" stop-color="#fff" stop-opacity=".2"/><stop offset=".78" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        ])

    def volume(self, element, fill):
        if fill.startswith('url(') and not any(key in fill for key in ['eye','nose','mouth','tongue','nostril']):
            self.parts.append(element.replace(f'fill="{fill}"','fill="url(#volume-rim)"'))
            self.parts.append(element.replace(f'fill="{fill}"','fill="url(#volume-shine)"'))

    def radial(self, key, light, middle, dark, cx='.36', cy='.26', r='.85'):
        if key not in self.materials:
            self.defs.append(f'<radialGradient id="{key}" cx="{cx}" cy="{cy}" r="{r}"><stop stop-color="{light}"/><stop offset=".48" stop-color="{middle}"/><stop offset="1" stop-color="{dark}"/></radialGradient>')
            self.materials[key] = f'url(#{key})'
        return self.materials[key]

    def linear(self, key, stops, x1='0', y1='0', x2='0', y2='1'):
        if key not in self.materials:
            self.defs.append(f'<linearGradient id="{key}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">' + ''.join(f'<stop offset="{p}" stop-color="{c}"/>' for p,c in stops) + '</linearGradient>')
            self.materials[key] = f'url(#{key})'
        return self.materials[key]

    def path(self, d, fill, stroke=None, width=1, extra=''):
        line = f' stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"' if stroke else ''
        element=f'<path d="{d}" fill="{fill}"{extra}/>'
        self.parts.append(f'<path d="{d}" fill="{fill}"{line}{extra}/>')
        self.volume(element,fill)

    def ellipse(self, x, y, rx, ry, fill, extra=''):
        element=f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}"{extra}/>'
        self.parts.append(element)
        self.volume(element,fill)

    def line(self, d, colour, width=1, opacity=1):
        self.path(d, 'none', colour, width, f' stroke-linecap="round" opacity="{opacity}"')

    def clipped(self, shape, parts):
        self.counter += 1
        key = f'clip{self.counter}'
        self.defs.append(f'<clipPath id="{key}">{shape}</clipPath>')
        self.parts.append(f'<g clip-path="url(#{key})">{parts}</g>')

    def start_clip(self, d):
        self.counter += 1
        key = f'clip{self.counter}'
        self.defs.append(f'<clipPath id="{key}"><path d="{d}"/></clipPath>')
        self.parts.append(f'<g clip-path="url(#{key})">')

    def end_clip(self):
        self.parts.append('</g>')

    def finish(self):
        self.defs.append('<clipPath id="padding"><rect x="8" y="8" width="176" height="176"/></clipPath>')
        return f'<svg xmlns="{NS}" width="192" height="192" viewBox="0 0 192 192" role="img" aria-label="{html.escape(self.title,quote=True)}"><defs>'+''.join(self.defs)+'</defs><g clip-path="url(#padding)">'+''.join(self.parts)+'</g></svg>\n'


def palette(s):
    return {
        'gold':s.radial('gold','#fff3a0','#ffcd32','#db8900'),
        'orange':s.radial('orange','#ffbe42','#f8870b','#b74200'),
        'brown':s.radial('brown','#cd8748','#995024','#51250f'),
        'dark':s.radial('dark','#56514c','#292727','#101011'),
        'cream':s.radial('cream','#fffdf4','#eee4d2','#bb9b74'),
        'white':s.radial('white','#ffffff','#f4efea','#c5b7a9'),
        'gray':s.radial('gray','#e5dede','#afa7a7','#665d60'),
        'pink':s.radial('pink','#ffc4be','#fa888d','#cf4056'),
        'red':s.radial('red','#ff8584','#f32940','#a90724'),
        'green':s.radial('green','#b8ee57','#77ba16','#397b09'),
        'blue':s.radial('blue','#71d7ff','#0d9eea','#07569d'),
        'ice':s.radial('ice','#eefcff','#b8e7f8','#70b1d4'),
    }


def eye(s,x,y,rx=7.5,ry=10.5):
    fill=s.radial('eye','#5b3e20','#201507','#050504',cx='.35',cy='.3',r='.75')
    s.ellipse(x,y,rx,ry,fill)
    s.ellipse(x-rx*.23,y-ry*.42,rx*.23,ry*.22,'#fff',extra=' opacity=".92"')
    s.ellipse(x+rx*.24,y+ry*.37,rx*.12,ry*.11,'#b28d57',extra=' opacity=".32"')


def nose(s,x=96,y=116,rx=11,ry=7,pink=False):
    fill=s.radial('nose-pink' if pink else 'nose','#ffa8a4' if pink else '#80776b','#ef6176' if pink else '#2b2520','#b92242' if pink else '#100e0c',cx='.42',cy='.12')
    s.path(f'M{x-rx} {y-2}C{x-rx} {y-ry-4} {x+rx} {y-ry-4} {x+rx} {y-2}C{x+rx} {y+ry*.2} {x+rx*.4} {y+ry} {x} {y+ry+1}C{x-rx*.4} {y+ry} {x-rx} {y+ry*.2} {x-rx} {y-2}Z',fill)
    s.ellipse(x-2,y-4,rx*.42,1.1,'#fff',extra=' opacity=".45"')


def mouth(s,x=96,y=128,rx=23,ry=26):
    d=f'M{x-rx} {y}Q{x} {y+9} {x+rx} {y}C{x+rx-3} {y+ry*.8} {x+rx*.42} {y+ry} {x} {y+ry}C{x-rx*.42} {y+ry} {x-rx+3} {y+ry*.8} {x-rx} {y}Z'
    shade=s.linear('mouth',[('0','#261006'),('.52','#5b130d'),('1','#8f201e')])
    s.path(d,shade,'#4f2817',.75)
    s.start_clip(d)
    s.ellipse(x,y+ry-3,rx*.66,ry*.33,s.radial('tongue','#ff9484','#ed4455','#b91930'))
    s.end_clip()


def muzzle(s,p,x=96,y=125,rx=35,ry=31):
    s.ellipse(x,y,rx,ry,p['cream'])
    mouth(s,x,y+1,rx*.63,ry*.7)
    s.ellipse(x-rx*.27,y-6,rx*.34,ry*.29,p['cream'])
    s.ellipse(x+rx*.27,y-6,rx*.34,ry*.29,p['cream'])
    s.line(f'M{x} {y-1}L{x} {y+7}', '#493123',.8)
    nose(s,x,y-8,rx*.29,ry*.2)


def whiskers(s,y=124,span=66):
    for sign in [-1,1]:
        x=96+sign*49
        s.line(f'M{x} {y}Q{96+sign*59} {y-5} {96+sign*(span+12)} {y-4}', '#392d26',1.15)
        s.line(f'M{x} {y+5}Q{96+sign*62} {y+5} {96+sign*(span+8)} {y+11}', '#392d26',1.05)


def round_ears(s,p,base,inner,cx=53,y=47,rx=22,ry=24):
    for x in [cx,192-cx]:
        s.ellipse(x,y,rx,ry,p[base])
        s.ellipse(x,y+1,rx*.67,ry*.67,p[inner])


def face_animal(slug,title):
    s=Drawing(title);p=palette(s)
    if slug=='dog':
        s.ellipse(96,98,65,64,p['orange'])
        for flip in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M66 40C49 29 25 53 16 77C8 97 14 114 31 112C45 109 42 83 50 66C55 55 61 47 66 40Z',p['brown'],extra=flip)
        s.path('M80 40C69 39 62 45 65 61C70 76 91 73 82 97C76 110 61 112 42 111C29 139 57 163 94 163C132 163 155 141 150 116C126 120 111 111 111 97C104 72 126 71 119 48C115 38 97 37 80 40Z',p['cream'])
        eye(s,70,94,8,11);eye(s,122,94,8,11)
        muzzle(s,p,y=128,rx=32,ry=29)
    elif slug in {'cat','fox'}:
        for transform in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M32 88C21 67 19 35 29 19C35 10 61 34 76 59Z',p['brown'] if slug=='fox' else p['gold'],extra=transform)
            s.path('M35 74C28 54 28 31 32 26C43 28 55 45 61 57Z',p['pink'],extra=transform)
        if slug=='fox':
            head='M96 49C64 47 44 69 31 97C24 108 17 113 10 118C27 133 29 154 59 164C85 181 111 180 137 164C167 154 169 133 182 118C175 113 168 108 161 97C148 69 128 47 96 49Z'
            s.path(head,p['orange']);s.start_clip(head)
            s.path('M8 126Q33 115 63 127Q96 141 128 127Q158 115 184 126L192 192H0Z',p['cream']);s.end_clip()
            eye(s,67,108);eye(s,125,108);muzzle(s,p,y=139,rx=30,ry=24)
        else:
            s.ellipse(96,105,73,63,p['gold']);eye(s,67,100);eye(s,125,100)
            mouth(s,y=130,rx=25,ry=26);nose(s,y=119,pink=True);whiskers(s,y=120)
    elif slug in {'mouse','hamster','bear','panda'}:
        base={'mouse':'gray','hamster':'orange','bear':'brown','panda':'dark'}[slug]
        round_ears(s,p,base,'pink' if slug in {'mouse','hamster'} else 'dark',cx=43 if slug in {'mouse','panda'} else 49,y=49 if slug=='mouse' else 40,rx=28 if slug=='mouse' else 24,ry=29 if slug=='mouse' else 25)
        if slug=='panda':
            s.path('M96 31C53 30 20 65 13 117C5 150 38 174 96 175C154 174 187 150 179 117C172 65 139 30 96 31Z',p['white'])
            for x,angle in [(60,25),(132,-25)]:
                s.ellipse(x,97,18,27,p['dark'],f' transform="rotate({angle} {x} 97)"')
                eye(s,x+(-1 if x<96 else 1),95,7.6,11.5)
            mouth(s,y=136,rx=24,ry=27)
            for x in [86,106]:s.ellipse(x,126,13,10,p['white'])
            nose(s,y=119,rx=13,ry=8)
        else:
            fill=p['gray'] if slug=='mouse' else p['orange'] if slug=='hamster' else p['brown']
            s.ellipse(96,107,72 if slug!='mouse' else 64,62,fill)
            if slug=='hamster':
                s.path('M96 43C84 66 95 89 72 106C53 119 33 105 29 119C27 157 59 169 96 170C133 169 165 157 163 119C159 105 139 119 120 106C97 89 108 66 96 43Z',p['cream'])
            eye(s,68,100,8,11);eye(s,124,100,8,11)
            if slug=='bear':muzzle(s,p,y=133,rx=34,ry=29)
            else:
                mouth(s,y=131,rx=24,ry=26);nose(s,y=122,pink=True)
                whiskers(s,y=125,span=62 if slug=='mouse' else 65)
    elif slug=='rabbit':
        for x,angle in [(59,-14),(133,14)]:
            s.ellipse(x,54,17,45,p['gray'],f' transform="rotate({angle} {x} 54)"')
            s.ellipse(x,56,9,33,p['pink'],f' transform="rotate({angle} {x} 54)"')
        s.path('M96 79C64 76 41 96 29 126C17 154 42 179 96 179C150 179 175 154 163 126C151 96 128 76 96 79Z',p['white'])
        eye(s,66,117,8,11);eye(s,126,117,8,11)
        mouth(s,y=146,rx=23,ry=23);nose(s,y=135,pink=True)
        whiskers(s,y=141,span=73)
    elif slug=='koala':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M60 42C47 28 36 24 31 27L36 33C19 30 18 38 22 43C7 43 12 54 17 58C7 63 13 74 20 78C14 87 24 98 34 92C44 97 57 82 62 68Z',p['gray'],extra=trans)
            s.ellipse(38,61,15,22,p['pink'],trans)
        s.ellipse(96,108,62,61,p['gray']);eye(s,68,103,7,10);eye(s,124,103,7,10)
        mouth(s,y=139,rx=21,ry=20)
        s.path('M96 91C84 88 77 107 80 121C84 133 108 133 112 121C115 107 108 88 96 91Z',p['dark'])
        s.ellipse(90,103,3,8,'#fff',extra=' opacity=".15"')
    elif slug=='tiger':
        round_ears(s,p,'dark','gold',cx=45,y=42,rx=24,ry=27)
        for x in [45,147]:s.ellipse(x,42,12,16,p['cream'])
        head='M96 36C65 33 47 53 32 81C20 102 18 125 14 133L20 131Q18 148 27 151L32 147Q30 162 40 163L45 160Q58 176 96 174Q134 176 147 160L152 163Q162 162 160 147L165 151Q174 148 172 131L178 133C174 125 172 102 160 81C145 53 127 33 96 36Z'
        s.path(head,p['gold']);s.start_clip(head)
        s.path('M10 105Q39 107 51 128Q70 137 96 132Q122 137 141 128Q153 107 182 105L192 192H0Z',p['cream'])
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M23 74Q31 98 48 111Q31 108 26 97Z',p['dark'],extra=trans)
            s.path('M19 99Q28 125 50 132Q26 137 22 118Z',p['dark'],extra=trans)
            s.path('M34 127Q40 142 54 148Q38 151 30 138Z',p['dark'],extra=trans)
        s.end_clip()
        for y,width in [(51,29),(65,26),(78,17)]:
            s.path(f'M{96-width} {y+2}Q96 {y-10} {96+width} {y+2}Q96 {y-4} {96-width} {y+2}Z',p['dark'])
        s.path('M93 44Q95 68 92 82L100 82Q98 68 99 44Z',p['dark'])
        eye(s,65,100);eye(s,127,100);mouth(s,y=135,rx=25,ry=26)
        for x in [82,110]:s.ellipse(x,128,17,10,p['cream'])
        nose(s,y=120,pink=True)
    elif slug=='lion':
        points=[]
        for i in range(40):
            a=math.tau*i/40;rad=83 if i%2==0 else 72
            points.append((96+math.sin(a)*rad,98-math.cos(a)*rad))
        d='M'+ 'Q'.join(f'{x:.2f} {y:.2f}' for x,y in points[:1])
        # Round the tufts rather than rasterising their uneven boundaries.
        for i,(x,y) in enumerate(points):
            nxt=points[(i+1)%len(points)];d+=f'Q{x:.2f} {y:.2f} {(x+nxt[0])/2:.2f} {(y+nxt[1])/2:.2f}'
        s.path(d+'Z',p['brown'])
        round_ears(s,p,'gold','brown',cx=55,y=65,rx=18,ry=21)
        s.ellipse(96,113,56,60,p['gold']);eye(s,70,108);eye(s,122,108)
        muzzle(s,p,y=140,rx=33,ry=28)
    elif slug=='cow':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M62 53C42 49 36 33 39 19C45 15 49 39 58 37L74 40Z',p['cream'],extra=trans)
            s.path('M51 65C37 51 15 50 11 62C13 75 29 84 44 79Z',p['dark'],extra=trans)
            s.path('M43 75Q23 78 15 65Q30 62 46 69Z',p['pink'],extra=trans)
        head='M96 37C60 34 46 52 39 84C33 105 28 133 36 149C52 171 140 171 156 149C164 133 159 105 153 84C146 52 132 34 96 37Z'
        s.path(head,p['cream']);s.start_clip(head)
        s.path('M37 33L82 32C62 50 88 72 76 97C70 114 39 111 31 137Z',p['dark']);s.end_clip()
        eye(s,69,97);eye(s,125,97)
        s.ellipse(96,145,60,35,p['pink'])
        for x in [74,118]:s.ellipse(x,132,6,8,s.radial('nostril','#a63842','#861b2c','#671224'))
        mouth(s,y=157,rx=20,ry=17)
    elif slug=='pig':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M64 54C47 23 37 39 16 33C11 33 13 43 14 54C13 78 34 89 55 77Z',p['pink'],extra=trans)
            s.path('M48 56Q34 43 23 43Q20 70 39 73Z',s.radial('ear-pink','#fa9098','#e56179','#b72d49'),extra=trans)
        s.ellipse(96,110,74,65,p['pink']);eye(s,65,102);eye(s,127,102)
        mouth(s,y=144,rx=27,ry=27)
        s.ellipse(96,128,28,21,p['pink'],extra=' stroke="#df6674" stroke-width=".8"')
        for x in [85,107]:s.ellipse(x,129,5,8,s.radial('pig-nostril','#d6455d','#a9183a','#7d0e2a'))
    elif slug=='monkey':
        round_ears(s,p,'orange','brown',cx=29,y=110,rx=22,ry=29)
        for x in [29,163]:s.ellipse(x,110,12,18,p['cream'])
        s.path('M96 39Q93 29 101 27Q108 27 106 34Q119 28 115 39C151 46 160 79 159 115C160 155 131 175 96 175C61 175 32 155 33 115C32 79 41 46 76 41Z',p['brown'])
        s.path('M96 84C80 59 45 81 49 113C42 150 64 170 96 170C128 170 150 150 143 113C147 81 112 59 96 84Z',p['cream'])
        eye(s,72,108);eye(s,120,108);mouth(s,y=137,rx=24,ry=26)
        s.ellipse(96,128,12,7,p['cream'])
        for x in [92,100]:s.ellipse(x,128,2.5,1.7,'#763e21')
    elif slug=='frog':
        s.ellipse(96,127,79,45,p['green'])
        for x in [60,132]:s.ellipse(x,80,29,37,p['green'])
        s.ellipse(96,104,60,39,p['green'])
        for x in [60,132]:
            s.ellipse(x,83,21,25,p['gold']);eye(s,x,84,15,20)
        mouth(s,y=123,rx=51,ry=37)
        for x in [87,105]:s.ellipse(x,116,2.3,1.4,'#3b7011')
    else:
        return None
    return s.finish()


FACE_ANIMALS={'dog','cat','mouse','hamster','rabbit','fox','bear','panda','koala','tiger','lion','cow','pig','frog','monkey'}


def body_animal(slug,title):
    s=Drawing(title);p=palette(s)
    if slug=='chicken':
        s.path('M53 112C29 104 20 136 17 149C15 165 35 168 46 151Z',p['white'])
        s.path('M139 112C163 104 172 136 175 149C177 165 157 168 146 151Z',p['white'])
        s.path('M96 43C64 40 45 73 34 117C24 162 43 181 96 181C149 181 168 162 158 117C147 73 128 40 96 43Z',p['white'])
        for x,y,rx,ry in [(77,40,12,16),(95,31,14,22),(113,43,13,17)]:s.ellipse(x,y,rx,ry,p['red'])
        eye(s,68,91);eye(s,124,91)
        for x in [85,109]:s.ellipse(x,147,13,21,p['red'])
        beak='M74 109Q76 96 96 96Q116 96 118 109L111 130Q96 142 81 130Z'
        s.path(beak,p['gold']);mouth(s,y=111,rx=17,ry=23)
        s.path('M75 108Q96 94 117 108Q97 119 75 108Z',p['gold'])
    elif slug=='penguin':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M47 104C27 111 24 140 14 153C8 174 28 177 43 156Z',p['dark'],extra=trans)
        s.path('M96 25C49 24 33 61 33 107C23 154 38 177 96 179C154 177 169 154 159 107C159 61 143 24 96 25Z',p['dark'])
        s.path('M96 99C85 53 58 50 50 90C42 109 36 129 45 151C55 177 138 177 147 151C156 129 150 109 142 90C134 50 107 53 96 99Z',p['white'])
        eye(s,66,95,7,11);eye(s,126,95,7,11)
        s.path('M76 114Q96 94 116 114Q117 144 96 150Q75 144 76 114Z',p['gold'])
        mouth(s,y=115,rx=16,ry=23)
        s.path('M76 114Q96 100 116 114Q96 123 76 114Z',p['gold'])
    elif slug=='duck':
        s.path('M51 120Q138 132 159 112Q164 102 169 105Q174 116 170 129Q181 135 173 157Q149 182 80 177Q31 175 39 140Z',p['brown'])
        s.ellipse(129,152,33,25,p['cream'],extra=' transform="rotate(-24 129 152)"')
        s.ellipse(113,67,40,45,s.radial('duck-green','#45c563','#08932d','#00511d'))
        s.path('M95 95Q115 106 132 100L128 117Q114 124 95 115Z',s.radial('duck-neck','#29ad42','#097e26','#004b19'))
        s.path('M95 110Q115 122 130 114L128 120Q111 125 93 116Z',p['white'])
        eye(s,110,64,8.5,11)
        s.path('M80 73C62 68 60 86 37 80C20 78 23 92 40 98L65 101Q54 113 57 121Q75 128 96 99Q109 84 80 73Z',p['gold'])
        s.path('M39 92Q62 105 91 92Q79 112 62 117Q59 112 68 103Q48 106 39 92Z',s.linear('bill-interior',[('0','#6e320a'),('1','#a91f15')]))
        s.line('M62 116Q70 119 80 109','#ff9578',2)
        s.ellipse(76,80,2,1.1,'#9b5400')
    elif slug=='owl':
        s.ellipse(96,136,67,46,p['brown'])
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M45 113C19 109 14 133 24 152Q20 169 41 177Q52 166 48 149Z',p['brown'],extra=trans)
        head='M96 29Q73 28 56 34Q34 23 26 15Q17 12 22 26L32 43Q16 33 20 48L32 62C12 79 21 117 47 128Q96 150 145 128C171 117 180 79 160 62L172 48Q176 33 160 43L170 26Q175 12 166 15Q158 23 136 34Q119 28 96 29Z'
        s.path(head,p['brown'])
        for x in [65,127]:
            s.ellipse(x,88,32,39,p['cream'])
            s.ellipse(x,85,21,25,p['gold']);eye(s,x,85,16,21)
        s.path('M96 99C83 98 79 112 84 123L96 137L108 123C113 112 109 98 96 99Z',p['brown'])
        s.ellipse(96,152,42,29,p['cream'])
        for row in range(2):
            for x in ([70,89,108,127] if row==0 else [80,99,118]):
                y=145+row*14
                s.line(f'M{x-7} {y}Q{x} {y+14} {x+7} {y}', '#c29c6b',1.2,.55)
    elif slug=='butterfly':
        wing=s.radial('wing-blue','#54efff','#07bfff','#1261ce',cx='.85',cy='.7',r='.95')
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M96 113C77 65 43 31 25 28C5 22 14 60 18 86C17 109 33 117 58 117C24 117 18 144 24 163C38 186 76 156 96 123Z',p['dark'],extra=trans)
            s.path('M90 108C77 66 44 39 29 39C17 38 25 60 38 69C25 65 29 85 47 92C30 85 34 102 59 106Z',wing,extra=trans)
            s.path('M89 119C66 116 36 129 35 149C37 164 62 147 69 136C63 152 79 142 89 119Z',wing,extra=trans)
            for x,y,r in [(27,35,4.8),(24,48,3.3),(24,64,2.8),(33,158,3.6),(28,148,2.5),(32,134,2.6),(45,163,3)]:s.ellipse(x,y,r,r,p['blue'],trans)
            s.line('M92 111Q53 83 28 52','#08639e',.8,.45)
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M96 97Q90 61 82 42', 'none', '#333a3c',2,extra=trans)
            s.ellipse(81,40,3.5,4,p['dark'],trans)
        s.ellipse(96,120,7,33,p['dark']);s.ellipse(96,94,6.5,8,p['dark'])
    elif slug=='bee':
        for d in ['M80 139Q58 156 62 169Q69 174 77 151Z','M103 149Q86 173 95 180Q105 182 111 156Z','M126 156Q121 176 137 182Q147 182 134 160Z']:
            s.path(d,p['brown'])
        s.ellipse(134,76,24,42,p['ice'],extra=' transform="rotate(36 134 76)"')
        s.line('M112 104Q128 89 147 55','#70b4d0',1.25,.4)
        body='M84 104C126 89 155 113 166 152Q174 169 176 175Q150 181 128 169C91 163 72 136 84 104Z'
        s.path(body,p['gold']);s.start_clip(body)
        for d in ['M108 100Q130 125 109 159L126 172Q155 135 125 102Z','M143 113Q164 146 147 175L169 181Q184 158 158 130Z']:
            s.path(d,p['brown'])
        s.end_clip()
        for d in ['M63 65Q62 35 46 31','M85 63Q91 32 105 28']:
            s.line(d,'#4c2a13',3.5)
        s.ellipse(44,29,8,6,p['brown']);s.ellipse(107,27,8,6,p['brown'])
        s.ellipse(72,98,49,46,p['gold']);eye(s,51,96,7.5,10);eye(s,88,96,7.5,10);mouth(s,72,117,16,20)
    elif slug=='turtle':
        for x,y,rx,ry,angle in [(46,155,13,23,22),(108,154,15,27,-25),(157,153,13,23,-20)]:
            s.ellipse(x,y,rx,ry,p['green'],extra=f' transform="rotate({angle} {x} {y})"')
        shell='M70 118C61 70 86 34 122 34C160 34 176 75 175 119Q129 153 70 118Z'
        s.path(shell,s.radial('shell','#7ca82c','#416e0e','#254900'))
        s.start_clip(shell)
        cells=['M96 37L121 45L122 66L96 77L80 60Z','M122 45L151 42L163 67L141 77L122 66Z','M96 77L122 66L141 77L138 107L112 114L94 99Z','M69 82L96 77L94 99L81 116L66 108Z','M141 77L171 75L182 101L169 124L138 107Z','M112 114L138 107L169 124L148 147L115 141L81 116L94 99Z']
        for d in cells:s.path(d,s.radial('shell-cell','#7a9d2a','#497918','#2d580c'),'#87b342',2.6)
        s.end_clip()
        s.path('M69 118Q122 151 175 119L176 129Q122 163 67 129Z',p['green'])
        s.ellipse(58,110,46,44,p['green']);eye(s,34,108,6,9);eye(s,73,108,6,9);mouth(s,53,129,16,18)
    elif slug=='octopus':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            for d in ['M59 119C41 128 35 124 32 110C26 95 12 108 18 117C21 112 22 123 27 133C35 146 57 147 70 131Z','M68 128C49 153 35 153 20 142C5 135 12 153 26 160C45 169 66 151 78 134Z','M78 125C74 148 73 156 52 165C27 176 52 182 69 170C86 159 91 143 91 128Z']:
                s.path(d,p['red'],extra=trans)
        s.ellipse(96,78,53,54,p['red']);eye(s,72,89,7.5,11);eye(s,120,89,7.5,11);mouth(s,y=109,rx=14,ry=17)
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M82 122C92 150 85 167 71 178C82 192 100 163 96 139L96 122Z',p['red'],extra=trans)
    elif slug=='whale':
        for d in ['M77 65Q76 37 53 36Q39 40 44 50Q66 49 77 65Z','M85 59Q84 28 88 20Q98 11 103 22Q98 35 85 59Z','M89 66Q101 34 118 35Q130 44 116 52Q103 51 89 66Z']:
            s.path(d,p['ice'])
        tail='M135 147C165 150 157 127 163 114C145 110 137 96 145 87Q155 100 167 97Q180 83 183 96C184 110 176 115 171 118C174 151 158 168 135 166Z'
        s.path(tail,p['blue'])
        body='M135 116C133 70 116 60 80 57C39 53 16 84 13 116C5 152 36 178 85 179C121 180 159 159 153 133Z'
        s.path(body,p['blue']);s.start_clip(body)
        s.path('M7 122Q44 127 63 124Q84 150 105 160Q133 163 157 141L183 192H0Z',p['ice'])
        for x in [22,34,46,58,70,82]:s.line(f'M{x} 122Q{x+4} 154 {x+26} 178','#75b1c9',1,.65)
        s.end_clip();eye(s,74,119,7.5,11)
        s.path('M98 141C113 137 131 156 133 172C121 184 99 172 89 154Q86 145 98 141Z',p['blue'])
    else:return None
    return s.finish()


BODY_ANIMALS={'chicken','penguin','duck','owl','butterfly','bee','turtle','octopus','whale'}


def familiar_face(slug,title,gold_defs):
    s=Drawing(title);p=palette(s)
    s.defs.append(gold_defs.replace('id="','id="approved-').replace('url(#','url(#approved-').replace('href="#face"','href="#approved-face"'))
    circle='M96 12C49.6 12 12 49.6 12 96C12 142.4 49.6 180 96 180C142.4 180 180 142.4 180 96C180 49.6 142.4 12 96 12Z'
    s.defs.append(f'<path id="approved-face" d="{circle}"/>')
    # Keep the approved happy-face lighting without extending it over features.
    if slug=='nauseated':
        s.path(circle,s.radial('sick-green','#eef792','#b6da40','#60971c',cx='.46',cy='.3',r='.69'))
    elif slug in {'angry','furious','hot-face'}:
        heat=s.radial('fury','#ffb96b','#f47a29','#db351a') if slug=='furious' else s.linear('heat',[('0','#f73939'),('.23','#ff8e45'),('.62','#ffbf35'),('1','#e0950c')])
        s.path(circle,heat)
    elif slug=='cold-face':
        s.path(circle,s.radial('cold-sphere','#c5f6ff','#43c5ff','#0877d3',cx='.46',cy='.25',r='.72'))
    else:
        s.parts.extend([f'<path d="{circle}" fill="url(#approved-{name})"'+(' mask="url(#approved-sphere-shading)"' if name=='edge-color' else '')+'/>' for name in ['gold','edge-color','top-shine','cheek','right-cheek']])
    if slug=='shocked':
        for x in [62,130]:
            s.ellipse(x,85,20,23,s.radial('eye-white','#fff','#fcfcfc','#a0a6a1'))
            eye(s,x,88,9.5,11)
        s.line('M45 54Q56 38 71 43','#573206',4.4)
        s.line('M121 43Q136 39 148 54','#573206',4.4)
        s.ellipse(96,135,18,27,s.linear('scream-mouth',[('0','#321504'),('.5','#622d0c'),('1','#a95522')]),extra=' stroke="#b97c09" stroke-width=".9"')
        hand=s.radial('scream-hand','#ffe98a','#ffc936','#d89408',cx='.35',cy='.23',r='.78')
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            d='M37 180C19 184 17 175 20 161C22 148 11 130 11 118C10 102 22 96 31 104C48 119 56 145 57 166C58 179 52 182 37 180Z'
            s.parts.append('<g'+trans+'>')
            s.path(d,hand)
            s.line('M25 112Q42 130 44 152','#fff2a6',1.5,.5)
            s.parts.append('</g>')
    elif slug=='mask':
        for x in [64,128]:
            s.path(f'M{x-16} 87C{x-15} 61 {x+15} 61 {x+16} 87Q{x} 70 {x-16} 87Z',s.radial('closed-eye','#674010','#382306','#231605'))
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M43 108Q27 104 14 96L12 103Q26 114 43 118Z',p['ice'],extra=trans)
            s.path('M43 141Q24 141 16 136L18 143Q27 150 45 151Z',p['ice'],extra=trans)
        mask='M48 104Q96 98 144 104Q150 105 150 118L147 151Q139 170 96 170Q53 170 45 151L42 118Q42 105 48 104Z'
        s.path(mask,s.linear('mask-fabric',[('0','#eefcff'),('.2','#c3edf9'),('.66','#9eddf4'),('1','#68b4db')]),'#5ba8cb',.9)
        s.start_clip(mask)
        for y in [117,132,147]:
            s.line(f'M50 {y}Q96 {y+5} 142 {y}','#8bc9e5',2.2,.7)
            s.line(f'M50 {y+2}Q96 {y+6} 142 {y+2}','#eefcff',1.2,.55)
        s.end_clip()
    elif slug=='bandage':
        eye(s,67,106,9,14);eye(s,125,106,9,14)
        s.line('M51 95Q64 91 75 84','#593507',4)
        s.line('M115 76Q128 85 140 88','#593507',4)
        s.path('M73 151Q96 129 119 151Q96 140 73 151Z','#543307')
        band='M13 80C42 48 90 21 128 17Q160 29 178 56C111 57 48 69 13 118Z'
        s.start_clip(circle)
        s.path(band,s.linear('bandage-cloth',[('0','#fafcfc'),('.35','#fff'),('1','#c7ced0')]),'#b3babc',.7)
        s.start_clip(band)
        for d in ['M14 102Q86 46 175 43','M20 117Q91 61 181 55']:
            s.line(d,'#b6bfc2',1.0,.8)
        for i in range(11):
            x=18+i*16;s.line(f'M{x} 30L{x+35} 125','#aab6ba',.2,.12)
        s.end_clip();s.end_clip()
    elif slug in {'party-face','innocent'}:
        for x in [64,128]:
            s.path(f'M{x-16} 98C{x-16} 75 {x+16} 75 {x+16} 98Q{x} 82 {x-16} 98Z','#593308')
        if slug=='innocent':
            s.path('M73 132Q96 143 119 132C111 154 81 154 73 132Z',s.linear('gentle-smile',[('0','#321804'),('1','#6a310a')]))
            halo='M18 34A78 20 0 1 0 174 34A78 20 0 1 0 18 34ZM36 34A60 12 0 1 0 156 34A60 12 0 1 0 36 34Z'
            s.path(halo,s.radial('halo','#a4f4ff','#37c7ef','#087cd0'),extra=' fill-rule="evenodd"')
            s.line('M39 25Q96 10 153 25','#d9ffff',1.2,.7)
        else:
            for d in ['M47 66Q59 54 72 59','M122 60Q135 55 146 66']:
                s.line(d,'#593308',3)
            s.line('M118 123Q140 127 120 134Q140 141 120 146','#593308',3.4)
            hat='M33 72L41 15Q45 9 50 16L78 53Z'
            s.path(hat,p['gold']);s.start_clip(hat)
            purple=s.radial('hat-purple','#d179fb','#9c22e2','#6813a5')
            s.path('M27 29L61 5L70 20L29 53Z',purple)
            s.path('M27 61L77 30L84 42L32 76Z',purple)
            s.end_clip()
            for d,colour in [('M19 89Q13 97 23 103L28 97',p['pink']),('M164 67Q177 61 175 54L169 51',p['pink']),('M23 152Q12 148 15 157L21 165',p['red']),('M153 27Q169 28 166 37L160 39',p['blue']),('M12 135Q18 138 24 131',p['blue'])]:
                s.path(d,'none',colour,6,extra=' stroke-linecap="round"')
            s.path('M128 133Q151 135 173 130L179 141Q151 144 127 139Z',p['blue'])
            s.ellipse(173,134,10,9,p['blue'])
            s.line('M169 136C165 127 180 124 178 134Q176 139 172 134','#8ce5ff',1.6,.8)
    elif slug=='nauseated':
        eye(s,64,102,8.5,12);eye(s,128,102,8.5,12)
        s.line('M48 78Q63 86 77 69','#4d4b06',3.3)
        s.line('M115 69Q129 86 144 78','#4d4b06',3.3)
        s.line('M57 144Q64 130 72 144Q80 158 88 144Q96 130 104 144Q112 158 120 144Q128 130 135 144','#455003',4)
    elif slug=='huff':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.parts.append('<g'+trans+'>')
            s.path('M49 65Q70 62 81 81Q61 75 49 65Z','#5b3206')
            s.path('M51 95Q64 105 80 94Q77 112 62 107Q55 105 51 95Z','#5b3206')
            s.end_clip()
        s.path('M76 129Q96 118 116 129L114 133Q96 126 78 133Z','#5b3206')
        steam='M82 128C81 137 68 143 67 149C74 148 78 155 74 161C78 173 65 180 58 174C50 183 36 176 39 168C28 165 34 151 43 151C38 142 52 139 58 144Z'
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.parts.append('<g'+trans+'>')
            s.path(steam,s.radial('steam','#fff','#eef9fc','#b7d2df'))
            s.ellipse(52,158,12,10,s.radial('steam-puff','#fff','#f7fcfd','#d5e5ed'))
            s.parts.append('</g>')
    elif slug=='grimace':
        eye(s,64,91,8,11);eye(s,128,91,8,11)
        teeth='M63 121Q96 116 129 121C146 124 146 145 129 149Q96 154 63 149C46 145 46 124 63 121Z'
        s.path(teeth,s.radial('teeth','#fff','#faf8f2','#ddd5c6'),'#5b3508',2)
        s.start_clip(teeth)
        s.line('M49 135H143','#a5a19a',.8)
        for x in [68,86,104,122]:s.line(f'M{x} 116V156','#a5a19a',.8)
        s.end_clip()
    elif slug in {'angry','furious','hot-face'}:
        eye(s,64,98,9,13);eye(s,128,98,9,13)
        if slug=='hot-face':
            s.line('M49 76Q64 85 77 68','#673109',3)
            s.line('M115 68Q128 85 143 76','#673109',3)
            s.ellipse(96,135,24,19,s.linear('heat-mouth',[('0','#341005'),('1','#76200a')]))
            tongue='M83 138Q96 133 109 138L110 161C110 186 82 186 82 161Z'
            s.path(tongue,s.radial('hot-tongue','#ff8d9d','#f3416a','#c82248'),'#a62d43',.7)
            s.line('M96 138V157','#b62d48',.7,.5)
            s.path('M158 62C153 72 145 82 146 93C146 113 173 113 173 93C173 82 163 70 158 62Z',p['blue'])
            s.line('M154 79Q149 90 152 93','#ebffff',1.5,.8)
        else:
            s.path('M47 70Q64 74 80 84L77 88Q63 82 49 75Z','#573007')
            s.path('M145 70Q128 74 112 84L115 88Q129 82 143 75Z','#573007')
            s.path('M73 147Q96 122 119 147Q96 138 73 147Z','#573007')
    elif slug=='cold-face':
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.parts.append('<g'+trans+'>')
            s.path('M28 136Q27 156 32 172Q35 176 37 170L40 149Z',p['blue'])
            s.path('M55 162L55 179Q58 186 61 179L65 165Z',p['blue'])
            s.path('M29 82V108M16 95H42M20 86L38 104M20 104L38 86','none','#e9fcff',1.7,extra=' stroke-linecap="round"')
            for d in ['M25 84L29 88L33 84','M25 106L29 102L33 106','M18 91L22 95L18 99','M40 91L36 95L40 99']:
                s.line(d,'#e9fcff',1.1)
            s.parts.append('</g>')
        for x in [66,126]:s.ellipse(x,82,8,12,s.radial('cold-eye','#12589c','#00356d','#00224e'))
        teeth='M63 109H129C145 110 145 137 129 138H63C47 137 47 110 63 109Z'
        s.path(teeth,s.radial('ice-teeth','#fff','#f0f8fa','#bad2e0'),'#176198',2)
        s.start_clip(teeth)
        s.line('M48 123H145','#7c9aad',.8)
        for x in [66,86,106,126]:s.line(f'M{x} 107V140','#7c9aad',.8)
        s.end_clip()
    elif slug=='zip-mouth':
        for x in [64,128]:
            s.ellipse(x,88,9,13,s.radial('zip-eye','#593407','#392004','#201102'))
        metal=s.linear('zip-metal',[('0','#fbfbf5'),('.35','#d2d6d5'),('.7','#8d969a'),('1','#c6cdce')])
        s.line('M52 127H134','#6d767c',8)
        for x in range(54,132,8):
            s.path(f'M{x} 119h5v7h-5Z',metal,'#818b8e',.4)
            s.path(f'M{x+3} 128h5v7h-5Z',metal,'#818b8e',.4)
        s.path('M129 119H143Q146 119 146 122V135Q146 138 143 138H129Z',metal,'#717c81',.8)
        s.line('M138 130L145 145','#7d888c',3)
        s.path('M141 138Q144 135 147 139L159 159Q162 164 158 167L149 172Q145 174 143 169L134 149Q132 144 136 141ZM144 148L151 160L147 163L140 151Z',metal,'#717c81',.8,extra=' fill-rule="evenodd"')
    elif slug in {'money-face','tongue','wink-tongue','zany','delicious'}:
        facial_eye=s.radial('facial-eye','#593407','#392004','#201102',cx='.36',cy='.35',r='.7')
        velvet=s.radial('tongue-velvet','#ff9ab7','#f44176','#ba1848',cx='.46',cy='.55',r='.64')
        if slug=='money-face':
            for x in [64,128]:
                s.line(f'M{x+7} 78C{x+1} 69 {x-11} 75 {x-10} 83C{x-10} 89 {x+9} 86 {x+9} 96C{x+9} 107 {x-8} 107 {x-10} 100','#432406',4.5)
                s.line(f'M{x} 71V109','#432406',2.2)
            s.line('M48 57Q60 49 73 55','#432406',3)
            s.line('M119 55Q132 49 144 57','#432406',3)
            s.path('M50 113Q96 120 142 113C135 155 57 155 50 113Z',s.linear('money-mouth',[('0','#321503'),('1','#753406')]))
            green=s.radial('money-tongue','#7cf332','#34bb15','#137108',cx='.43',cy='.55',r='.65')
            s.path('M73 125Q96 122 119 125L119 157C119 185 73 185 73 157Z',green,'#248408',.6)
            s.line('M104 138C99 132 85 134 86 143C86 151 104 147 105 156C106 165 87 166 85 158M96 131V169','#064e17',3)
        elif slug=='delicious':
            for x in [64,128]:s.path(f'M{x-16} 96C{x-16} 73 {x+16} 73 {x+16} 96Q{x} 80 {x-16} 96Z',facial_eye)
            s.line('M50 121Q68 158 106 148Q125 145 138 122','#532907',4.5)
            s.ellipse(146,134,18,18,velvet,extra=' stroke="#b02449" stroke-width=".65"')
        else:
            if slug=='tongue':
                for x in [64,128]:s.ellipse(x,88,9,13,facial_eye)
            elif slug=='wink-tongue':
                s.path('M47 92Q64 70 81 92Q64 85 47 92Z',facial_eye)
                s.ellipse(128,80,21,25,s.radial('tongue-eye-white','#fff','#fff','#a0a59d',cx='.47',cy='.43',r='.59'))
                s.ellipse(128,81,8.5,10,facial_eye)
            else:
                for x,y,rx,ry in [(64,93,18,23),(127,70,22,27)]:
                    s.ellipse(x,y,rx,ry,s.radial('tongue-eye-white','#fff','#fff','#a0a59d',cx='.47',cy='.43',r='.59'))
                    s.ellipse(x,y+2,7.7,9,facial_eye)
            if slug=='zany':s.parts.append('<g transform="rotate(-14 96 135)">')
            s.path('M56 121Q96 127 136 121C132 154 60 154 56 121Z',s.linear('tongue-mouth',[('0','#321503'),('1','#6b3008')]))
            if slug=='zany':s.path('M61 125Q96 130 131 125L127 132Q96 139 65 132Z',p['white'])
            s.path('M74 129Q96 125 118 129L118 158C118 186 74 186 74 158Z',velvet,'#b5294e',.6)
            s.line('M96 129V148','#d13760',.7,.55)
            if slug=='zany':s.parts.append('</g>')
    else:return None
    return s.finish()


def rainbow(title):
    s=Drawing(title);p=palette(s)
    colours=[('#ff7271','#f73243','#c92330'),('#ffac3d','#ff8624','#df6015'),('#ffe878','#ffd733','#e1b409'),('#91de59','#52b638','#28952a'),('#57d9f3','#22b6de','#0689bf'),('#7c7cfa','#4e55e7','#343ab1'),('#b289ff','#8354e3','#5a30a7')]
    for i,(light,middle,dark) in enumerate(colours):
        radius=80-i*9
        s.path(f'M{96-radius} 142A{radius} {radius} 0 0 1 {96+radius} 142','none',s.radial(f'rainbow-{i}',light,middle,dark,cx='.35',cy='.18',r='1'),10)
    cloud='M17 155C6 151 8 133 17 129C22 118 35 116 42 123C54 114 69 122 70 133C83 135 85 154 72 160C64 168 53 166 47 163C37 170 25 165 22 160Z'
    for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
        s.parts.append('<g'+trans+'>')
        s.path(cloud,s.radial('cloud','#ffffff','#edf5f8','#a8bdcb'))
        s.start_clip(cloud)
        for x,y,rx,ry in [(25,141,15,19),(44,138,18,22),(66,146,16,17)]:
            s.ellipse(x,y,rx,ry,s.radial('cloud-puff','#fff','#eef5f8','#bdced8'))
        s.end_clip()
        s.line('M20 151Q19 142 25 137','#fff',1.1,.55)
        s.parts.append('</g>')
    return s.finish()


def beer(title):
    s=Drawing(title);p=palette(s)
    glass=s.linear('glass',[('0','#cbd0d2'),('.14','#fff'),('.28','#a5abad'),('.5','#e5e9ec'),('.7','#a6abad'),('.91','#fff'),('1','#919498')],x2='1',y2='0')
    s.path('M137 66C170 57 178 73 178 104L178 131C176 153 163 161 138 159L137 145C157 146 164 142 165 130L165 96C165 79 159 77 139 80Z',glass,'#8b9296',.8)
    s.path('M43 51L139 51L142 168Q138 184 94 184Q51 183 40 175Z',glass,'#969c9d',.7)
    drink='M49 64L132 64L133 164Q91 175 49 163Z'
    s.path(drink,s.linear('amber',[('0','#d98500'),('.25','#f9b600'),('.5','#ffd72d'),('.75','#f6ad00'),('1','#c67500')],x2='1',y2='0'))
    s.start_clip(drink)
    rng=random.Random(321)
    bubble=s.radial('bubble','#fff5b0','#ffdf50','#d9930a')
    for i in range(68):
        x=rng.uniform(68,125);y=rng.uniform(78,162);r=rng.uniform(.5,1.7)
        s.ellipse(round(x,2),round(y,2),round(r,2),round(r,2),bubble,extra=' opacity=".7"')
        s.ellipse(round(x-r*.25,2),round(y-r*.3,2),round(r*.32,2),round(r*.32,2),'#fff8c9',extra=' opacity=".72"')
    s.path('M54 65L67 65L66 166L53 163Z','#fff9cc',extra=' opacity=".58"')
    s.path('M124 66L129 65L130 163L125 164Z','#fff',extra=' opacity=".27"')
    s.end_clip()
    s.line('M45 169Q91 184 137 170','#fff',2.2,.8)
    foam='M41 68C27 65 29 45 39 39C37 27 59 22 67 26C72 12 91 15 99 20C111 13 126 18 131 25C147 21 157 31 155 44C161 55 154 70 145 74C137 84 125 77 123 68Q115 78 103 70Q91 78 81 72C72 71 78 88 66 94C52 100 46 86 47 76Z'
    s.path(foam,s.radial('foam','#fffef3','#f8edd5','#dbc3a2'), '#ddc8a7',.65)
    for x,y,rx,ry in [(46,44,7,5),(66,35,9,7),(86,31,7,5),(107,35,9,6),(130,41,8,7),(143,54,6,5),(64,68,6,7),(89,57,5,3),(115,56,6,5)]:
        s.ellipse(x,y,rx,ry,s.radial('foam-puff','#fffef7','#f6ead1','#e3d2b2'),extra=' opacity=".62"')
    return s.finish()


FAMILIAR_FACES={'shocked','mask','bandage','party-face','innocent','nauseated','huff','grimace','angry','furious','hot-face','cold-face','money-face','tongue','wink-tongue','zany','delicious','zip-mouth'}


def donkey(title):
    s=Drawing(title);p=palette(s)
    hoof=s.radial('hoof','#73717a','#393740','#18171f')
    s.line('M50 128Q22 134 29 111','#da7608',5)
    s.path('M29 116Q15 107 26 92Q25 101 31 97Q42 108 29 116Z',p['dark'])
    for d in ['M57 137Q48 157 39 173L42 179L57 178L72 151Z','M104 142L96 171L100 179L113 177L119 147Z']:
        s.path(d,p['orange'])
    for x,y in [(48,177),(106,176)]:s.ellipse(x,y,11,5,hoof)
    s.ellipse(86,132,45,30,p['orange'])
    s.path('M91 137C98 113 96 94 106 79L127 75Q142 96 127 137L118 151Z',p['orange'])
    s.path('M102 83Q87 99 91 115Q91 122 96 125L96 144Q106 140 106 124L112 104Z',p['dark'])
    for d in ['M60 139L66 166L60 179L72 182L79 172L74 141Z','M117 131L122 161L128 176L143 176L137 154L137 133Z']:
        s.path(d,p['orange'])
    for x,y in [(68,179),(137,175)]:s.ellipse(x,y,11,5,hoof)
    for x,y,angle in [(111,40,-25),(151,38,14)]:
        s.ellipse(x,y,12,31,p['orange'],extra=f' transform="rotate({angle} {x} {y})"')
        s.ellipse(x,y-1,6.6,24,p['pink'],extra=f' transform="rotate({angle} {x} {y})"')
    s.ellipse(130,86,24,33,p['orange'],extra=' transform="rotate(-9 130 86)"')
    s.path('M109 65Q106 54 117 53Q114 41 125 50Q129 39 134 52Q147 48 141 68Q132 57 129 69Q122 54 117 69Z',p['dark'])
    for x,y in [(120,84),(145,83)]:
        s.ellipse(x,y,7,10,p['white']);eye(s,x+1,y+1,5,7.5)
    s.line('M113 72Q120 66 126 72','#673510',1.5)
    s.line('M141 71Q146 67 150 72','#673510',1.2)
    s.ellipse(145,107,23,16,p['cream'],extra=' transform="rotate(-5 145 107)"')
    for x,y,angle in [(135,105,-30),(153,102,20)]:s.ellipse(x,y,2.6,3.1,'#7b3a1c',extra=f' transform="rotate({angle} {x} {y})"')
    s.line('M139 116Q148 121 157 113','#9b5527',1.0)
    return s.finish()


def spider(title):
    s=Drawing(title);p=palette(s);rng=random.Random(8821)
    fur=s.radial('fur','#736353','#3b332e','#191a1d',cx='.32',cy='.16',r='.88')
    legshade=s.linear('leg-shade',[('0','#9b8a75'),('.25','#4b4138'),('.66','#312b26'),('1','#1c1c1d')],x2='.7',y2='1')

    def add_hairs(batches):
        # One path per brush, retaining every strand. Quantising brush width
        # and opacity is bounded at .025 units and .025 respectively.
        for (colour,width,opacity),paths in batches.items():
            s.parts.append(f'<path d="{"".join(paths)}" fill="none" stroke="{colour}" stroke-width="{width}" opacity="{opacity}" stroke-linecap="round"/>')

    def hair(batches,path,colour,width,opacity):
        key=(colour,round(round(width/.05)*.05,2),round(round(opacity/.05)*.05,2))
        batches.setdefault(key,[]).append(path)

    def hairs_on_curve(points,n,width):
        batches={}
        for i in range(n):
            t=rng.uniform(.03,.97);a=1-t
            x=a**3*points[0][0]+3*a*a*t*points[1][0]+3*a*t*t*points[2][0]+t**3*points[3][0]
            y=a**3*points[0][1]+3*a*a*t*points[1][1]+3*a*t*t*points[2][1]+t**3*points[3][1]
            dx=3*a*a*(points[1][0]-points[0][0])+6*a*t*(points[2][0]-points[1][0])+3*t*t*(points[3][0]-points[2][0])
            dy=3*a*a*(points[1][1]-points[0][1])+6*a*t*(points[2][1]-points[1][1])+3*t*t*(points[3][1]-points[2][1])
            length=max(math.hypot(dx,dy),.1);nx,ny=-dy/length,dx/length
            offset=rng.uniform(-width/2,width/2);x+=nx*offset;y+=ny*offset
            direction=-1 if offset<0 else 1
            reach=rng.uniform(1.3,3.6)*direction
            colour=rng.choice(['#b7a28b','#7b6d5e','#dcc9ae','#4e4740'])
            hair(batches,f'M{x:.2f} {y:.2f}q{nx*reach*.7:.2f} {ny*reach*.7:.2f} {nx*reach+dx/length*.8:.2f} {ny*reach+dy/length*.8:.2f}',colour,round(rng.uniform(.13,.28),2),round(rng.uniform(.3,.62),2))
        add_hairs(batches)

    legs=[[(58,80),(34,69),(23,103),(13,143)],[(55,89),(32,87),(37,113),(31,155)],[(67,101),(46,107),(53,138),(56,161)],[(56,72),(37,69),(31,77),(28,99)]]
    for points in legs:
        for mirrored in [False,True]:
            points2=[(192-x if mirrored else x,y) for x,y in points]
            d='M'+' '.join(str(x) for x in points2[0])+'C'+' '.join(str(x) for pair in points2[1:] for x in pair)
            s.line(d,'#232120',11)
            s.line(d,legshade,9.4)
            hairs_on_curve(points2,270,9)
    s.ellipse(96,72,47,31,fur)
    s.ellipse(96,82,45,29,fur)
    batches={}
    for i in range(4000):
        angle=rng.uniform(0,math.tau);r=math.sqrt(rng.uniform(.05,1.02))
        x=96+math.cos(angle)*46*r;y=76+math.sin(angle)*31*r
        reach=rng.uniform(1.1,3.7)
        dx=math.cos(angle)*reach;dy=math.sin(angle)*reach
        colour=rng.choice(['#cec0ac','#948677','#b4a799','#63594f','#403b36'])
        hair(batches,f'M{x:.2f} {y:.2f}q{dx*.6:.2f} {dy*.55:.2f} {dx:.2f} {dy+1:.2f}',colour,round(rng.uniform(.12,.28),2),round(rng.uniform(.3,.7),2))
    add_hairs(batches)
    for x in [86,106]:
        s.ellipse(x,108,9,17,s.radial('iridescent','#74f98c','#07953b','#063932',cx='.3',cy='.2',r='.9'))
        s.ellipse(x-2,103,2.2,6,'#9cdba8',extra=' opacity=".34"')
    for x,y,rx in [(80,82,16),(113,79,15.7),(58,87,8),(138,75,7),(148,70,4)]:
        s.ellipse(x,y,rx+1.8,rx+1.6,s.radial('eye-rim','#e3cda8','#9e8668','#3b3024'))
        s.ellipse(x,y,rx,rx,s.radial('spider-eye','#5b554d','#151617','#010203',cx='.3',cy='.18',r='.78'))
        s.ellipse(x,y-rx*.38,rx*.77,rx*.45,s.radial('spider-eye-gloss','#90a4b8','#536778','#14202c'),extra=' opacity=".32"')
        s.ellipse(x-rx*.3,y-rx*.4,rx*.25,rx*.23,'#fff',extra=' opacity=".95"')
        s.ellipse(x+rx*.37,y-rx*.15,rx*.12,rx*.11,'#d8edff',extra=' opacity=".8"')
        s.path(f'M{x-rx*.75:.2f} {y+rx*.3:.2f}Q{x:.2f} {y+rx*.65:.2f} {x+rx*.7:.2f} {y+rx*.3:.2f}','none','#a98145',.8,extra=' opacity=".4"')
    for points in [[(73,108),(78,119),(81,124),(86,127)],[(120,106),(115,117),(111,121),(109,126)]]:
        d='M'+' '.join(str(x) for x in points[0])+'C'+' '.join(str(x) for pair in points[1:] for x in pair)
        s.line(d,legshade,14);hairs_on_curve(points,130,13)
    return s.finish()


EXTRA_ANIMALS={'crypto-donkey','jumping-spider'}
NATURE_DETAILS={'sunflower','rose','sun','moon','star'}
DEVICE_DETAILS={'phone','laptop','gamepad','football'}
CLEAN_SLUGS=FACE_ANIMALS | BODY_ANIMALS | EXTRA_ANIMALS | FAMILIAR_FACES | NATURE_DETAILS | DEVICE_DETAILS | {'rainbow','beer'}


def device_detail(slug,title):
    s=Drawing(title);p=palette(s)
    metal=s.linear('device-metal',[('0','#777c88'),('.14','#ecedf3'),('.28','#808696'),('.55','#aeb4c2'),('.78','#f2f3f7'),('1','#626877')],x2='1',y2='1')
    if slug=='football':
        sphere='M96 13A83 83 0 1 0 96 179A83 83 0 1 0 96 13Z'
        s.path(sphere,s.radial('ball-white','#fff','#f4f4f2','#b0b3b6'))
        s.start_clip(sphere)
        for d in ['M96 66Q95 47 96 26','M122 84Q138 76 157 66','M112 114Q128 131 144 150','M80 114Q63 131 48 150','M70 84Q49 73 33 63','M33 63Q22 98 28 123','M157 66Q173 98 166 126','M48 150Q91 170 144 150']:
            s.line(d,'#a4a8a7',.7,.8)
        for d in ['M96 64L123 84L113 114H80L69 84Z','M78 7L114 7L125 22L111 34H81L66 22Z','M0 52L22 54L39 71L29 100L0 102Z','M167 54L192 54L192 101L165 101L155 73Z','M20 142L48 137L66 158L55 183H17Z','M151 137L176 146L178 186H139L128 159Z']:
            s.path(d,p['dark'], '#424648',.6)
        s.end_clip()
    elif slug=='gamepad':
        body='M60 49Q41 35 28 52C18 74 13 111 9 140C6 166 24 172 39 157L61 130Q76 128 85 135Q96 142 107 135Q116 128 131 130L153 157C168 172 186 166 183 140C179 111 174 74 164 52Q151 35 132 49Q96 58 60 49Z'
        s.path(body,s.radial('controller-body','#676973','#393c44','#171b24'), '#1c2028',.75)
        cross='M48 69H60Q63 69 63 72V80H71Q75 80 75 84V92Q75 96 71 96H63V104Q63 108 59 108H50Q46 108 46 104V96H38Q34 96 34 92V84Q34 80 38 80H46V72Q46 69 48 69Z'
        s.path(cross,s.radial('dpad','#7b7f87','#4a4e57','#2b303a'),'#191d25',.8)
        for x,y,fill in [(139,74,p['gold']),(123,91,p['blue']),(155,91,p['red']),(139,108,p['green'])]:
            s.ellipse(x,y,7.7,7.7,fill)
        for x in [76,116]:
            s.ellipse(x,124,12,11,s.radial('joystick-base','#4a4c57','#282c34','#141922'))
            s.ellipse(x,121,9,8,s.radial('joystick','#858792','#51535d','#2d323b'))
        s.line('M89 78H96M101 78H108','#6a6d78',1.5)
    elif slug=='phone':
        s.path('M62 11H130Q147 11 147 29V165Q147 183 130 183H62Q45 183 45 165V29Q45 11 62 11Z',metal)
        s.path('M63 16H129Q141 16 141 30V165Q141 178 129 178H63Q51 178 51 165V30Q51 16 63 16Z',s.radial('phone-screen','#273148','#101b32','#070c1b'))
        s.line('M84 25H108','#536078',2.5)
        s.ellipse(96,170,4.5,4.5,'#0a1020',extra=' stroke="#647086" stroke-width=".8"')
        colours=[p['gold'],p['green'],p['blue'],p['blue'],p['orange'],p['pink'],p['gold'],p['blue'],p['gold'],p['blue'],p['white'],s.radial('violet-app','#dbb3ff','#a172dd','#7250a6')]
        for i,fill in enumerate(colours):
            x=67+i%3*29;y=49+i//3*29;r=9
            s.path(f'M{x-r+4} {y-r}H{x+r-4}Q{x+r} {y-r} {x+r} {y-r+4}V{y+r-4}Q{x+r} {y+r} {x+r-4} {y+r}H{x-r+4}Q{x-r} {y+r} {x-r} {y+r-4}V{y-r+4}Q{x-r} {y-r} {x-r+4} {y-r}Z',fill)
        s.line('M55 29V162','#d6e8ff',.65,.35)
    else:
        s.path('M43 28H149Q160 28 160 41L158 121L181 159Q188 175 171 178H21Q5 175 12 159L34 121L32 41Q32 28 43 28Z',metal,'#677286',.65)
        s.path('M45 34H147Q154 34 154 44V111Q154 119 146 119H46Q38 119 38 111V44Q38 34 45 34Z',p['dark'])
        screen='M49 41H143Q148 41 148 47V106Q148 112 143 112H49Q44 112 44 106V47Q44 41 49 41Z'
        s.path(screen,s.linear('laptop-display',[('0','#38a4ff'),('.48','#086eff'),('1','#043bad')],x2='1',y2='1'))
        s.path('M44 43H101L45 94Z','#b4ddff',extra=' opacity=".08"')
        s.ellipse(96,32,1,1,'#d4e9ff')
        s.path('M43 128H149L162 152Q96 158 30 152Z',p['dark'])
        key=s.linear('keycap',[('0','#7d8392'),('.3','#434b5a'),('1','#242b3a')])
        for row in range(3):
            y=132+row*5.5
            for col in range(11):
                x=46+col*9.1-row*2
                s.path(f'M{x:.2f} {y:.2f}h6.6l1 3.2h-8.3Z',key)
        s.path('M79 151H115L117 153H77Z',key)
        s.path('M78 159H115Q119 159 119 162L121 168H73L74 162Q74 159 78 159Z',metal,'#818b9c',.45)
        s.line('M21 174Q96 178 171 174','#e5e9f0',.8,.75)
    return s.finish()


def nature_detail(slug,title):
    s=Drawing(title);p=palette(s)
    if slug=='sunflower':
        s.line('M96 113L96 182','#397809',7)
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M95 169C80 139 55 139 35 147C49 169 70 175 95 169Z',p['green'],extra=trans)
            s.line('M43 151Q66 153 87 166','#729a25',1,.6)
        for i in range(12):
            angle=i*30;theta=math.radians(angle);x=96+math.sin(theta)*42;y=79-math.cos(theta)*42
            s.ellipse(round(x,2),round(y,2),10,27,p['gold'],extra=f' transform="rotate({angle} {x:.2f} {y:.2f})"')
        s.ellipse(96,79,34,34,p['brown']);s.ellipse(96,79,25,25,s.radial('seeds','#8f5426','#653916','#3c210d'))
        for i in range(160):
            theta=i*2.39996;r=math.sqrt(i/160)*23;x=96+math.cos(theta)*r;y=79+math.sin(theta)*r
            s.ellipse(round(x,2),round(y,2),1.25,1.6,s.radial('seed','#b0743c','#7a461f','#4f2a10'))
    elif slug=='rose':
        s.path('M88 128Q99 151 89 178Q86 184 93 184Q108 153 103 129Z',p['green'])
        for trans in ['', ' transform="translate(192 0) scale(-1 1)"']:
            s.path('M96 157Q76 130 38 132Q48 167 85 165Z',p['green'],extra=trans)
            s.line('M47 139Q67 145 86 158','#6c9c20',1,.55)
        petal=s.radial('rose-petal','#ff7b89','#ed233f','#a20423',cx='.28',cy='.17',r='.93')
        s.ellipse(95,49,29,25,petal)
        s.ellipse(59,65,27,30,petal);s.ellipse(131,65,28,29,petal)
        s.path('M51 82C28 73 19 76 29 93C45 108 41 128 62 142Q92 156 122 142C147 127 145 107 164 91C177 77 158 69 141 80Q99 107 51 82Z',petal)
        s.path('M57 53C50 79 81 103 128 107C145 98 151 65 134 52Q110 96 57 53Z',p['red'])
        s.path('M47 77C53 125 71 152 91 146C92 116 85 108 47 77Z',petal)
        s.path('M144 80C144 123 123 148 94 146C93 109 106 101 144 80Z',p['red'])
        s.ellipse(96,72,25,18,petal)
        s.path('M73 68C79 48 114 50 119 68C123 90 76 92 73 68Z',p['red'])
        s.path('M80 67C89 58 113 60 111 71Q91 87 80 67Z',petal)
        s.path('M87 66Q104 61 106 70Q95 77 89 71Q100 73 101 69Q96 65 87 66Z',s.radial('rose-fold','#f8576d','#ca1438','#740e22'))
    elif slug=='sun':
        for i in range(8):
            a=i*math.tau/8;points=[(96+math.sin(a-.17)*66,98-math.cos(a-.17)*66),(96+math.sin(a)*87,98-math.cos(a)*87),(96+math.sin(a+.17)*66,98-math.cos(a+.17)*66)]
            d='M'+'L'.join(f'{x:.2f} {y:.2f}' for x,y in points)+'Z';s.path(d,p['gold'],p['gold'],3)
        s.ellipse(96,98,56,56,p['gold']);eye(s,73,103,6.5,9.5);eye(s,119,103,6.5,9.5);mouth(s,y=123,rx=17,ry=14)
    elif slug=='moon':
        s.path('M70 16C130 13 175 57 178 103C181 145 147 178 99 178C58 180 27 162 12 133C9 123 19 121 26 128C57 151 96 127 99 86C102 53 81 30 70 24Q62 17 70 16Z',p['gold'])
        for x in [122,151]:s.line(f'M{x-5} 116Q{x} 123 {x+5} 116','#4f3008',2.8)
        s.path('M121 136Q136 146 151 136Q147 151 136 151Q125 151 121 136Z','#50300a')
    elif slug=='star':
        points=[(96+math.sin(i*math.pi/5)*(85 if i%2==0 else 39),99-math.cos(i*math.pi/5)*(85 if i%2==0 else 39)) for i in range(10)]
        d=''
        for i,point in enumerate(points):
            a=points[(i-1)%10];b=points[(i+1)%10];before=[point[j]*.85+a[j]*.15 for j in range(2)];after=[point[j]*.85+b[j]*.15 for j in range(2)]
            d+=('M' if i==0 else 'L')+' '.join(f'{x:.2f}' for x in before)+'Q'+' '.join(f'{x:.2f}' for x in [*point,*after])
        s.path(d+'Z',p['gold']);eye(s,73,106,6.5,10);eye(s,119,106,6.5,10);mouth(s,y=125,rx=19,ry=15)
    return s.finish()


def rebuild(slug,title,gold_defs):
    if slug in FACE_ANIMALS:return face_animal(slug,title)
    if slug in BODY_ANIMALS:return body_animal(slug,title)
    if slug in FAMILIAR_FACES:return familiar_face(slug,title,gold_defs)
    if slug in NATURE_DETAILS:return nature_detail(slug,title)
    if slug in DEVICE_DETAILS:return device_detail(slug,title)
    if slug=='rainbow':return rainbow(title)
    if slug=='beer':return beer(title)
    if slug=='crypto-donkey':return donkey(title)
    if slug=='jumping-spider':return spider(title)
    raise ValueError(slug)
