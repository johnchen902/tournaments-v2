import xml.etree.ElementTree as et
import itertools

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

def _extend_groups(section, groups):
    groupsdiv = et.SubElement(section, "div", {"class": "groups collapse-h3"})

    for group in groups:
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

def _extend_single_group(section, group):
    section.append(create_group_table(group['placements'], group['winners']))

    teams = [row['team'] for row in group['placements']]
    crosstable = compute_crosstable_from_games(teams, group['games'])
    crosstable = create_crosstable(teams, crosstable)
    details = wrap_details(crosstable, summary="Crosstable")
    section.append(details)

    groupsdiv = et.Element("div", {"class": "groups"})
    for _, games in itertools.groupby(group['games'], lambda g: g['label']):
        groupsdiv.append(create_games_table(games))
    details = wrap_details(groupsdiv, summary="Games")
    section.append(details)

def create_group_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    if 'groups' in stage:
        _extend_groups(section, stage['groups'])
    else:
        _extend_single_group(section, stage)

    return section

def create_matchbox(match):
    table = et.Element("table", {"class": "matchbox"})
    team1, team2, winner = match['team1'], match['team2'], match['winner']
    table.append(create_matchbox_tr(
            team1['abbr'], team1 == winner, str(match['score1']),
            team2['abbr'], team2 == winner, str(match['score2'])))
    return table

def _append_match(section, match):
    if 'label' in match:
        et.SubElement(section, "h3").text = match['label']

    section.append(create_matchbox(match))

    games_table = create_games_table(match['games'])
    details = wrap_details(games_table, summary="Games")
    section.append(details)

def create_single_match_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']
    for match in stage['matches']:
        _append_match(section, match)
    return section

def create_knockout_stage_section(stage):
    section = et.Element("section")
    et.SubElement(section, "h2").text = stage['name']

    clazz = "groups"
    if 'label' in stage['matches'][0]:
        clazz += " collapse-h3"
    groupsdiv = et.SubElement(section, "div", {"class": clazz})

    for match in stage['matches']:
        subsection = et.SubElement(groupsdiv, "div")
        _append_match(subsection, match)
    return section
