from html5lib.serializer import serialize
import itertools
import xml.dom
import yaml

msi = yaml.safe_load(open('msi-2018.yaml'))

impl = xml.dom.getDOMImplementation()
doctype = impl.createDocumentType("html", None, None)
doc = impl.createDocument(None, "html", doctype)
html = doc.documentElement
html.setAttribute("lang", "en")

head = doc.createElement("head")
html.appendChild(head)

title = doc.createElement("title")
title.appendChild(doc.createTextNode(msi['abbr']))
head.appendChild(title)

charset = doc.createElement("meta")
charset.setAttribute("charset", "utf-8")
head.appendChild(charset)

viewport = doc.createElement("meta")
viewport.setAttribute("name", "viewport")
viewport.setAttribute("content", "width=device-width, initial-scale=1")
head.appendChild(viewport)

stylesheet = doc.createElement("link")
stylesheet.setAttribute("rel", "stylesheet")
stylesheet.setAttribute("href", "style.css")
head.appendChild(stylesheet)

style = doc.createElement("style")
style.appendChild(doc.createTextNode("""
#participants td:nth-child(3) {
    text-align: left;
    padding-left: 1em;
    padding-right: 1em;
}
"""))
head.appendChild(style)

body = doc.createElement("body")
html.appendChild(body)

h1 = doc.createElement("h1")
h1.appendChild(doc.createTextNode(msi['name']))
body.appendChild(h1)

def wrap_details(doc, element, summary=None):
    details = doc.createElement("details")
    if summary is not None:
        if not isinstance(summary, xml.dom.Node):
            summary = doc.createTextNode(summary)
        outer_summary = doc.createElement("summary")
        outer_summary.appendChild(summary)
        details.appendChild(outer_summary)
    details.appendChild(element)
    return details

def create_teams_section(doc, msi):
    teams = msi['teams']

    section = doc.createElement("div")

    table = doc.createElement("table")
    table.setAttribute("id", "participants")

    for i, team in enumerate(teams):
        if i in [0, 4, 6, 10]:
            tr = doc.createElement("tr")
            th = doc.createElement("th")
            th.setAttribute("colspan", "3")
            label = {
                0: "Main Event Seeds",
                4: "Play-In Round 2 Seeds",
                6: "Play-In Round 1 Seeds (Pool 1)",
                10: "Play-In Round 1 Seeds (Pool 2)",
            }[i]
            th.appendChild(doc.createTextNode(label))
            tr.appendChild(th)
            table.appendChild(tr)
        if i == 0:
            tr = doc.createElement("tr")
            for text in ["Region", "Team", "Full Team Name"]:
                th = doc.createElement("th")
                th.appendChild(doc.createTextNode(text))
                tr.appendChild(th)
            table.appendChild(tr)
        tr = doc.createElement("tr")
        for text in [team["region"], team["abbr"], team["name"]]:
            td = doc.createElement("td")
            td.appendChild(doc.createTextNode(text))
            tr.appendChild(td)
        table.appendChild(tr)

    details = wrap_details(doc, table, "Participants")
    section.appendChild(details)
    return section

body.appendChild(create_teams_section(doc, msi))

def create_group_table(doc, placements, winning_place):
    table = doc.createElement("table")
    table.setAttribute("class", "grouptable")

    tr = doc.createElement("tr")
    for text in ["Place", "Team", "W", "L"]:
        th = doc.createElement("th")
        th.appendChild(doc.createTextNode(text))
        tr.appendChild(th)
    table.appendChild(tr)

    for row in placements:
        tr = doc.createElement("tr")
        if row['place'] <= winning_place:
            tr.setAttribute("class", "won")
        else:
            tr.setAttribute("class", "lost")
        for text in [row['place'], row['team']['abbr'],
                     row['wins'], row['losses']]:
            td = doc.createElement("td")
            td.appendChild(doc.createTextNode(str(text)))
            tr.appendChild(td)
        table.appendChild(tr)
    return table

def compute_crosstable(teams, games):
    crosstable = [[{'wins': 0, 'losses': 0} for _ in teams] for _ in teams]
    for game in games:
        blue, red = game['blue'], game['red']
        i = teams.index(blue)
        j = teams.index(red)
        if blue == game['winner']:
            crosstable[i][j]['wins'] += 1
            crosstable[j][i]['losses'] += 1
        elif red == game['winner']:
            crosstable[j][i]['wins'] += 1
            crosstable[i][j]['losses'] += 1
    return crosstable

