from html5lib.serializer import serialize
import itertools
import sys
import xml.etree.ElementTree as et
import yaml

import tournament

msi = yaml.safe_load(open('msi-2018.yaml'))

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

teams_table = tournament.create_teams_table(msi['teams'], labels = {
    0: "Main Event Seeds",
    4: "Play-In Round 2 Seeds",
    6: "Play-In Round 1 Seeds (Pool 1)",
    10: "Play-In Round 1 Seeds (Pool 2)",
})
teams_div = et.SubElement(body, "div")
details = tournament.wrap_details(teams_table, summary="Participants")
teams_div.append(details)


body.append(tournament.create_group_stage_section(msi['stages'][0]))
body.append(tournament.create_knockout_stage_section(msi['stages'][1]))
body.append(tournament.create_group_stage_section(msi['stages'][2]))
body.append(tournament.create_knockout_stage_section(msi['stages'][3]))

out = sys.stdout.buffer
out.write(b"<!DOCTYPE html>\n")
out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
out.write(b"\n")
