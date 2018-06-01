from collections import OrderedDict
import yaml

msi = yaml.safe_load(open('msi-2018.yaml'))
# print(msi)

print("""<!DOCTYPE html>
<html>
<head>
<title>"""  + msi['abbr'] + """</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="style.css">
<style>
#participants td:nth-child(3) {
    text-align: left;
    padding-left: 1em;
    padding-right: 1em;
}
</style>
</head>
<body>
<h1>""" + msi['name'] + """</h1>""")

teams = msi['teams']
print("<section>")
print("<details>")
print("<summary>Participants</summary>")
print("<table id=\"participants\">")
print("<tr colspan=3><th colspan=3>Main Event Seeds</th></tr>")
print("<tr><th>Region<th>Team<th>Full Team Name</tr>")
for team in teams[:4]:
    print("<tr><td>%(region)s<td>%(abbr)s<td>%(name)s</tr>" % team)
print("<tr colspan=3><th colspan=3>Play-In Round 2 Seeds</th></tr>")
for team in teams[4:6]:
    print("<tr><td>%(region)s<td>%(abbr)s<td>%(name)s</tr>" % team)
print("<tr colspan=3><th colspan=3>Play-In Round 1 Seeds (Pool 1)</th></tr>")
for team in teams[6:10]:
    print("<tr><td>%(region)s<td>%(abbr)s<td>%(name)s</tr>" % team)
print("<tr colspan=3><th colspan=3>Play-In Round 1 Seeds (Pool 2)</th></tr>")
for team in teams[10:]:
    print("<tr><td>%(region)s<td>%(abbr)s<td>%(name)s</tr>" % team)
print("</table>")
print("</details>")
print("</section>")

playin1 = msi['stages'][0]
assert playin1['name'] == 'Play-In Round 1'
print("<section>")
print("<h2>%(name)s</h2>" % playin1)
print("<div class=\"groups collapse-h3\">")
for group in playin1['groups']:
    print('<section>')
    print('<h3>%s</h3>' % group['name'])
    print('<table class="grouptable">')
    print('<tr><th>Place<th>Team<th>W<th>L</tr>')
    for team in group['placements']:
        print('<tr><td>%d<td class="%s">%s<td>%d<td>%d</tr>' % 
                (team['place'], 'won' if team['place'] <= 1 else 'lost',
                 team['team']['abbr'], team['wins'], team['losses']))
    print('</table>')

    teams = [team['team'] for team in group['placements']]
    crosstable = [[{'wins': 0, 'losses': 0} for _ in teams] for _ in teams]
    for game in group['games']:
        blue, red = game['blue'], game['red']
        i = teams.index(blue)
        j = teams.index(red)
        if blue == game['winner']:
            crosstable[i][j]['wins'] += 1
            crosstable[j][i]['losses'] += 1
        elif red == game['winner']:
            crosstable[j][i]['wins'] += 1
            crosstable[i][j]['losses'] += 1

    print('<details>')
    print('<summary>Crosstable</summary>')
    print('<table class="crosstable">')
    print('<tr><th>Team<th>' +
            '<th>'.join(team['abbr'] for team in teams) + '</tr>')
    for i, team in enumerate(teams):
        print('<tr><td>%(abbr)s' % team +
                ''.join('<td>' if i == j else '<td class="%s">%d&ndash;%d' %
                        ('won' if wl['wins'] > wl['losses'] else
                         'lost' if wl['losses'] > wl['wins'] else
                         'tied', wl['wins'], wl['losses'])
                        for j, wl in enumerate(crosstable[i])) + '</tr>')

    print('</table>')
    print('</details>')

    print('<details>')
    print('<summary>Games</summary>')
    print('<table class="matchbox">')
    lastlabel = None
    for game in group['games']:
        if lastlabel is None or lastlabel != game['label']:
            print('<tr><th colspan=4>%s</tr>' % game['label'])
            lastlabel = game['label']
        blue, red = game['blue'], game['red']
        print('<tr><td class="%s">%s<td>%d<td>%d<td class="%s">%s</tr>' % 
                ('won' if blue == game['winner'] else 'lost',
                 blue['abbr'],
                 int(blue == game['winner']),
                 int(red == game['winner']),
                 'won' if red == game['winner'] else 'lost',
                 red['abbr']))
    print('</table>')
    print('</details>')
    print('</section>')
print("</div>")
print("</section>")

playin2 = msi['stages'][1]
assert playin2['name'] == 'Play-In Round 2'
print("<section>")
print("<h2>%(name)s</h2>" % playin2)
print("<div class=\"groups\">")
for match in playin2['matches']:
    team1, team2 = match['team1'], match['team2']
    print("<div>")
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

groupstage = msi['stages'][2]
assert groupstage['name'] == 'Group Stage'
print("<section>")
print("<h2>%(name)s</h2>" % groupstage)

print('<table class="grouptable">')
print('<tr><th>Place<th>Team<th>W<th>L</tr>')
for team in groupstage['placements']:
    print('<tr><td>%d<td class="%s">%s<td>%d<td>%d</tr>' % 
            (team['place'], 'won' if team['place'] <= 4 else 'lost',
             team['team']['abbr'], team['wins'], team['losses']))
print('</table>')

teams = [team['team'] for team in groupstage['placements']]
crosstable = [[{'wins': 0, 'losses': 0} for _ in teams] for _ in teams]
for game in groupstage['games']:
    blue, red = game['blue'], game['red']
    i = teams.index(blue)
    j = teams.index(red)
    if blue == game['winner']:
        crosstable[i][j]['wins'] += 1
        crosstable[j][i]['losses'] += 1
    elif red == game['winner']:
        crosstable[j][i]['wins'] += 1
        crosstable[i][j]['losses'] += 1

print('<details>')
print('<summary>Crosstable</summary>')
print('<table class="crosstable">')
print('<tr><th>Team<th>' +
        '<th>'.join(team['abbr'] for team in teams) + '</tr>')
for i, team in enumerate(teams):
    print('<tr><td>%(abbr)s' % team +
            ''.join('<td>' if i == j else '<td class="%s">%d&ndash;%d' %
                    ('won' if wl['wins'] > wl['losses'] else
                     'lost' if wl['losses'] > wl['wins'] else
                     'tied', wl['wins'], wl['losses'])
                    for j, wl in enumerate(crosstable[i])) + '</tr>')

print('</table>')
print('</details>')

print('<details>')
print('<summary>Games</summary>')
print("<div class=\"groups\">")
print('<table class="matchbox">')
lastlabel = None
for game in groupstage['games']:
    if lastlabel is None or lastlabel != game['label']:
        if lastlabel is not None:
            print('</table>')
            print('<table class="matchbox">')
        print('<tr><th colspan=4>%s</tr>' % game['label'])
        lastlabel = game['label']
    blue, red = game['blue'], game['red']
    print('<tr><td class="%s">%s<td>%d<td>%d<td class="%s">%s</tr>' % 
            ('won' if blue == game['winner'] else 'lost',
             blue['abbr'],
             int(blue == game['winner']),
             int(red == game['winner']),
             'won' if red == game['winner'] else 'lost',
             red['abbr']))
print('</table>')
print("</div>")
print('</details>')
print("</section>")

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

print("</body>")
print("</html>")
