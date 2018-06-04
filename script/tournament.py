from collections import OrderedDict
import xml.etree.ElementTree as et
import io
import itertools
import math

def wrap_details(*elements, summary=None):
    details = et.Element("details")
    if summary is not None:
        et.SubElement(details, "summary").text = summary
    details.extend(elements)
    return details

def create_teams_table(teams, labels={}):
    table = et.Element("table", {"class": "participants"})

    has_region = 'region' in teams[0]

    for i, team in enumerate(teams):
        if i in labels:
            tr = et.SubElement(table, "tr")
            et.SubElement(tr, "th", colspan="3").text = labels[i]

        if i == 0:
            tr = et.SubElement(table, "tr")
            if has_region:
                et.SubElement(tr, "th").text = "Region"
            et.SubElement(tr, "th").text = "ID"
            et.SubElement(tr, "th").text = "Team"

        tr = et.SubElement(table, "tr")
        if has_region:
            et.SubElement(tr, "td", {"class": "region"}).text = team["region"]
        et.SubElement(tr, "td", {"class": "teamabbr"}).text = team["abbr"]
        et.SubElement(tr, "td", {"class": "teamname"}).text = team["name"]

    return table

def compute_region_teams(teams):
    region_teams = OrderedDict()
    for team in teams:
        region = team['region']
        if region in region_teams:
            region_teams[region].append(team)
        else:
            region_teams[region] = [team]
    return region_teams

def create_region_teams_table(region_teams):
    table = et.Element("table", {"class": "participants"})

    tr = et.SubElement(table, "tr")
    et.SubElement(tr, "th").text = "Region"
    et.SubElement(tr, "th").text = "ID"
    et.SubElement(tr, "th").text = "Team"

    for region, teams in region_teams.items():
        for i, team in enumerate(teams):
            tr = et.SubElement(table, "tr")
            if i == 0:
                td = et.SubElement(tr, "td", {"class": "region"})
                if len(teams) > 1:
                    td.set("rowspan", str(len(teams)))
                td.text = region
            et.SubElement(tr, "td", {"class": "teamabbr"}).text = team["abbr"]
            et.SubElement(tr, "td", {"class": "teamname"}).text = team["name"]
    return table

def create_group_table(placements):
    ALL_KEYS = OrderedDict([
        ('wins', "W"),
        ('ties', "T"),
        ('losses', "L"),
        ('gamewins', "GW"),
        ('gamelosses', "GL"),
        ('points', "P"),
    ])

    keys = OrderedDict((k, v) for k, v in ALL_KEYS.items()
                              if k in placements[0])

    table = et.Element("table", {"class": "grouptable"})

    tr = et.SubElement(table, "tr")
    et.SubElement(tr, "th").text = "Place"
    et.SubElement(tr, "th").text = "Team"
    for text in keys.values():
        et.SubElement(tr, "th").text = text

    for row in placements:
        tr = et.SubElement(table, "tr")
        et.SubElement(tr, "td").text = str(row['place'])

        teamtd = et.SubElement(tr, "td")
        teamtd.text = row['team']['abbr']
        if 'class' in row:
            teamtd.set("class", row['class'])

        for key in keys:
            et.SubElement(tr, "td").text = str(row[key])
    return table

def compute_match_crosstable(teams, matches):
    crosstable = [[0] * len(teams) for _ in teams]
    for match in matches:
        team1, team2 = match['team1'], match['team2']
        i = teams.index(team1)
        j = teams.index(team2)
        if team1 == match['winner']:
            crosstable[i][j] += 1
        elif team2 == match['winner']:
            crosstable[j][i] += 1
    return crosstable

def compute_game_crosstable(teams, matches):
    crosstable = [[0] * len(teams) for _ in teams]
    for match in matches:
        team1, team2 = match['team1'], match['team2']
        i = teams.index(team1)
        j = teams.index(team2)
        crosstable[i][j] += match['score1']
        crosstable[j][i] += match['score2']
    return crosstable