def create_crosstable(doc, teams, crosstable):
    table = doc.createElement("table")
    table.setAttribute("class", "crosstable")
    tr = doc.createElement("tr")
    for text in ["Team"] + [team['abbr'] for team in teams]:
        th = doc.createElement("th")
        th.appendChild(doc.createTextNode(text))
        tr.appendChild(th)
    table.appendChild(tr)

    for i, team in enumerate(teams):
        tr = doc.createElement("tr")
        td = doc.createElement("td")
        td.appendChild(doc.createTextNode(team['abbr']))
        tr.appendChild(td)
        for j, wl in enumerate(crosstable[i]):
            if i == j:
                tr.appendChild(doc.createElement("td"))
                continue

            text = '%(wins)d\u2013%(losses)d' % wl
            clazz = ('won' if wl['wins'] > wl['losses'] else
                     'lost' if wl['losses'] > wl['wins'] else
                     'tied')
            td = doc.createElement("td")
            td.setAttribute("class", clazz)
            td.appendChild(doc.createTextNode(text))
            tr.appendChild(td)
        table.appendChild(tr)
    return table

def create_matchbox_tr(doc, abbr1, won1, score1, abbr2, won2, score2):
    tr = doc.createElement("tr")

    td1n = doc.createElement("td")
    td1n.appendChild(doc.createTextNode(abbr1))
    td1s = doc.createElement("td")
    td1s.appendChild(doc.createTextNode(score1))

    td2s = doc.createElement("td")
    td2s.appendChild(doc.createTextNode(score2))
    td2n = doc.createElement("td")
    td2n.appendChild(doc.createTextNode(abbr2))

    if won1 or won2:
        td1n.setAttribute("class", "won" if won1 else "lost")
        td2n.setAttribute("class", "won" if won2 else "lost")

    tr.appendChild(td1n)
    tr.appendChild(td1s)
    tr.appendChild(td2s)
    tr.appendChild(td2n)
    return tr

def create_games_table(doc, games):
    table = doc.createElement("table")
    table.setAttribute("class", "matchbox")

    lastlabel = None
    for game in games:
        label = game.get('label')
        if label is not None and (lastlabel is None or lastlabel != label):
            tr = doc.createElement("tr")
            th = doc.createElement("th")
            th.setAttribute("colspan", "4")
            th.appendChild(doc.createTextNode(label))
            tr.appendChild(th)
            table.appendChild(tr)
            lastlabel = label
        blue, red, winner = game['blue'], game['red'], game['winner']
        tr = create_matchbox_tr(doc,
                blue['abbr'], blue == winner, str(int(blue == winner)),
                red ['abbr'], red  == winner, str(int(red  == winner)))
        table.appendChild(tr)
    return table

def create_playin_round1_section(doc, stage):
    section = doc.createElement("section")

    h2 = doc.createElement("h2")
    h2.appendChild(doc.createTextNode(stage['name']))
    section.appendChild(h2)

    groupsdiv = doc.createElement("div")
    section.appendChild(groupsdiv)
    groupsdiv.setAttribute("class", "groups collapse-h3")

    for group in stage['groups']:
        subsection = doc.createElement("section")
        groupsdiv.appendChild(subsection)

        h3 = doc.createElement("h3")
        h3.appendChild(doc.createTextNode(group['name']))
        subsection.appendChild(h3)

        subsection.appendChild(create_group_table(doc, group["placements"], 1))

        teams = [row['team'] for row in group['placements']]
        crosstable = compute_crosstable(teams, group['games'])
        outer_crosstable = create_crosstable(doc, teams, crosstable)
        details = wrap_details(doc, outer_crosstable, "Crosstable")
        subsection.appendChild(details)

        games_table = create_games_table(doc, group['games'])
        details = wrap_details(doc, games_table, "Games")
        subsection.appendChild(details)

    return section

body.appendChild(create_playin_round1_section(doc, msi['stages'][0]))

