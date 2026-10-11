"""Small, deliberately drawn SVG masters for familiar hands, food and objects.

The checked-in PNGs provide proportions, colours and component references.
These are reconstructions, with smooth cubic contours and shaded materials;
no sampled colour tiles, raster embedding, tracing API or image generation.
"""
import math
import random
from clean_vectors import Drawing as BaseDrawing, palette, beer


class Drawing(BaseDrawing):
    """A shallow, shaded bevel follows each material's actual outline."""
    def __init__(self, title):
        super().__init__(title)
        self.defs = [d.replace('stop-opacity=".56"', 'stop-opacity=".30"') for d in self.defs]
        self.defs.append('<filter id="material-depth" x="-8%" y="-8%" width="116%" height="116%" color-interpolation-filters="sRGB"><feGaussianBlur in="SourceAlpha" stdDeviation="1.15" result="height"/><feSpecularLighting in="height" surfaceScale="3" specularConstant=".65" specularExponent="20" lighting-color="#fff" result="gloss"><feDistantLight azimuth="225" elevation="45"/></feSpecularLighting><feComposite in="gloss" in2="SourceAlpha" operator="in" result="rim"/><feComposite in="SourceGraphic" in2="rim" operator="arithmetic" k2="1" k3=".65" result="lit"/><feComposite in="lit" in2="SourceAlpha" operator="in"/></filter>')

    def volume(self, element, fill):
        if fill.startswith('url(') and not any(key in fill for key in ['eye', 'nose', 'mouth', 'tongue', 'nostril']):
            self.parts[-1] = self.parts[-1].replace('/>', ' filter="url(#material-depth)"/>')
            super().volume(element, fill)

HAND_SLUGS = {'thumbs-up', 'thumbs-down', 'wave', 'clap', 'thanks', 'peace'}
FOOD_SLUGS = {'apple', 'banana', 'strawberry', 'watermelon', 'lemon', 'avocado',
              'pizza', 'burger', 'fries', 'taco', 'popcorn', 'cake', 'doughnut',
              'cookie', 'ice-cream', 'coffee', 'beer', 'cheers'}
OBJECT_SLUGS = {'gift', 'idea', 'key', 'lock', 'rocket', 'camera', 'trophy', 'poop'}
SYMBOL_SLUGS = {'heart', 'broken-heart', 'fire', 'celebrate', 'yes', 'no', 'bitcoin'}


def supports(slug):
    return slug.split('-tone')[0] in HAND_SLUGS or slug in FOOD_SLUGS | OBJECT_SLUGS | SYMBOL_SLUGS


def glossy(s, key, light, middle, dark, cx='.34', cy='.22', r='.88'):
    return s.radial(key, light, middle, dark, cx, cy, r)


def oval(s, x, y, rx, ry, fill, angle=0, extra=''):
    s.ellipse(x, y, rx, ry, fill, extra=(f' transform="rotate({angle} {x} {y})"' if angle else '') + extra)


def rounded(s, x, y, w, h, radius, fill, extra=''):
    s.path(f'M{x+radius} {y}H{x+w-radius}Q{x+w} {y} {x+w} {y+radius}V{y+h-radius}Q{x+w} {y+h} {x+w-radius} {y+h}H{x+radius}Q{x} {y+h} {x} {y+h-radius}V{y+radius}Q{x} {y} {x+radius} {y}Z', fill, extra=extra)


