import xml.etree.ElementTree as et

import playoffs_svg
import tournament

class MSI2016Generator(tournament.HTMLGenerator):
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
    html = MSI2016Generator().generate(data)

    out = sys.stdout.buffer
    out.write(b"<!DOCTYPE html>\n")
    out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
    out.write(b"\n")
