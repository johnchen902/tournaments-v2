import xml.etree.ElementTree as et
import math

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

def create_single_elimination_svg(matches):
    rounds = math.floor(math.log2(len(matches))) + 1
    r1matches = (2 ** (rounds - 1))

    width = rounds * 100 - 20
    height = r1matches * 50

    svg = et.Element("svg", width="%dpx" % width, height="%dpx" % height,
                            viewBox="-5.5 -5.5 %d %d" % (width, height),
                            xmlns="http://www.w3.org/2000/svg")
    
    ys = [i * 50 for i in range(r1matches)]
    matchid = 0

    for r in range(rounds):
        for y in ys:
            svg.append(create_matchbox(r * 100, y, 70, 40, matches[matchid]))
            matchid += 1
        if len(ys) >= 2:
            newys = []
            for i in range(0, len(ys), 2):
                newys.append((ys[i] + ys[i + 1]) / 2)
                svg.append(create_connection(r * 100 + 70, ys[i] + 20,
                                            (r + 1) * 100, newys[-1] + 10))
                svg.append(create_connection(r * 100 + 70, ys[i + 1] + 20,
                                            (r + 1) * 100, newys[-1] + 35))
            ys = newys

    return svg