def hands(slug, title):
    s = Drawing(title)
    base, _, modifier = slug.partition('-tone')
    tone = int(modifier) if modifier else 0
    shades = [('#fff4a0', '#ffd23b', '#c78208'), ('#fff0de', '#f5c69f', '#ab6c42'),
              ('#ffe3bb', '#e9aa73', '#96532d'), ('#dca777', '#b47648', '#633618'),
              ('#b47c53', '#875434', '#42200f'), ('#986b50', '#66402b', '#2c160e')]
    light, middle, dark = shades[tone]
    # Coloured highlights preserve the human tone instead of washing dark
    # skin towards grey with the generic white material highlight.
    s.defs = [d.replace('stop-color="#fff"', f'stop-color="{light}"') if 'id="volume-shine"' in d else d for d in s.defs]
    inverted = base == 'thumbs-down'
    if inverted:
        s.defs = [d.replace('cy=".13"', 'cy=".87"').replace('cy=".45"', 'cy=".55"').replace('azimuth="225"', 'azimuth="135"') for d in s.defs]
    skin = glossy(s, 'hand-skin', light, middle, dark, '.35', '.76' if inverted else '.24', '.94')
    stops = [('0', dark), ('.36', middle), ('.62', light), ('.86', middle), ('1', dark)] if inverted else [('0', dark), ('.14', middle), ('.38', light), ('.64', middle), ('1', dark)]
    finger = s.linear('finger-skin', stops)
    crease = dark
    motion = glossy(s, 'motion-blue', '#68dbff', '#099eea', '#0861b1')
    if base in {'thumbs-up', 'thumbs-down'}:
        if base == 'thumbs-down':
            s.parts.append('<g transform="translate(0 192) scale(1 -1)">')
        oval(s, 48, 133, 26, 39, skin, -7)
        palm = 'M50 116C57 102 76 88 81 65C88 46 82 31 84 22C87 6 109 10 116 26C125 44 119 63 114 77C110 87 111 95 121 97L151 98Q166 98 169 110L163 158Q158 179 138 181H104C72 181 60 163 53 148C48 138 45 125 50 116Z'
        s.path(palm, skin)
        for x, y, w, h in [(111, 97, 61, 28), (110, 123, 61, 26), (111, 147, 55, 24), (112, 169, 44, 14)]:
            rounded(s, x, y, w, h, min(12, h / 2), finger)
        s.line('M107 106C102 125 101 151 107 174', crease, .85, .3)
        s.line('M89 25C94 17 105 20 107 28', light, 1.4, .6)
        if base == 'thumbs-down':
            s.parts.append('</g>')
    elif base == 'wave':
        palm = 'M57 138L21 105C6 91 21 77 33 87L58 108L26 65C15 49 31 38 43 51L75 89L44 40C34 23 53 12 63 28L96 82L74 27C66 9 86 5 95 23L122 83C123 66 124 48 130 43C143 31 158 39 156 54L151 82C152 102 164 123 158 143C152 171 132 184 105 181C88 179 71 160 57 138Z'
        s.path(palm, skin)
        for d in ['M58 108L44 93', 'M75 89L60 68', 'M96 82L83 61', 'M121 86Q120 105 111 119']:
            s.line(d, crease, 1.1, .34)
        s.line('M144 45Q140 46 139 55', light, 1.4, .5)
        for d in ['M12 137Q22 157 42 162', 'M9 149Q21 174 43 180']:
            s.line(d, motion, 5)
            s.line(d, '#91e5ff', .75, .5)
    elif base == 'clap':
        rear = 'M67 155C43 144 29 124 17 110C6 99 14 85 25 90L18 80C8 67 20 58 32 67L18 56C8 41 22 31 35 42L82 83L73 62C68 48 86 43 93 57L114 97L143 142L128 169Q101 174 67 155Z'
        s.path(rear, skin)
        for d in ['M25 91L52 115', 'M32 68L61 93', 'M45 53L71 78']:
            s.line(d, crease, .9, .34)
        front = 'M123 178L110 160C87 156 69 135 55 119L42 102C31 88 41 75 54 84L44 72C34 57 45 46 58 58L89 90L55 51C42 37 55 25 68 38L109 76L72 34C61 18 77 7 90 21L124 56L119 43C113 27 130 19 139 33C151 51 162 72 164 94L164 119Q183 132 175 146Q153 176 139 181Q130 185 123 178Z'
        s.path(front, skin)
        for d in ['M56 84L76 105', 'M69 67L91 88', 'M89 49L110 70', 'M126 56Q135 70 137 83']:
            s.line(d, crease, 1, .35)
        s.path('M132 11Q130 8 139 9L147 12Q152 14 149 20L134 36Q130 38 130 33Z', glossy(s, 'applause-flash', '#fff297', '#ffc116', '#fa8800'))
    elif base == 'thanks':
        cuff = glossy(s, 'cuff-blue', '#67b8ff', '#0874f1', '#0645a5')
        for reflected in [False, True]:
            if reflected:
                s.parts.append('<g transform="translate(192 0) scale(-1 1)">')
            s.path('M16 151Q26 143 47 132L90 154L82 181H18Q11 181 11 173V160Q11 154 16 151Z', cuff)
            palm = 'M44 133C62 110 69 73 76 29C77 10 90 5 94 19L94 145L81 162Q60 163 44 143Z'
            s.path(palm, skin)
            s.path('M89 16Q84 17 84 29L79 80Q76 106 72 122', 'none', light, 2, extra=' opacity=".45" stroke-linecap="round"')
            s.line('M47 137Q59 153 78 160', '#95ccff', 1.2, .8)
            if reflected:
                s.parts.append('</g>')
        s.line('M96 24V146', crease, .9, .5)
    else:
        palm = 'M50 110C49 95 58 88 70 94L52 33C46 14 63 6 73 18L93 77L111 21C117 3 139 10 136 28L120 98C130 119 142 140 130 162C121 181 98 186 74 180C49 174 42 151 45 132Z'
        s.path(palm, skin)
        oval(s, 57, 122, 14, 23, finger, -20)
        oval(s, 76, 105, 15, 24, finger, -21)
        s.path('M84 104C108 99 126 109 131 127C136 143 121 155 111 149L104 132L82 128C67 124 70 106 84 104Z', skin)
        s.line('M83 127Q95 125 104 132Q106 140 103 146', crease, .9, .5)
        s.line('M94 149Q101 138 112 139', crease, .7, .24)
    return s.finish()


def leaf(s, d, vein, fill):
    s.path(d, fill)
    s.line(vein, '#b2de62', .9, .44)


def strawberry(s, x=96, y=110, scale=1):
    s.parts.append(f'<g transform="translate({x-96*scale} {y-110*scale}) scale({scale})">')
    fruit = 'M69 45C44 49 20 75 26 119C29 149 44 173 57 182C93 189 150 145 162 111C174 76 151 50 131 47Z'
    s.path(fruit, glossy(s, 'strawberry-red', '#ffbbc1', '#fa263c', '#9c031a'))
    seed = glossy(s, 'strawberry-seed', '#fff5a4', '#ffce20', '#b87700')
    for xx, yy, a in [(43, 89, 22), (61, 77, 26), (89, 88, 17), (120, 84, 0), (146, 102, -5), (37, 114, 10), (61, 112, 20), (91, 118, 14), (118, 120, 15), (49, 143, 6), (73, 148, 13), (100, 145, 15), (62, 169, 12), (81, 165, 24)]:
        oval(s, xx, yy, 2.8, 5.3, seed, a)
    foliage = glossy(s, 'strawberry-leaf', '#a4e24e', '#5aaa13', '#285c02')
    for d, v in [('M96 61Q66 55 53 31Q52 54 74 66Z', 'M60 39L81 62'), ('M89 62Q84 41 91 16Q94 44 109 59Z', 'M92 28L100 57'), ('M110 60Q139 61 147 40Q153 61 127 70Z', 'M143 49L120 64'), ('M102 66Q70 59 59 73Q70 89 103 75Z', 'M73 73L97 70'), ('M109 63Q128 75 143 100Q113 97 108 76Z', 'M116 77L133 92'), ('M104 65Q96 82 109 96Q126 77 115 65Z', 'M110 72L111 86')]:
        leaf(s, d, v, foliage)
    s.line('M111 61L118 29', foliage, 9)
    s.parts.append('</g>')


