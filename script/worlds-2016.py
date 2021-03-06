import xml.etree.ElementTree as et

import tournament
import playoffs_svg

class Worlds2016Generator(tournament.HTMLGenerator):
    def generate_participants(self, data):
        teams = data['teams']
        teams_table = tournament.create_teams_table(teams, labels = {
            0: "Pool 1",
            4: "Pool 2",
            12: "Pool 3",
        })
        details = tournament.wrap_details(teams_table,
                                          summary="Participants (by pool)")
        div = et.Element("div")
        div.append(details)

        region_teams = tournament.compute_region_teams(teams)
        region_teams_table = tournament.create_region_teams_table(region_teams)
        details = tournament.wrap_details(region_teams_table,
                                          summary="Participants (by region)")
        div.append(details)
        return div
    def generate_stage(self, i, stage):
        if i == 0:
            return tournament.create_group_stage_section(stage)
        if i == 1:
            svg = playoffs_svg.create_single_elimination_svg(stage['matches'])
            image = tournament.svg_to_image(svg, alt="")
            return tournament.create_knockout_stage_section(stage, image=image)

if __name__ == '__main__':
    from html5lib.serializer import serialize
    import sys
    import yaml

    data = yaml.safe_load(sys.stdin)
    html = Worlds2016Generator().generate(data)

    out = sys.stdout.buffer
    out.write(b"<!DOCTYPE html>\n")
    out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
    out.write(b"\n")
