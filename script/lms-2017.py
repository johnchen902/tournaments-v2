import xml.etree.ElementTree as et

import tournament
import playoffs_svg

class Worlds2015Generator(tournament.HTMLGenerator):
    def generate_participants(self, data):
        spring_teams = data['spring_teams']
        spring_teams_table = tournament.create_teams_table(spring_teams)
        details = tournament.wrap_details(spring_teams_table,
                                          summary="Spring Participants")
        div = et.Element("div")
        div.append(details)

        summer_teams = data['summer_teams']
        summer_teams_table = tournament.create_teams_table(summer_teams)
        details = tournament.wrap_details(summer_teams_table,
                                          summary="Summer Participants")
        div.append(details)
        return div
    def generate_stage(self, i, stage):
        if i in (0, 2):
            return tournament.create_bo3_group_stage_section(stage)
        if i in (1, 3):
            svg = playoffs_svg.create_gauntlet_svg(stage['matches'])
            image = tournament.svg_to_image(svg, alt="")
            return tournament.create_knockout_stage_section(stage, image=image)
        if i == 4:
            return tournament.create_championship_points_section(stage)
        if i == 5:
            svg = playoffs_svg.create_single_elimination_svg(stage['matches'])
            image = tournament.svg_to_image(svg, alt="")
            return tournament.create_knockout_stage_section(stage, image=image)

if __name__ == '__main__':
    from html5lib.serializer import serialize
    import sys
    import yaml

    data = yaml.safe_load(sys.stdin)
    html = Worlds2015Generator().generate(data)

    out = sys.stdout.buffer
    out.write(b"<!DOCTYPE html>\n")
    out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
    out.write(b"\n")