def foods(slug, title):
    if slug == 'beer':
        return beer(title)
    s = Drawing(title)
    p = palette(s)
    pastry = glossy(s, 'pastry', '#ffe7a0', '#ffc657', '#b56a13')
    crust = glossy(s, 'crust', '#ffc578', '#dd8928', '#8e4210')
    cream = glossy(s, 'cream-food', '#fffef3', '#f4e8cb', '#c4a77c')
    chocolate = glossy(s, 'chocolate', '#bb7650', '#753b20', '#3b170b')
    silver = s.linear('silver-food', [('0', '#8b8b91'), ('.15', '#f8f8fb'), ('.38', '#bfc0c5'), ('.68', '#fff'), ('1', '#72757c')], x2='1', y2='.2')
    if slug == 'apple':
        apple = 'M96 46C73 28 40 40 25 65C5 100 21 156 43 177Q54 186 77 181Q96 178 113 182C146 188 169 153 175 116C183 73 166 41 141 39Q119 36 96 46Z'
        s.path(apple, glossy(s, 'apple-skin', '#ffadb1', '#fa1930', '#9b0015', '.28', '.22', '.98'))
        s.path('M84 50Q96 62 116 52', 'none', '#940919', 1.6, extra=' opacity=".5" stroke-linecap="round"')
        s.line('M98 52Q98 31 87 18', chocolate, 8)
        s.line('M95 42Q94 27 87 20', '#d0a058', 1.3, .55)
        leaf(s, 'M102 43C101 18 126 8 157 10C151 33 127 49 102 43Z', 'M105 40Q127 22 150 15', p['green'])
        oval(s, 53, 70, 8, 5, '#fff3f0', -28, ' opacity=".18"')
    elif slug == 'lemon':
        s.path('M51 172C25 137 26 86 48 57C64 32 122 28 146 50C176 80 177 130 147 163Q126 185 69 181L57 184Q49 184 51 172Z', glossy(s, 'lemon-skin', '#fff8b1', '#ffcf15', '#cf8400', '.27', '.23', '.95'))
        leaf(s, 'M36 67C54 26 87 12 141 27C129 57 95 77 36 67Z', 'M42 63Q89 46 129 30', p['green'])
        s.line('M139 46L149 22', p['green'], 8)
        s.line('M136 30L126 29', p['green'], 5)
        rng = random.Random(81)
        for i in range(48):
            x, y = rng.uniform(57, 145), rng.uniform(81, 155)
            oval(s, round(x, 1), round(y, 1), .45, .65, '#fff8bb', extra=' opacity=".18"')
    elif slug == 'strawberry':
        strawberry(s)
    elif slug == 'avocado':
        shell = 'M126 13C146 5 167 22 164 47L153 115C151 154 122 184 82 184C47 185 23 166 22 143C21 110 44 93 68 73L108 29Q118 17 126 13Z'
        flesh = 'M128 18C145 12 159 27 157 48L146 114C144 151 120 177 83 178C53 180 28 165 28 143C26 116 48 99 74 78L113 35Q122 22 128 18Z'
        s.path(shell, glossy(s, 'avocado-rind', '#8ac83f', '#3d7c1a', '#173e07'))
        s.path(flesh, glossy(s, 'avocado-flesh', '#ffffc4', '#ecf17b', '#94be37', '.51', '.25', '.83'))
        oval(s, 88, 133, 31, 36, chocolate, 29)
        oval(s, 80, 123, 10, 16, glossy(s, 'pit-gloss', '#ffdfb2', '#d8955d', '#8b4f2c'), 27, ' opacity=".6"')
        s.line('M39 154Q50 170 74 171', '#faffb5', 1.4, .55)
    elif slug == 'banana':
        banana = glossy(s, 'banana-fruit', '#fffce0', '#ffecb0', '#cdad5e')
        s.path('M96 113C114 100 122 81 125 47C126 20 132 9 145 10C168 10 177 41 172 71C167 105 157 128 140 146Z', banana)
        s.path('M91 105C79 73 53 70 28 85C17 92 8 110 14 117Q22 123 39 105Q64 82 72 95L76 124Z', pastry)
        s.path('M28 157C56 151 90 129 108 103C115 88 139 90 143 108C140 141 110 172 77 178H38Q19 179 23 166Z', p['gold'])
        s.path('M110 105C126 88 151 98 159 117C171 139 160 166 151 179H126C134 145 132 119 110 105Z', banana)
        s.line('M30 159Q73 153 105 119', '#fff3a3', 1.6, .65)
        s.line('M116 106Q148 118 137 168', '#fffcec', 1.7, .7)
        oval(s, 25, 168, 5, 9, chocolate, -13)
    elif slug == 'watermelon':
        rind = 'M49 39L174 113C166 145 139 168 111 172C73 177 29 151 19 118C12 92 26 51 36 30Z'
        s.path(rind, p['green'])
        s.path('M40 33L170 113C160 143 139 159 111 163C77 168 37 146 28 117C21 93 33 53 40 33Z', cream)
        s.path('M48 41L164 114C153 139 131 153 111 156C80 160 45 141 36 114C31 94 39 60 48 41Z', glossy(s, 'melon-flesh', '#ffadb4', '#ff3b50', '#c51627'))
        for x, y, a in [(62, 77, 46), (94, 85, 19), (66, 105, 40), (103, 116, 9), (132, 106, -13)]:
            s.path(f'M{x} {y-6}C{x-9} {y-1} {x-7} {y+7} {x} {y+7}C{x+7} {y+7} {x+7} {y-1} {x} {y-6}Z', p['dark'], extra=f' transform="rotate({a} {x} {y})"')
            oval(s, x-2, y+1, 1.4, 2, '#aaa1a0', a, ' opacity=".5"')
        s.line('M28 107Q30 139 64 154', '#82bd2d', 2.1, .6)
    elif slug == 'pizza':
        s.path('M77 26C105 26 148 67 164 98Q169 110 161 119L31 182Q17 188 18 174L65 52Z', crust)
        cheese = 'M67 42C96 43 136 78 150 110L90 140Q91 157 82 158Q75 160 73 148L29 179L21 178Z'
        s.path(cheese, pastry)
        s.path('M69 45C68 28 80 15 91 20C125 33 155 65 166 93Q172 109 156 116Q145 115 143 103C128 76 100 51 69 45Z', crust)
        pepperoni = glossy(s, 'pepperoni', '#ff7465', '#f12626', '#a40c10')
        for x, y, rx, ry in [(77, 82, 21, 18), (109, 112, 15, 14), (50, 134, 18, 16), (27, 165, 3.5, 7)]:
            oval(s, x, y, rx, ry, pepperoni, -23)
            if rx > 5:
                oval(s, x, y, rx-3, ry-3, 'none', -23, ' stroke="#ff8974" stroke-width=".8" opacity=".65"')
                for dx, dy in [(-5, -4), (5, 0), (0, 5)]:
                    oval(s, x+dx, y+dy, 1.1, 1.3, '#ffc196', extra=' opacity=".42"')
        s.line('M80 26Q125 44 155 91', '#ffd499', 1.3, .5)
    elif slug == 'burger':
        s.path('M26 147Q95 154 167 145C173 168 149 182 97 183C51 184 24 172 26 147Z', crust)
        oval(s, 97, 143, 70, 19, chocolate)
        s.path('M24 126Q47 119 68 123L94 126L142 124Q163 122 169 134L165 139L129 141L113 165Q109 171 104 165L69 141L26 140Z', p['gold'])
        s.path('M29 103Q96 96 164 105L168 119Q134 129 96 127Q60 130 27 119Z', p['red'])
        lettuce = 'M24 92Q34 84 45 91Q57 80 68 91Q81 82 95 93Q109 82 121 93Q134 84 145 91Q167 85 174 98Q180 111 168 112Q159 100 151 112Q141 125 126 111Q111 107 105 115Q93 123 81 113Q68 105 62 112Q46 126 34 109Q19 115 18 104Q17 98 24 92Z'
        s.path(lettuce, p['green'])
        bun = 'M24 95C19 56 52 19 93 17C139 15 173 52 174 94Q173 101 96 102Q29 104 24 95Z'
        s.path(bun, pastry)
        for x, y, a in [(55, 44, 43), (75, 34, 56), (100, 33, -17), (124, 40, -47), (143, 53, -40), (45, 68, 39), (68, 64, 37), (95, 57, 25), (116, 68, -26), (151, 78, -36), (55, 85, -37), (84, 82, 37)]:
            oval(s, x, y, 2, 4, cream, a)
    elif slug == 'fries':
        back = 'M27 66Q93 49 167 66L154 154Q94 173 35 153Z'
        s.path(back, p['red'])
        for x, y, w, h, a in [(36, 42, 17, 105, -17), (59, 25, 19, 121, -12), (82, 37, 18, 112, -3), (101, 17, 18, 128, 0), (120, 37, 18, 110, 8), (139, 23, 19, 124, 12), (156, 44, 16, 101, 20), (54, 62, 19, 92, -8), (78, 48, 18, 105, -2), (105, 68, 18, 85, 0), (130, 48, 18, 109, 6)]:
            rounded(s, x-9, y, w, h, 3, p['gold'], extra=f' transform="rotate({a} {x} {y+40})"')
            s.line(f'M{x-6} {y+5}V{y+35}', '#fff5a3', .9, .55)
        carton = 'M26 76Q38 80 45 90Q93 129 153 89L168 76L156 174Q153 184 142 182Q96 167 52 181Q40 186 36 173Z'
        s.path(carton, glossy(s, 'fries-carton', '#ff6874', '#f61d36', '#a5001a', '.27', '.23', '.95'))
        s.line('M40 96L49 166', '#ff8990', 1.3, .5)
    elif slug == 'taco':
        shell = 'M20 149C21 85 67 32 119 25C157 21 171 56 170 110L159 150L39 180Q22 183 20 149Z'
        s.path(shell, pastry)
        s.path('M26 146C30 90 75 36 119 31Q134 34 136 51L53 173Q26 182 26 146Z', chocolate)
        rng = random.Random(229)
        for i in range(30):
            x, y = rng.uniform(34, 85), rng.uniform(102, 164)
            if x + y < 147 or x + y > 225:
                continue
            oval(s, round(x, 1), round(y, 1), 5.5, 6.2, chocolate)
        for x, y, a in [(50, 97, 30), (59, 77, -22), (73, 62, 40), (88, 48, -15), (108, 37, 26), (125, 40, -20), (142, 48, 23), (43, 111, 18), (73, 94, -22), (91, 72, 36), (116, 60, 30)]:
            oval(s, x, y, 7, 10, p['green'], a)
        for x, y in [(63, 110), (65, 67), (92, 47), (113, 69), (138, 46), (90, 84)]:
            rounded(s, x-5, y-5, 11, 11, 2, p['red'], extra=f' transform="rotate(18 {x} {y})"')
        for d in ['M47 99Q60 86 73 92', 'M62 72Q85 60 91 65', 'M85 50Q104 44 119 53', 'M74 94Q85 75 107 78']:
            s.line(d, p['gold'], 4)
        front = 'M42 174C56 135 67 107 95 76C116 49 145 46 162 66C178 85 181 116 175 139Q172 146 159 149L52 180Q45 183 42 174Z'
        s.path(front, pastry)
        s.line('M48 172C60 137 81 96 110 72', '#ffec96', 1.7, .6)
        for x, y, r in [(97, 113, 2), (121, 84, 2.1), (147, 97, 2.4), (123, 126, 2.6), (151, 128, 1.9), (83, 148, 2), (108, 151, 2.2), (163, 112, 1.7), (107, 96, 1.5)]:
            oval(s, x, y, r, r*1.1, '#d7962a', extra=' opacity=".45"')
    elif slug == 'popcorn':
        tub = 'M29 72H164L151 173Q150 183 97 183Q44 183 42 173Z'
        s.path(tub, cream)
        s.start_clip(tub)
        for d in ['M31 76H48L60 182H44Z', 'M64 76H83L87 184H68Z', 'M105 76H125L123 184H104Z', 'M143 76H164L151 183H134Z']:
            s.path(d, p['red'])
        s.end_clip()
        popcorn = glossy(s, 'popcorn-puff', '#fffef0', '#f6e6bc', '#c4a369')
        s.path('M29 74C29 43 54 31 73 24C94 17 121 21 141 42Q161 48 166 76Z', popcorn)
        for x, y, r in [(55, 48, 13), (73, 29, 14), (94, 39, 13), (111, 28, 12), (129, 40, 13), (145, 51, 12), (39, 63, 12), (64, 65, 14), (90, 58, 16), (118, 63, 15), (149, 69, 13)]:
            for dx, dy, k in [(-5, 1, .7), (4, -4, .7), (1, 5, .7), (0, 0, .76)]:
                oval(s, x+dx, y+dy, round(r*k, 2), round(r*k, 2), popcorn)
        oval(s, 97, 77, 70, 8, cream)
        s.line('M35 81Q97 91 159 81', '#fffdf4', 1.6, .8)
    elif slug == 'cake':
        body = 'M25 89L146 68L173 86V169Q170 177 162 177L35 184Q26 185 25 176Z'
        s.path(body, cream)
        s.path('M27 103L159 91V124L29 137Z', pastry)
        s.path('M29 161L159 147V178L34 184Q27 184 27 176Z', pastry)
        for x, y, rx, ry in [(64, 147, 20, 9), (118, 140, 22, 9)]:
            oval(s, x, y, rx, ry, p['red'], -7)
        s.path('M25 89L125 22Q134 17 144 26L171 77Q179 89 169 92L33 106Q21 108 25 89Z', cream)
        strawberry(s, 92, 58, .39)
        for d in ['M114 70C113 56 132 52 130 32Q150 38 145 52C162 54 154 77 129 78Z', 'M123 70Q148 62 138 47', 'M119 58Q134 53 134 40']:
            if d.startswith('M114'):
                s.path(d, cream)
            else:
                s.line(d, '#fffdf2', 2, .75)
        s.line('M30 108L155 97', '#fffefa', 1.1, .8)
    elif slug == 'doughnut':
        ring = 'M96 16A80 80 0 1 0 96 176A80 80 0 1 0 96 16ZM96 74A23 23 0 1 1 96 120A23 23 0 1 1 96 74Z'
        s.path(ring, crust, extra=' fill-rule="evenodd"')
        icing = 'M94 19C114 15 141 25 153 39C166 52 169 67 168 81Q174 93 164 109Q166 124 154 133Q152 154 131 153Q123 169 108 159Q95 174 79 163Q64 165 56 152Q40 155 34 138Q18 130 27 113Q15 98 26 86Q21 67 33 56Q35 37 53 36Q68 19 94 19ZM96 73A24 24 0 1 1 96 121A24 24 0 1 1 96 73Z'
        s.path(icing, chocolate, extra=' fill-rule="evenodd"')
        colours = [p['pink'], p['blue'], p['gold'], p['red'], glossy(s, 'sprinkle-purple', '#eed3ff', '#b66be6', '#7634a5')]
        for i, (x, y, a) in enumerate([(52, 44, 25), (82, 37, -25), (108, 29, 0), (138, 40, 30), (153, 60, 12), (149, 85, 0), (156, 109, 32), (130, 131, -20), (111, 150, -30), (84, 141, 36), (59, 128, 7), (40, 111, -25), (43, 85, -45), (62, 69, 36), (96, 58, 25), (122, 62, 42)]):
            rounded(s, x-5, y-2, 11, 5, 2.5, colours[i % len(colours)], extra=f' transform="rotate({a} {x} {y})"')
    elif slug == 'cookie':
        oval(s, 96, 96, 82, 82, pastry)
        for x, y, a, k in [(58, 56, 12, 1), (131, 39, -24, .8), (57, 104, -25, .9), (115, 101, -10, 1), (88, 146, 0, 1), (150, 133, -25, .65), (158, 73, -10, .55)]:
            d = f'M{x-12*k} {y+5*k}C{x-17*k} {y-7*k} {x-4*k} {y-11*k} {x+5*k} {y-17*k}Q{x+16*k} {y-19*k} {x+16*k} {y+4*k}C{x+13*k} {y+20*k} {x-6*k} {y+17*k} {x-12*k} {y+5*k}Z'
            s.path(d, chocolate, extra=f' transform="rotate({a} {x} {y})"')
        for x, y, r in [(91, 65, 4.5), (82, 104, 4), (124, 153, 4.2), (44, 137, 3), (132, 66, 2), (99, 29, 1.5), (60, 151, 1.8), (108, 126, 1.7)]:
            oval(s, x, y, r, r, '#c98a36', extra=' opacity=".46"')
    elif slug == 'ice-cream':
        cone = 'M59 107H133L111 172Q107 185 96 184Q83 184 80 174Z'
        s.path(cone, pastry)
        s.start_clip(cone)
        for x in range(41, 149, 11):
            s.line(f'M{x} 110L{x+52} 181', '#bc771f', .8, .6)
            s.line(f'M{x} 110L{x-52} 181', '#bc771f', .8, .6)
        s.end_clip()
        s.path('M53 99Q97 105 137 99L133 114Q95 124 60 113Z', crust)
        scoop = 'M62 93C40 95 46 77 56 70C51 55 71 43 80 33C85 28 94 18 93 12C92 7 103 8 112 17Q125 28 119 39C137 43 142 56 136 67C151 76 149 92 137 98Q95 111 60 101Z'
        s.path(scoop, cream)
        for d in ['M58 71Q111 76 133 57', 'M55 92Q113 102 140 80', 'M79 41Q111 44 121 32']:
            s.line(d, '#fffdf4', 1.6, .65)
    elif slug == 'coffee':
        oval(s, 94, 168, 75, 16, glossy(s, 'porcelain', '#fff', '#f2efea', '#aaa19a'))
        oval(s, 96, 165, 55, 9, cream)
        s.path('M141 88C179 77 186 108 170 128Q158 142 138 139L137 127Q157 131 165 116Q175 98 143 100Z', cream)
        cup = 'M37 86H146C146 150 129 169 95 170C62 171 44 149 37 86Z'
        s.path(cup, glossy(s, 'coffee-cup', '#fff', '#efede7', '#aaa198', '.3', '.28', '.99'))
        oval(s, 92, 87, 55, 12, cream)
        oval(s, 92, 88, 46, 8, glossy(s, 'coffee', '#9b7054', '#593520', '#2c170d'))
        s.line('M43 106Q45 144 61 152', '#fff', 1.5, .85)
        for d in ['M84 79C72 61 80 58 87 48Q96 39 92 28', 'M107 77Q122 63 110 52Q98 41 113 31']:
            s.line(d, '#b8b3b0', 2.2, .45)
    elif slug == 'cheers':
        glass = s.linear('clear-glass', [('0', '#bac2ca'), ('.25', '#fff'), ('.5', '#cfdae4'), ('.8', '#fff'), ('1', '#9ba7b3')], x2='1', y2='0')
        wine = glossy(s, 'champagne', '#fff5bd', '#ffca3d', '#d58d08')
        for reflected in [False, True]:
            s.parts.append('<g' + (' transform="translate(192 0) scale(-1 1)"' if reflected else '') + '>')
            s.parts.append('<g transform="rotate(18 68 116)">')
            s.path('M47 42H91L88 111Q87 133 69 138Q50 134 49 111Z', glass)
            s.path('M51 66H87L84 109Q84 129 69 133Q54 128 53 109Z', wine)
            s.line('M69 138V174', '#c6d1db', 3)
            s.line('M68.2 140V171', '#fff', .6, .75)
            oval(s, 69, 177, 22, 4, glass)
            s.line('M53 52L56 110Q57 124 63 127', '#fff', 1.8, .65)
            for x, y in [(65, 79), (77, 102), (67, 114), (75, 90), (61, 98)]:
                oval(s, x, y, .8, 1.1, '#fff1a6', extra=' opacity=".7"')
            s.parts.append('</g></g>')
        for d in ['M96 13V28', 'M78 20L86 30', 'M112 20L104 30']:
            s.line(d, p['gold'], 4)
    else:
        raise ValueError(slug)
    return s.finish()