def create_crosstable(teams, crosstable):
    table = et.Element("table", {"class": "crosstable"})
    tr = et.SubElement(table, "tr")
    for text in ["Team"] + [team['abbr'][0] for team in teams]:
        et.SubElement(tr, "th").text = text

    for i, team in enumerate(teams):
        tr = et.SubElement(table, "tr")
        et.SubElement(tr, "td").text = team['abbr']

        for j, team in enumerate(teams):
            if i == j:
                et.SubElement(tr, "td")
                continue

            wins = crosstable[i][j]
            losses = crosstable[j][i]
            clazz = ('won' if wins > losses else
                     'lost' if wins < losses else 'tied')
            et.SubElement(tr, "td", {"class": clazz}).text = str(wins)
    return table

def create_matchbox_tr(abbr1, score1, class1, abbr2, score2, class2):
    tr = et.Element("tr")
    et.SubElement(tr, "td").text = abbr1
    et.SubElement(tr, "td").text = str(score1)
    et.SubElement(tr, "td").text = str(score2)
    et.SubElement(tr, "td").text = abbr2
    if class1:
        tr[0].set("class", class1)
    if class2:
        tr[3].set("class", class2)
    return tr

def create_match_tr(match):
    team1, team2, winner = match['team1'], match['team2'], match['winner']
    if team1 == team2:
        raise ValueError('team 1 and team 2 must be different')
    abbr1, abbr2 = team1['abbr'], team2['abbr']

    if winner == team1:
        score1, score2, class1, class2 = 1, 0, 'won', 'lost'
    elif winner == team2:
        score1, score2, class1, class2 = 0, 1, 'lost', 'won'
    elif winner == 'tied':
        score1, score2, class1, class2 = 1, 1, 'tied', 'tied'
    elif winner is None:
        score1, score2, class1, class2 = 0, 0, None, None
    else:
        raise ValueError("winner must be either teams, 'tied' or None")

    if 'score1' in match:
        score1 = match['score1']
    if 'score2' in match:
        score2 = match['score2']
    if 'class1' in match:
        class1 = match['class1']
    if 'class2' in match:
        class2 = match['class2']

    return create_matchbox_tr(abbr1, score1, class1, abbr2, score2, class2)

def create_matches_table(matches):
    table = et.Element("table", {"class": "matchbox"})

    lastlabel = None
    for match in matches:
        label = match.get('label')
        if label is not None and (lastlabel is None or lastlabel != label):
            tr = et.SubElement(table, "tr")
            et.SubElement(tr, "th", colspan="4").text = label
            lastlabel = label

        tr = create_match_tr(match)
        table.append(tr)
    return table

def _extend_crosstable(section, teams, data, summary=None):
    crosstable = create_crosstable(teams, data)
    if summary is not None:
        crosstable = wrap_details(crosstable, summary=summary)
    section.append(crosstable)

def _extend_matches(section, matches, split_labels, summary=None):
    if split_labels:
        element = et.Element("div", {"class": "groups"})
        for _, part in itertools.groupby(matches, lambda g: g['label']):
            element.append(create_matches_table(part))
    else:
        element = create_matches_table(matches)
    if summary is not None:
        element = wrap_details(element, summary=summary)
    section.append(element)

def _extend_groups(section, groups):
    groupsdiv = et.SubElement(section, "div", {"class": "groups collapse-h3"})

    for group in groups:
        subsection = et.SubElement(groupsdiv, "section")
        et.SubElement(subsection, "h3").text = group['name']

        subsection.append(create_group_table(group["placements"]))

        teams = [row['team'] for row in group['placements']]
        data = compute_match_crosstable(teams, group['games'])
        _extend_crosstable(subsection, teams, data, "Crosstable")

        _extend_matches(subsection, group['games'], False, "Games")

def _extend_single_group(section, group):
    section.append(create_group_table(group['placements']))

    teams = [row['team'] for row in group['placements']]
    data = compute_match_crosstable(teams, group['games'])
    _extend_crosstable(section, teams, data, "Crosstable")

    _extend_matches(section, group['games'], True, "Games")

