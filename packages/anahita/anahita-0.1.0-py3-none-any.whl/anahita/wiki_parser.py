from datetime import datetime
import re
import flatdict
import wikitextparser
from wikitextparser import WikiText


def remove_ref_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<ref.*?ref>')
    return re.sub(clean, '', text)


def extract_all_revisions_links(json_file):
    dic = {"page_name": json_file['title'].split(":")[-1], "revision": {}}
    for i in json_file['revision']:
        date_time_str = i['timestamp']
        date_time_obj = datetime.strptime(date_time_str,
                                          '%Y-%m-%dT%H:%M:%S.%f%z')
        if ('text' not in i) or '_VALUE' not in i['text']:
            dic["revision"][date_time_str] = []
            continue
        destination_pages = extract_links(i['text']['_VALUE'])
        dic["revision"][date_time_str] = destination_pages
    return dic


def extract_links(wikitext: str) -> list:
    links = re.findall('\[\[([^\]\]]*)\]\]', wikitext)
    destination_pages = []
    for link in links:
        if ":" in link:
            continue
        else:
            if "|" in link:
                destination_pages.append(link.split("|")[1])
            else:
                destination_pages.append(link)
    return destination_pages


def extract_infobox(wikitext: str) -> dict:
    parsed_wikitext = WikiText(wikitext)
    dic = {}
    for template in parsed_wikitext.templates:
        if "Infobox" in template.name:
            print(template.name)
            for arg in template.arguments:
                dic[arg.name.strip()] = arg.value
    return dic


def extract_infobox_properties(wikitext: str) -> dict:
    parsed_wikitext = WikiText(wikitext)
    dic = {}
    for template in parsed_wikitext.templates:
        if "Infobox" in template.name:
            print(template.name)
            # for arg in template.arguments:
            #     dic[arg.name.strip()] = WikiText(arg.value).plain_text().strip()
            dic = template_properties(template)
            break
    d = flatdict.FlatDict(dic, delimiter='.')
    return dict(d)


def template_properties(template: wikitextparser.Template) -> dict:
    dic = {}
    for arg in template.arguments:
        if len(arg.templates) == 0 and len(arg.wikilinks) == 0:
            dic[arg.name.strip()] = arg.value.strip()
        elif len(arg.templates) == 0 and len(arg.wikilinks) != 0:
            dic[arg.name.strip()] = WikiText(arg.value.strip()).plain_text()
        elif len(arg.templates) > 0:
            c = 1
            for temp in arg.templates:
                if temp.nesting_level == template.nesting_level + 1:
                    if f"{arg.name.strip()}.{temp.name}" in dic:
                        property_key = f"{arg.name.strip()}.{temp.name}{c}"
                        c += 1
                    else:
                        property_key = f"{arg.name.strip()}.{temp.name}"
                    dic[property_key] = template_properties(temp)
        else:
            print("Not defined")
    return dic