def objects(slug, title):
    s = Drawing(title)
    p = palette(s)
    metal = s.linear('polished-metal', [('0', '#686e78'), ('.13', '#e8ecf2'), ('.28', '#9ba1ac'), ('.49', '#fff'), ('.7', '#b6bdc7'), ('.89', '#f2f5f8'), ('1', '#666d77')], x2='1', y2='.15')
    gold = s.linear('polished-gold', [('0', '#b46c00'), ('.17', '#ffcf21'), ('.34', '#fff5ae'), ('.49', '#ffe057'), ('.75', '#ffba06'), ('.9', '#d88c00'), ('1', '#a36300')], x2='1', y2='.1')
    if slug == 'key':
        key = 'M106 77C91 49 98 17 123 11C152 2 180 26 181 52C183 82 160 100 133 99Q124 99 119 96L111 112H98L96 128H83L81 145H65L64 162H47L44 180H17L16 157Z'
        hole = 'M149 28A12 12 0 1 1 149 52A12 12 0 1 1 149 28Z'
        s.path(key+hole, gold, extra=' fill-rule="evenodd"')
        s.line('M25 158L99 84', '#fff5ae', 2.1, .65)
        oval(s, 149, 40, 14.5, 14.5, 'none', extra=' stroke="#fff1a1" stroke-width="1.2" opacity=".6"')
    elif slug == 'lock':
        shackle = 'M49 86V60C49 30 64 11 95 11C128 11 145 33 145 61V86H126V61C126 42 116 29 96 29C75 29 68 43 68 61V86Z'
        s.path(shackle, metal)
        rounded(s, 34, 78, 124, 105, 12, gold)
        hole = 'M96 102C112 102 119 124 106 133L110 153Q110 158 105 158H88Q83 158 84 153L88 133C73 124 80 102 96 102Z'
        s.path(hole, p['dark'], '#a86d07', 1.5)
        s.line('M42 91V164', '#fff0a0', 1.3, .7)
        s.line('M59 57Q59 22 91 20', '#fff', 1, .65)
    elif slug == 'idea':
        bulb = 'M95 12C58 12 34 38 35 73C36 105 60 111 68 143H124C130 111 158 107 158 73C158 40 132 11 95 12Z'
        s.path(bulb, glossy(s, 'bulb-glass', '#ffffdd', '#ffeb73', '#e1a126', '.43', '.34', '.83'))
        s.line('M86 144Q88 112 75 99', '#d39a18', 1.7, .55)
        s.line('M104 144Q102 111 115 100', '#d39a18', 1.7, .55)
        s.line('M75 99Q95 106 115 100', '#fff4a1', 1.4, .75)
        rounded(s, 68, 142, 56, 25, 5, metal)
        for y in [148, 156, 163]:
            s.line(f'M70 {y}Q96 {y+6} 122 {y}', '#5f626b', 1.8, .75)
            s.line(f'M73 {y-1}Q96 {y+3} 120 {y-1}', '#fff', .75, .75)
        s.path('M81 169H111Q106 183 96 183Q86 183 81 169Z', p['dark'])
    elif slug == 'gift':
        s.path('M24 71L96 93L170 71V154Q170 164 96 184L32 164Q24 162 24 153Z', gold)
        s.path('M96 93L170 71V154Q170 164 96 184Z', p['gold'])
        s.path('M22 53L95 29L173 53V87L96 112L22 88Z', p['gold'])
        s.path('M22 53L96 75L173 53L95 29Z', glossy(s, 'gift-top', '#fff7a6', '#ffdd44', '#db9c0a'))
        ribbon = glossy(s, 'gift-ribbon', '#ff9192', '#f9283a', '#9e001c')
        for d in ['M49 62L70 68V177L49 171Z', 'M122 68L143 62V171L122 177Z', 'M49 62L125 37L145 45L70 68Z', 'M70 38L143 62L122 69L49 45Z']:
            s.path(d, ribbon)
        s.path('M92 51C62 55 32 54 42 32C50 11 62 9 70 20L96 44Z', ribbon)
        s.path('M101 51C127 54 162 53 153 31C145 8 132 9 123 22L98 44Z', ribbon)
        s.path('M46 42Q63 32 88 49Q55 56 46 42Z', '#8d061c')
        s.path('M107 49Q133 30 148 41Q143 54 107 49Z', '#8d061c')
        rounded(s, 85, 38, 23, 22, 8, ribbon)
        s.line('M47 31Q51 15 59 17', '#ffb3af', 1.1, .7)
        s.line('M133 18Q144 12 149 31', '#ffb3af', 1.1, .7)
    elif slug == 'rocket':
        flame = 'M61 132C24 133 16 159 13 183C39 180 66 168 72 145Z'
        s.path(flame, glossy(s, 'rocket-flame', '#fff9a9', '#ffd31b', '#ff4900', '.75', '.17', '.98'))
        s.path('M59 137C38 139 29 151 26 169C45 165 59 154 64 144Z', '#fff7a1')
        s.path('M62 74C36 74 18 90 11 115Q9 123 16 120L45 110L69 113Z', p['red'])
        s.path('M112 124L116 158Q118 169 126 160C149 139 148 115 137 100Z', p['red'])
        hull = 'M42 117C59 70 102 18 171 13Q183 12 181 25C178 87 146 126 88 155Z'
        s.path(hull, glossy(s, 'rocket-hull', '#fff', '#dcdfe5', '#7e828d', '.34', '.25', '.97'))
        s.path('M126 25Q148 15 171 13Q184 11 181 28Q180 49 171 68Q143 56 126 25Z', p['red'])
        s.path('M42 117L88 155L81 163L36 124Z', metal)
        oval(s, 118, 77, 21, 21, metal)
        oval(s, 118, 77, 17.5, 17.5, glossy(s, 'rocket-port', '#70e8ff', '#087cef', '#003087', '.33', '.23', '.91'))
        oval(s, 112, 69, 5, 4, '#e4faff', extra=' opacity=".63"')
        s.path('M83 99C100 85 97 105 79 124L54 146Q48 149 52 138Z', p['red'])
        s.line('M56 110Q84 58 116 41', '#fff', 1.2, .7)
    elif slug == 'camera':
        rounded(s, 15, 50, 162, 124, 13, metal)
        s.path('M15 76H177V153H15Z', glossy(s, 'camera-grip', '#59585b', '#2a2a2e', '#15161b'))
        s.path('M68 50L78 31Q81 26 89 26H120Q128 26 131 33L139 50Z', metal)
        rounded(s, 30, 39, 26, 11, 3, p['dark'])
        oval(s, 103, 115, 47, 47, metal)
        oval(s, 103, 115, 40, 40, p['dark'])
        oval(s, 103, 115, 31, 31, glossy(s, 'camera-glass', '#70d2ff', '#13358c', '#020818', '.27', '.18', '.92'))
        oval(s, 106, 119, 23, 23, glossy(s, 'camera-inner', '#554bcc', '#122651', '#090e26', '.26', '.26', '.83'))
        oval(s, 98, 108, 14, 17, glossy(s, 'camera-coating', '#b282fa', '#342a89', '#0b1b36'), -27, ' opacity=".64"')
        oval(s, 91, 100, 4, 5, '#b7f2ff', -28, ' opacity=".78"')
        oval(s, 155, 68, 5, 5, p['red'])
        s.line('M24 56H62', '#fff', .85, .7)
    elif slug == 'trophy':
        for reflected in [False, True]:
            s.parts.append('<g' + (' transform="translate(192 0) scale(-1 1)"' if reflected else '') + '>')
            s.path('M50 30C11 18 8 56 32 86Q45 102 67 105L64 94C39 85 23 58 28 43Q33 31 51 43Z', gold)
            s.line('M48 33Q20 28 23 53', '#fff0a2', 1.2, .7)
            s.parts.append('</g>')
        bowl = 'M47 21Q96 8 145 21L141 61C138 101 123 123 98 126C68 127 53 104 50 61Z'
        s.path(bowl, gold)
        oval(s, 96, 22, 48, 7, p['gold'])
        oval(s, 96, 22, 40, 3.5, '#a3690e')
        s.path('M84 123H108C106 142 110 149 120 151Q127 157 118 161H72Q63 157 72 151C84 149 87 137 84 123Z', gold)
        rounded(s, 56, 160, 80, 22, 4, p['brown'])
        rounded(s, 49, 177, 94, 7, 3, p['brown'])
        rounded(s, 72, 165, 47, 13, 1, gold)
        s.line('M59 32Q63 102 82 116', '#fff6ba', 1.5, .6)
    elif slug == 'poop':
        brown = glossy(s, 'poop-swirl', '#c48351', '#84431f', '#4a2110', '.29', '.2', '.94')
        s.path('M44 130C14 147 15 170 43 178Q96 189 153 177C181 170 184 150 158 133Z', brown)
        s.path('M47 134C29 121 44 96 69 87Q97 65 135 91C166 100 174 126 151 142Q99 162 47 134Z', brown)
        s.path('M69 88C52 74 74 56 85 47C97 37 86 25 91 16C112 20 133 44 125 60Q149 59 148 81Q111 102 69 88Z', brown)
        for x in [71, 125]:
            oval(s, x, 119, 18, 24, p['white'])
            oval(s, x, 121, 8.8, 14.4, p['dark'])
            oval(s, x-3, 113, 2.6, 4, '#fff', extra=' opacity=".8"')
        s.path('M66 152Q95 161 133 150Q127 175 102 175Q78 174 66 152Z', p['dark'])
        s.path('M69 154Q96 162 130 153Q126 171 104 171Q81 171 69 154Z', p['white'])
    else:
        raise ValueError(slug)
    return s.finish()