def _extend_single_bo3_group(section, group):
    section.append(create_group_table(group['placements']))

    teams = [row['team'] for row in group['placements']]
    data = compute_match_crosstable(teams, group['matches'])
    _extend_crosstable(section, teams, data, "Match Crosstable")

    data = compute_game_crosstable(teams, group['matches'])
    _extend_crosstable(section, teams, data, "Game Crosstable")

    _extend_matches(section, group['matches'], True, "Matches")

def create_group_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    if 'groups' in stage:
        _extend_groups(section, stage['groups'])
    else:
        _extend_single_group(section, stage)

    return section

def create_bo3_group_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    if 'groups' in stage:
        _extend_bo3_groups(section, stage['groups'])
    else:
        _extend_single_bo3_group(section, stage)

    return section

def create_matchbox(match):
    table = et.Element("table", {"class": "matchbox"})
    table.append(create_match_tr(match))
    return table

def _append_match(section, match):
    if 'label' in match:
        et.SubElement(section, "h3").text = match['label']

    section.append(create_matchbox(match))

    games_table = create_matches_table(match['games'])
    details = wrap_details(games_table, summary="Games")
    section.append(details)

def create_single_match_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']
    for match in stage['matches']:
        _append_match(section, match)
    return section

def create_knockout_stage_section(stage, image=None):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']
    if image is not None:
        section.append(image)

    clazz = "groups"
    if image is None and 'label' in stage['matches'][0]:
        clazz += " collapse-h3"
    groupsdiv = et.SubElement(section, "div", {"class": clazz})

    for match in stage['matches']:
        subsection = et.SubElement(groupsdiv, "div")
        _append_match(subsection, match)
    return section

def _points_to_str(point):
    if point is None:
        return ''
    if point == math.inf:
        return '\u221e'
    return str(point)

def _total_points(spring, summer):
    if spring is None:
        return summer
    if summer is None:
        return spring
    return spring + summer

def create_championship_points_table(placements):
    table = et.Element("table", {"class": "championship-points"})

    tr = et.SubElement(table, "tr")
    et.SubElement(tr, "th").text = "Team"
    et.SubElement(tr, "th").text = "Spring"
    et.SubElement(tr, "th").text = "Summer"
    et.SubElement(tr, "th").text = "Total"

    for row in placements:
        spring = row['spring']
        summer = row['summer']
        total = _total_points(spring, summer)

        tr = et.SubElement(table, "tr")
        et.SubElement(tr, "td").text = row['team']['abbr']
        et.SubElement(tr, "td").text = _points_to_str(spring)
        et.SubElement(tr, "td").text = _points_to_str(summer)
        et.SubElement(tr, "td").text = _points_to_str(total)

        if 'class' in row:
            tr[0].set("class", row['class'])
    return table

def create_championship_points_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']
    section.append(create_championship_points_table(stage['placements']))
    return section

def svg_to_image(svg, **attr):
    string_io = io.StringIO()
    et.ElementTree(svg).write(string_io, encoding="unicode")
    src = 'data:image/svg+xml,' + string_io.getvalue()
    return et.Element("img", src=src, **attr)

class HTMLGenerator:
    def generate(self, data):
        html = et.Element("html", lang="en")
        head = et.SubElement(html, "head")
        et.SubElement(head, "meta", charset="utf-8")
        et.SubElement(head, "title").text = data['abbr']
        et.SubElement(head, "meta", name="viewport",
                      content="width=device-width, initial-scale=1")
        et.SubElement(head, "link", rel="stylesheet", href="style.css")

        body = et.SubElement(html, "body")
        et.SubElement(body, "h1").text = data['name']
        body.append(self.generate_participants(data))
        body.extend(self.generate_stages(data))
        return html
    def generate_participants(self, data):
        teams_table = create_teams_table(data['teams'])
        details = wrap_details(teams_table, summary="Participants")
        teams = et.Element("div")
        teams.append(details)
        return teams
    def generate_stages(self, data):
        result = []
        for i, stage in enumerate(data['stages']):
            result.append(self.generate_stage(i, stage))
        return result
    def generate_stage(self, i, stage):
        section = et.Element("section")
        et.SubElement(section, "h2").text = stage['name']
        return section
