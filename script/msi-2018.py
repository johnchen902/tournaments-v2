import xml.etree.ElementTree as et

import tournament

class MSI2018Generator(tournament.HTMLGenerator):
    def generate_participants(self, data):
        teams_table = tournament.create_teams_table(data['teams'], labels = {
            0: "Main Event Seeds",
            4: "Play-In Round 2 Seeds",
            6: "Play-In Round 1 Seeds (Pool 1)",
            10: "Play-In Round 1 Seeds (Pool 2)",
        })
        details = tournament.wrap_details(teams_table, summary="Participants")
        teams = et.Element("div")
        teams.append(details)
        return teams
    def generate_stage(self, i, stage):
        if i in (0, 2):
            return tournament.create_group_stage_section(stage)
        if i == 1:
            return tournament.create_knockout_stage_section(stage)
        if i == 3:
            image = et.Element("img", src="msi-2018.svg", alt="")
            return tournament.create_knockout_stage_section(stage, image=image)

if __name__ == '__main__':
    from html5lib.serializer import serialize
    import os
    import sys
    import yaml

    import playoffs_svg

    datadir = os.getenv('DATADIR', '../data')
    htmldir = os.getenv('HTMLDIR', '../html')

    data = yaml.safe_load(open(datadir + '/msi-2018.yaml'))
    html = MSI2018Generator().generate(data)

    with open(htmldir + '/msi-2018.html', 'wb') as out:
        out.write(b"<!DOCTYPE html>\n")
        out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
        out.write(b"\n")

    matches = data['stages'][3]['matches']
    svg = playoffs_svg.create_single_elimination_svg(matches)

    with open(htmldir + '/msi-2018.svg', 'wb') as out:
        et.ElementTree(svg).write(out)
        out.write(b"\n")