def symbols(slug, title):
    s = Drawing(title)
    p = palette(s)
    if slug in {'heart', 'broken-heart'}:
        heart = 'M96 49C76 9 39 6 19 36C-5 72 23 115 47 139L90 179Q96 185 102 179C131 154 168 120 179 85C195 38 168 12 143 13Q115 13 96 49Z'
        if slug == 'broken-heart':
            left = 'M93 47C70 11 37 12 19 40C-1 73 24 125 84 175L79 134L93 112L79 94L92 74L81 61Z'
            right = 'M110 43C129 11 158 8 177 36C202 75 166 131 103 179L98 133L111 112L97 94L110 73L99 60Z'
            for d in [left, right]:
                s.path(d, glossy(s, 'heart-red', '#ffb2b8', '#ff2844', '#a70023', '.37', '.18', '.98'))
        else:
            s.path(heart, glossy(s, 'heart-red', '#ffb2b8', '#ff2844', '#a70023', '.37', '.18', '.98'))
        s.line('M30 43Q47 22 68 36', '#ffd9db', 1.2, .5)
        s.line('M126 31Q151 21 164 43', '#ffd9db', 1.2, .45)
    elif slug == 'fire':
        flame = 'M99 13C123 25 143 44 143 77C141 109 158 103 157 78C175 96 187 133 163 157Q136 183 99 184C60 185 30 164 24 141C16 119 30 98 43 86C31 116 57 123 58 93C58 65 96 56 95 29Z'
        s.path(flame, glossy(s, 'fire-orange', '#fff5a6', '#ffbf17', '#fa3906', '.5', '.83', '.9'))
        inner = 'M99 56C111 85 132 98 129 122Q137 139 143 127C153 158 126 178 98 179C66 178 48 158 53 135Q54 126 59 118C60 141 78 137 78 111Q78 88 99 56Z'
        s.path(inner, glossy(s, 'fire-core', '#ffffe2', '#fff578', '#ffbb0d', '.49', '.8', '.92'))
        s.path('M40 61Q43 44 52 39Q54 52 40 61Z', p['red'])
    elif slug in {'yes', 'no'}:
        if slug == 'yes':
            d = 'M25 90Q32 83 40 90L69 119L140 35Q146 27 154 33L172 48Q180 55 173 63L82 169Q73 180 63 170L15 121Q8 113 15 105Z'
            fill = glossy(s, 'check-green', '#9cff71', '#26cd1b', '#087406', '.37', '.18', '.98')
        else:
            d = 'M26 19Q32 13 40 19L96 73L149 20Q157 13 164 20L178 34Q185 41 178 48L122 96L178 149Q185 156 178 164L164 178Q157 185 149 178L96 123L42 177Q34 185 26 177L13 164Q7 157 14 149L70 96L15 44Q7 37 14 29Z'
            fill = glossy(s, 'cross-red', '#ff939c', '#ff2c44', '#b40423', '.33', '.15', '.98')
        s.path(d, fill)
    elif slug == 'celebrate':
        cone = 'M83 55L152 106C123 131 62 177 32 181Q17 182 22 166C34 131 54 78 65 62Q71 50 83 55Z'
        s.path(cone, p['gold'])
        s.start_clip(cone)
        for d in ['M15 148Q51 177 92 154L78 169Q42 185 13 169Z', 'M34 104Q75 151 116 140L104 155Q65 164 25 126Z', 'M52 62Q100 117 147 110L127 131Q90 135 43 86Z']:
            s.path(d, glossy(s, 'party-purple', '#d898ff', '#9333e3', '#562196'))
        s.end_clip()
        oval(s, 106, 78, 48, 14, p['gold'], 37)
        for d, fill in [('M116 52C124 34 125 23 115 14', p['pink']), ('M147 41Q140 26 159 19Q168 15 167 10', p['gold']), ('M157 93Q174 77 182 91', p['blue'])]:
            s.line(d, fill, 8)
        for x, y, r, fill in [(80, 22, 4, p['blue']), (101, 21, 4, p['pink']), (41, 75, 3.5, p['blue']), (169, 54, 4, p['red']), (166, 111, 3.5, p['gold']), (157, 137, 4, p['blue']), (178, 107, 2.4, p['gold'])]:
            oval(s, x, y, r, r, fill)
    elif slug == 'bitcoin':
        coin = s.linear('coin-gold', [('0', '#fff3a0'), ('.22', '#ffc625'), ('.56', '#ff9409'), ('.83', '#ed7b00'), ('1', '#cf5b00')], x2='1', y2='1')
        oval(s, 96, 96, 87, 87, coin)
        oval(s, 96, 96, 80, 80, 'none', extra=' stroke="#ffe37a" stroke-width="2"')
        oval(s, 96, 96, 73, 73, p['orange'])
        oval(s, 96, 96, 73, 73, 'none', extra=' stroke="#c66a06" stroke-width="1.4"')
        mark = 'M65 54H79V40H87V54H99V40H107V55C128 58 133 78 122 89C141 100 136 127 107 133V148H99V134H87V148H79V134H65V124H73V64H65ZM87 64V86H101C119 86 119 64 101 64ZM87 96V123H103C124 123 124 96 103 96Z'
        s.path(mark, '#a85503', extra=' fill-rule="evenodd" transform="translate(1 1.4)"')
        s.path(mark, glossy(s, 'bitcoin-mark', '#fff', '#fff9ee', '#ddd2bc'), extra=' fill-rule="evenodd"')
        s.line('M33 52Q59 20 97 17', '#fff5a6', 1.1, .7)
    else:
        raise ValueError(slug)
    return s.finish()


def rebuild(slug, title):
    if slug.split('-tone')[0] in HAND_SLUGS:
        return hands(slug, title)
    if slug in FOOD_SLUGS:
        return foods(slug, title)
    if slug in OBJECT_SLUGS:
        return objects(slug, title)
    return symbols(slug, title)
