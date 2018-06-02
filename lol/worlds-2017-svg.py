import itertools
import sys
import xml.etree.ElementTree as et
import yaml

import tournament

def create_rect(x, y, width, height, **attr):
    x, y, width, height = map(str, (x, y, width, height))
    return et.Element("rect", x=x, y=y, width=width, height=height, **attr)

def create_text(x, y, text, **attr):
    x, y, text = map(str, (x, y, text))
    element = et.Element("text", x=x, y=y, **attr)
    element.text = text
    return element

def create_line(x1, y1, x2, y2, **attr):
    x1, y1, x2, y2 = map(str, (x1, y1, x2, y2))
    return et.Element("line", x1=x1, y1=y1, x2=x2, y2=y2, **attr)

def create_polyline(*points, **attr):
    points_val = ' '.join('%g,%g' % (x, y) for x, y in points)
    return et.Element("polyline", points=points_val, **attr)

def create_matchbox(x, y, w, h, game):
    g = et.Element("g")
    g.append(create_rect(x, y, w, h, fill="none", stroke="black"))
    g.append(create_line(x + w * .7, y, x + w * .7, y + h, stroke="black"))
    g.append(create_line(x, y + h * .5, x + w, y + h * .5, stroke="black"))
    g.append(create_text(x + w * .1, y + h * .4, game['team1']['abbr']))
    g.append(create_text(x + w * .8, y + h * .4, game['score1']))
    g.append(create_text(x + w * .1, y + h * .9, game['team2']['abbr']))
    g.append(create_text(x + w * .8, y + h * .9, game['score2']))
    return g

def create_connection(x1, y1, x2, y2):
    xm = (x1 + x2) / 2
    return create_polyline((x1, y1), (xm, y1), (xm, y2), (x2, y2),
                           fill="none", stroke="black")

def create_single_elimination_8_svg(matches):
    svg = et.Element("svg", width="280px", height="200px",
                            viewBox="-5.5 -5.5 280 200",
                            xmlns="http://www.w3.org/2000/svg")

    svg.append(create_matchbox(  0,   0, 70, 40, matches[0]))
    svg.append(create_matchbox(  0,  50, 70, 40, matches[1]))
    svg.append(create_matchbox(  0, 100, 70, 40, matches[2]))
    svg.append(create_matchbox(  0, 150, 70, 40, matches[3]))

    svg.append(create_matchbox(100,  25, 70, 40, matches[4]))
    svg.append(create_matchbox(100, 125, 70, 40, matches[5]))

    svg.append(create_matchbox(200,  75, 70, 40, matches[6]))

    svg.append(create_connection( 70,  20, 100,  35))
    svg.append(create_connection( 70,  70, 100,  55))
    svg.append(create_connection( 70, 120, 100, 135))
    svg.append(create_connection( 70, 170, 100, 155))

    svg.append(create_connection(170,  45, 200,  85))
    svg.append(create_connection(170, 145, 200, 105))
    return svg

data = yaml.safe_load(open('worlds-2017.yaml'))
matches = data['stages'][3]['matches']
svg = create_single_elimination_8_svg(matches)
et.ElementTree(svg).write(sys.stdout.buffer)