def create_matchbox(doc, match):
    table = doc.createElement("table")
    table.setAttribute("class", "matchbox")

    team1, team2, winner = match['team1'], match['team2'], match['winner']
    tr = create_matchbox_tr(doc,
            team1['abbr'], team1 == winner, str(match['score1']),
            team2['abbr'], team2 == winner, str(match['score2']))
    table.appendChild(tr)
    return table

def create_playin_round2_section(doc, stage):
    section = doc.createElement("section")

    h2 = doc.createElement("h2")
    h2.appendChild(doc.createTextNode(stage['name']))
    section.appendChild(h2)

    groupsdiv = doc.createElement("div")
    section.appendChild(groupsdiv)
    groupsdiv.setAttribute("class", "groups")

    for match in stage['matches']:
        subsection = doc.createElement("div")
        groupsdiv.appendChild(subsection)

        subsection.appendChild(create_matchbox(doc, match))

        games_table = create_games_table(doc, match['games'])
        details = wrap_details(doc, games_table, "Games")
        subsection.appendChild(details)

    return section

body.appendChild(create_playin_round2_section(doc, msi['stages'][1]))

def create_group_stage_section(doc, stage):
    section = doc.createElement("section")

    h2 = doc.createElement("h2")
    h2.appendChild(doc.createTextNode(stage['name']))
    section.appendChild(h2)

    section.appendChild(create_group_table(doc, stage["placements"], 4))

    teams = [row['team'] for row in stage['placements']]
    crosstable = compute_crosstable(teams, stage['games'])
    outer_crosstable = create_crosstable(doc, teams, crosstable)
    details = wrap_details(doc, outer_crosstable, "Crosstable")
    section.appendChild(details)

    groupsdiv = doc.createElement("div")
    groupsdiv.setAttribute("class", "groups")
    for _, games in itertools.groupby(stage['games'], lambda g: g['label']):
        groupsdiv.appendChild(create_games_table(doc, games))
    details = wrap_details(doc, groupsdiv, "Games")
    section.appendChild(details)

    return section

body.appendChild(create_group_stage_section(doc, msi['stages'][2]))

def create_knockout_stage_section(doc, stage):
    section = doc.createElement("section")

    h2 = doc.createElement("h2")
    h2.appendChild(doc.createTextNode(stage['name']))
    section.appendChild(h2)

    groupsdiv = doc.createElement("div")
    section.appendChild(groupsdiv)
    groupsdiv.setAttribute("class", "groups collapse-h3")

    for match in stage['matches']:
        subsection = doc.createElement("div")
        groupsdiv.appendChild(subsection)

        h3 = doc.createElement("h3")
        h3.appendChild(doc.createTextNode(match['label']))
        subsection.appendChild(h3)

        subsection.appendChild(create_matchbox(doc, match))

        games_table = create_games_table(doc, match['games'])
        details = wrap_details(doc, games_table, "Games")
        subsection.appendChild(details)

    return section

body.appendChild(create_knockout_stage_section(doc, msi['stages'][3]))

if False:

    knockout = msi['stages'][3]
    assert knockout['name'] == 'Knockout Stage'
    print("<section>")
    print("<h2>%(name)s</h2>" % knockout)
    print("<div class=\"groups collapse-h3\">")
    for match in knockout['matches']:
        team1, team2 = match['team1'], match['team2']
        print("<div>")
        print("<h3>%s</h3>" % match['label'])
        print("<table class=\"matchbox\">")
        print("<tr><td class=\"%s\">%s<td>%d<td>%d<td class=\"%s\">%s</tr>" % 
                ('won' if team1 == match['winner'] else 'lost',
                 team1['abbr'],
                 match['score1'],
                 match['score2'],
                 'won' if team2 == match['winner'] else 'lost',
                 team2['abbr']))
        print("</table>")
        print("<details>")
        print('<summary>Games</summary>')
        print('<table class="matchbox">')
        for game in match['games']:
            blue, red = game['blue'], game['red']
            print('<tr><td class="%s">%s<td>%d<td>%d<td class="%s">%s</tr>' % 
                    ('won' if blue == game['winner'] else 'lost',
                     blue['abbr'],
                     int(blue == game['winner']),
                     int(red == game['winner']),
                     'won' if red == game['winner'] else 'lost',
                     red['abbr']))
        print("</table>")
        print("</details>")
        print("</div>")
    print("</div>")
    print("</section>")

print(serialize(doc, tree="dom"))
