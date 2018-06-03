import xml.etree.ElementTree as et

import tournament
import playoffs_svg

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
            svg = playoffs_svg.create_single_elimination_svg(stage['matches'])
            image = tournament.svg_to_image(svg, alt="")
            return tournament.create_knockout_stage_section(stage, image=image)

if __name__ == '__main__':
    from html5lib.serializer import serialize
    import sys
    import yaml

    data = yaml.safe_load(sys.stdin)
    html = MSI2018Generator().generate(data)

    out = sys.stdout.buffer
    out.write(b"<!DOCTYPE html>\n")
    out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
    out.write(b"\n")
