"""Requested semantic changes that cannot come from tracing the PNGs."""
import math
import random
from clean_vectors import Drawing as BaseDrawing


class Drawing(BaseDrawing):
    # Materials have their own highlights: the generic white overlay made
    # cheese, pastry and red fruit pale in the previous pass.
    def volume(self,element,fill):pass


def vegetarian_overlay():
    s=Drawing('Vegetarian toppings')
    s.defs=[]
    s.defs.append('<filter id="topping-shadow" x="-15%" y="-15%" width="130%" height="130%"><feDropShadow dx=".3" dy=".65" stdDeviation=".35" flood-color="#8c4210" flood-opacity=".42"/></filter>')
    # Red rounds become sliced tomatoes: pale pulp/seed chambers explicitly
    # distinguish these from the earlier pepperoni reference.
    for x,y,k in [(83,75,1.14),(112,111,.77),(53,125,1.04),(20,158,.22)]:
        s.parts.append(f'<g transform="translate({x} {y}) rotate(-24) scale({k})">')
        s.ellipse(0,0,15.7,12.6,'none',extra=' stroke="#ffcf77" stroke-width=".8" opacity=".7"')
        for a in [0,math.tau/3,math.tau*2/3]:
            xx,yy=math.cos(a)*10.5,math.sin(a)*7
            s.path(f'M0 0Q{xx-4:.2f} {yy-2:.2f} {xx:.2f} {yy:.2f}Q{xx+2:.2f} {yy+2:.2f} 0 0Z','#ffcd75',extra=' opacity=".76"')
            s.ellipse(round(xx*.67,2),round(yy*.67,2),1.05,.62,'#fff3ad')
        s.parts.append('</g>')
    s.parts.append('<g filter="url(#topping-shadow)">')
    pepper=s.radial('pepper','#bcf37b','#45a51e','#176510',cx='.25',cy='.14')
    for x,y,a,k in [(100,79,20,.85),(83,113,-30,.78),(39,154,-20,.6)]:
        s.parts.append(f'<g transform="translate({x} {y}) rotate({a}) scale({k})">')
        s.path('M-13 4C-21-8-4-14 6-9Q17-3 10 9L5 6Q10 0 3-4C-8-10-13-3-8 3Z',pepper)
        s.line('M-12 1Q-17-7-5-9Q3-10 9-4','#d5f7a0',1.05,.8);s.parts.append('</g>')
    # Mushrooms, purple onion and olives make the vegetarian toppings explicit.
    mushroom=s.radial('mushroom','#fff6da','#dfc7a3','#a58b63')
    for x,y,a,k in [(80,56,-15,.72),(75,145,-28,.6)]:
        s.parts.append(f'<g transform="translate({x} {y}) rotate({a}) scale({k})">')
        s.path('M-4 1L-5 11Q0 14 5 11L4 1Z',mushroom)
        s.path('M-14 1C-12-17 12-17 14 1Q0 7-14 1Z',mushroom)
        s.line('M-10 2Q0 5 10 2','#8f7253',1,.7);s.parts.append('</g>')
    for x,y,a in [(104,128,-24),(52,105,25)]:
        s.parts.append(f'<g transform="translate({x} {y}) rotate({a})">')
        s.path('M-10-4C-16 3-9 11 2 9Q12 8 10-1L7-1Q8 6 1 6C-6 7-10 3-7-2Z','#a15091')
        s.line('M-9-2C-13 5-5 9 2 8Q10 7 9 1','#f6daee',1,.95);s.parts.append('</g>')
    olive=s.radial('olive','#737c43','#2c331c','#12190c',cx='.22',cy='.17')
    for x,y,k in [(89,96,1),(126,94,.77),(41,140,.73)]:
        s.path(f'M{x} {y-5*k}A{7*k} {5*k} 0 1 0 {x} {y+5*k}A{7*k} {5*k} 0 1 0 {x} {y-5*k}ZM{x} {y-2*k}A{3*k} {2*k} 0 1 1 {x} {y+2*k}A{3*k} {2*k} 0 1 1 {x} {y-2*k}Z',olive,extra=' fill-rule="evenodd"')
        s.line(f'M{x-3*k} {y-3*k}Q{x} {y-5*k} {x+3*k} {y-3*k}','#aeb481',.6,.7)
    s.parts.append('</g>')
    return ''.join(s.defs),''.join(s.parts)


# Small outlined letters keep the engraved plaque font-independent.
LETTERS={
 'D':'M0 0H2Q5 0 5 3.5Q5 7 2 7H0Z M1.4 1.4V5.6H2Q3.6 5.6 3.6 3.5Q3.6 1.4 2 1.4Z',
 'O':'M2.5 0C-1 0-1 7 2.5 7C6 7 6 0 2.5 0Z M2.5 1.3C4.2 1.3 4.2 5.7 2.5 5.7C.8 5.7 .8 1.3 2.5 1.3Z',
 'N':'M0 7V0H1.5L3.7 4.4V0H5V7H3.5L1.3 2.6V7Z',
 'K':'M0 0H1.4V2.7L3.6 0H5.3L2.5 3.3L5.4 7H3.7L1.4 4V7H0Z',
 'E':'M0 0H5V1.3H1.4V2.8H4.5V4.1H1.4V5.7H5V7H0Z',
 'Y':'M0 0H1.5L2.7 2.8L4 0H5.5L3.4 4.3V7H2V4.3Z',
}


def trophy_engraving():
    letters=''.join(f'<path d="{LETTERS[c]}" transform="translate({i*6.2} 0)" fill-rule="evenodd"/>' for i,c in enumerate('DONKEY'))
    return '<g aria-label="DONKEY" transform="translate(77.2 158.5) scale(.98)"><g fill="#ffe7a0" transform="translate(.25 .45)" opacity=".85">'+letters+'</g><g fill="#68430e">'+letters+'</g></g>'
