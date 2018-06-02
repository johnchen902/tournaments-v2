from html5lib.serializer import serialize
import itertools
import sys
import xml.etree.ElementTree as et
import yaml

msi = yaml.safe_load(open('msi-2017.yaml'))

html = et.Element("html", lang="en")
head = et.SubElement(html, "head")
et.SubElement(head, "meta", charset="utf-8")
et.SubElement(head, "title").text = msi['abbr']
et.SubElement(head, "meta", name="viewport",
              content="width=device-width, initial-scale=1")
et.SubElement(head, "link", rel="stylesheet", href="style.css")
et.SubElement(head, "style").text = """
#participants td:nth-child(3) {
    text-align: left;
    padding-left: 1em;
    padding-right: 1em;
}
"""

body = et.SubElement(html, "body")
et.SubElement(body, "h1").text = msi['name']

def wrap_details(*elements, summary=None):
    details = et.Element("details")
    if summary is not None:
        et.SubElement(details, "summary").text = summary
    details.extend(elements)
    return details

def create_teams_table(teams, labels={}):
    table = et.Element("table", id="participants")

    for i, team in enumerate(teams):
        if i in labels:
            tr = et.SubElement(table, "tr")
            et.SubElement(tr, "th", colspan="3").text = labels[i]

        if i == 0:
            tr = et.SubElement(table, "tr")
            for text in ["Region", "Team", "Full Team Name"]:
                et.SubElement(tr, "th").text = text

        tr = et.SubElement(table, "tr")
        for text in [team["region"], team["abbr"], team["name"]]:
            et.SubElement(tr, "td").text = text

    return table

teams_table = create_teams_table(msi['teams'], labels = {
    0: "Main Event Seeds",
    3: "Play-In Round 2 Seeds",
    5: "Play-In Round 1 Seeds (Pool 1)",
    9: "Play-In Round 1 Seeds (Pool 2)",
})
teams_div = et.SubElement(body, "div")
teams_div.append(wrap_details(teams_table, summary="Participants"))

def create_group_table(placements, winners):
    table = et.Element("table", {"class": "grouptable"})

    tr = et.SubElement(table, "tr")
    for text in ["Place", "Team", "W", "L"]:
        et.SubElement(tr, "th").text = text

    for row in placements:
        tr = et.SubElement(table, "tr")
        for text in [row['place'], row['team']['abbr'],
                     row['wins'], row['losses']]:
            et.SubElement(tr, "td").text = str(text)
        tr[1].set("class", "won" if row['team'] in winners else "lost")
    return table

def compute_crosstable_from_games(teams, games):
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

def create_crosstable(teams, crosstable):
    table = et.Element("table", {"class": "crosstable"})
    tr = et.SubElement(table, "tr")
    for text in ["Team"] + [team['abbr'] for team in teams]:
        et.SubElement(tr, "th").text = text

    for i, team in enumerate(teams):
        tr = et.SubElement(table, "tr")
        et.SubElement(tr, "td").text = team['abbr']

        for j, wl in enumerate(crosstable[i]):
            if i == j:
                et.SubElement(tr, "td")
                continue

            text = '%(wins)d\u2013%(losses)d' % wl
            clazz = ('won' if wl['wins'] > wl['losses'] else
                     'lost' if wl['losses'] > wl['wins'] else
                     'tied')
            et.SubElement(tr, "td", {"class": clazz}).text = text
    return table

def create_matchbox_tr(abbr1, won1, score1, abbr2, won2, score2):
    tr = et.Element("tr")
    et.SubElement(tr, "td").text = abbr1
    et.SubElement(tr, "td").text = score1
    et.SubElement(tr, "td").text = score2
    et.SubElement(tr, "td").text = abbr2
    if won1 or won2:
        tr[0].set("class", "won" if won1 else "lost")
        tr[3].set("class", "won" if won2 else "lost")
    return tr

def create_games_table(games):
    table = et.Element("table", {"class": "matchbox"})

    lastlabel = None
    for game in games:
        label = game.get('label')
        if label is not None and (lastlabel is None or lastlabel != label):
            tr = et.SubElement(table, "tr")
            et.SubElement(tr, "th", colspan="4").text = label
            lastlabel = label
        blue, red, winner = game['blue'], game['red'], game['winner']
        tr = create_matchbox_tr(
                blue['abbr'], blue == winner, str(int(blue == winner)),
                red ['abbr'], red  == winner, str(int(red  == winner)))
        table.append(tr)
    return table

def create_playin_round1_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']
    groupsdiv = et.SubElement(section, "div", {"class": "groups collapse-h3"})

    for group in stage['groups']:
        subsection = et.SubElement(groupsdiv, "section")
        et.SubElement(subsection, "h3").text = group['name']

        subsection.append(create_group_table(group["placements"],
                                             group["winners"]))

        teams = [row['team'] for row in group['placements']]
        crosstable = compute_crosstable_from_games(teams, group['games'])
        crosstable = create_crosstable(teams, crosstable)
        details = wrap_details(crosstable, summary="Crosstable")
        subsection.append(details)

        games_table = create_games_table(group['games'])
        details = wrap_details(games_table, summary="Games")
        subsection.append(details)

    return section

body.append(create_playin_round1_section(msi['stages'][0]))

def create_matchbox(match):
    table = et.Element("table", {"class": "matchbox"})
    team1, team2, winner = match['team1'], match['team2'], match['winner']
    table.append(create_matchbox_tr(
            team1['abbr'], team1 == winner, str(match['score1']),
            team2['abbr'], team2 == winner, str(match['score2'])))
    return table

def create_playin_round2_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    groupsdiv = et.SubElement(section, "div", {"class": "groups"})

    for match in stage['matches']:
        subsection = et.SubElement(groupsdiv, "div")
        subsection.append(create_matchbox(match))

        games_table = create_games_table(match['games'])
        details = wrap_details(games_table, summary="Games")
        subsection.append(details)

    return section

body.append(create_playin_round2_section(msi['stages'][1]))

def create_playin_round3_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    for match in stage['matches']:
        section.append(create_matchbox(match))

        games_table = create_games_table(match['games'])
        details = wrap_details(games_table, summary="Games")
        section.append(details)

    return section

body.append(create_playin_round3_section(msi['stages'][2]))

def create_group_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    section.append(create_group_table(stage['placements'], stage['winners']))

    teams = [row['team'] for row in stage['placements']]
    crosstable = compute_crosstable_from_games(teams, stage['games'])
    crosstable = create_crosstable(teams, crosstable)
    details = wrap_details(crosstable, summary="Crosstable")
    section.append(details)

    groupsdiv = et.Element("div", {"class": "groups"})
    for _, games in itertools.groupby(stage['games'], lambda g: g['label']):
        groupsdiv.append(create_games_table(games))
    details = wrap_details(groupsdiv, summary="Games")
    section.append(details)

    return section

body.append(create_group_stage_section(msi['stages'][3]))

def create_knockout_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    groupsdiv = et.SubElement(section, "div", {"class": "groups collapse-h3"})

    for match in stage['matches']:
        subsection = et.SubElement(groupsdiv, "div")
        et.SubElement(subsection, "h3").text = match['label']

        subsection.append(create_matchbox(match))

        games_table = create_games_table(match['games'])
        details = wrap_details(games_table, summary="Games")
        subsection.append(details)

    return section

body.append(create_knockout_stage_section(msi['stages'][4]))

out = sys.stdout.buffer
out.write(b"<!DOCTYPE html>\n")
out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
out.write(b"\n")
