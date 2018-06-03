import xml.etree.ElementTree as et

def create_index(data, pages):
    html = et.Element("html", lang="en")
    head = et.SubElement(html, "head")
    et.SubElement(head, "meta", charset="utf-8")
    et.SubElement(head, "title").text = "LoL Tournament Results"
    et.SubElement(head, "meta", name="viewport",
                  content="width=device-width, initial-scale=1")
    et.SubElement(head, "link", rel="stylesheet", href="style.css")
    et.SubElement(head, "style").text = """
        #tournament-list > section {
            margin-top: 1ch;
            margin-bottom: 1ch;
        }
        #tournament-list > section > h2 {
            display: inline;
            font-size: 120%;
        }
        #tournament-list > section > h2::after {
            content: ": ";
        }
        .touchable {
            display: inline-block;
            padding: 0.5ch 1ch;
            background-color: #eee;
            color: #000;
            border-radius: 1ch;
        }
    """

    body = et.SubElement(html, "body")
    et.SubElement(body, "h1").text = "League of Legends Tournament Results"

    div = et.SubElement(html, "div", {"id": "tournament-list"})
    for tournament in data:
        section = et.SubElement(div, "section")

        h2 = et.SubElement(section, "h2")
        h2.text = tournament['abbr']
        h2.tail = tournament['name']
        et.SubElement(section, "br")

        for season in tournament['seasons']:
            span = et.SubElement(section, "span", {"class": "touchable"})
            anchor = season.get('anchor', str(season['year']))
            if season['href'] in pages:
                et.SubElement(span, "a", href=season['href']).text = anchor
            else:
                span.text = anchor
            span.tail = " "
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
