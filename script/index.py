import xml.etree.ElementTree as et

def create_index(data, pages):
    html = et.Element("html", lang="en")
    head = et.SubElement(html, "head")
    et.SubElement(head, "meta", charset="utf-8")
    et.SubElement(head, "title").text = "LoL Tournament Results"
    et.SubElement(head, "meta", name="viewport",
                  content="width=device-width, initial-scale=1")
    et.SubElement(head, "link", rel="stylesheet", href="style.css")

    body = et.SubElement(html, "body")
    et.SubElement(body, "h1").text = "League of Legends Tournament Results"

    table = et.SubElement(html, "table")
    for tournament in data:
        tr = et.SubElement(table, "tr")

        th = et.SubElement(tr, "th")
        abbr = et.SubElement(th, "abbr", title=tournament['name'])
        abbr.text = tournament['abbr']

        lastyear = 2011
        for season in tournament['seasons']:
            if lastyear < season['year']:
                et.SubElement(tr, "td", colspan=str(season['year'] - lastyear))
                lastyear = season['year']

            td = et.SubElement(tr, "td")
            anchor = season.get('anchor', str(season['year']))
            if season['href'] in pages:
                et.SubElement(td, "a", href=season['href']).text = anchor
            else:
                td.text = anchor
            lastyear += 1
    return html

if __name__ == '__main__':
    from html5lib.serializer import serialize
    import os
    import sys
    import yaml

    pages = set(os.listdir(sys.argv[1]))

    data = yaml.safe_load(sys.stdin)
    html = create_index(data, pages)

    out = sys.stdout.buffer
    out.write(b"<!DOCTYPE html>\n")
    out.write(serialize(html, encoding='ascii', inject_meta_charset=False))
    out.write(b"\n")
