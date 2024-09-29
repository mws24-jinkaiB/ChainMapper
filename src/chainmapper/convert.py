import xml.etree.ElementTree as ET
import Evtx.Evtx as evtx
import sys
import yaml
import json
import argparse

ascii_art = r'''
   ___ _           _                                          
  / __\ |__   __ _(_)_ __   /\/\   __ _ _ __  _ __   ___ _ __ 
 / /  | '_ \ / _` | | '_ \ /    \ / _` | '_ \| '_ \ / _ \ '__|
/ /___| | | | (_| | | | | / /\/\ \ (_| | |_) | |_) |  __/ |   
\____/|_| |_|\__,_|_|_| |_\/    \/\__,_| .__/| .__/ \___|_|   
                                       |_|   |_|              
'''


def is_json(myjson):
    # check if myjson = <string>json</string>
    try:
        myjson = myjson.replace("<string>", "")
        myjson = myjson.replace("</string>", "")
        _ = json.loads(myjson)
    except ValueError as e:
        return False
    return True


def parse_json(myjson):
    # parse json string
    myjson = myjson.replace("<string>", "")
    myjson = myjson.replace("</string>", "")
    json_object = json.loads(myjson)
    return get_string_keys(json_object)


def get_string_keys(d, parent_key=''):
    keys = []
    for k, v in d.items():
        new_key = f"{parent_key}.{k}" if parent_key else k
        if isinstance(v, str):
            keys.append(new_key)
        elif isinstance(v, dict):
            keys.extend(get_string_keys(v, new_key))
    return keys


def get_eventdata_paths(element, parent_path="", index=0):
    paths = []
    json_paths = []

    tag = element.tag
    # remove namespace
    if "}" in tag:
        tag = tag.split("}", 1)[1]

    sibling_count = 1
    if element.getparent() is not None:
        sibling_count = sum(
            1 for sibling in element.getparent() if sibling.tag == element.tag
        )

    if "Name" in element.attrib:
        # <Hoge Name="Fuga"> => Fuga
        # <Provider Name="Fuga"> => Provider
        if parent_path:
            if tag == "Provider":
                full_key = f"{parent_path}.{tag}"
            else:
                full_key = f"{parent_path}.{element.attrib['Name']}"
        else:
            full_key = f"{element.attrib['Name']}"
        paths.append(full_key)
    else:
        if sibling_count > 1 or tag == "Data":
            # <Hoge></Hoge><Hoge></Hoge> => Hoge[0], Hoge[1]
            index = list(element.getparent()).index(element)
            if is_json(element.text):
                json_keys = parse_json(element.text)
                for key in json_keys:
                    json_paths.append(
                        (f"{key}", f"{parent_path}.{tag}[{index}]"))
            else:
                full_key = f"{parent_path}.{tag}[{index}]"
                if element.text and element.text.strip():
                    paths.append(f"{full_key}")
        else:
            # <Hoge> => Hoge
            if parent_path:
                full_key = f"{parent_path}.{tag}"
            else:
                full_key = f"{tag}"
            if element.text and element.text.strip():
                paths.append(f"{full_key}")

    for i, child in enumerate(element):
        child_paths, child_json_paths = get_eventdata_paths(child, full_key, i)
        paths.extend(child_paths)
        json_paths.extend(child_json_paths)

    return paths, json_paths


def chainmapper(file_name):
    with evtx.Evtx(file_name) as log:
        dict = {}
        json_dict = {}
        for record in log.records():
            elm = record.lxml()
            ns = {"ns": "http://schemas.microsoft.com/win/2004/08/events/event"}

            providers = elm.xpath("//ns:Provider/@Name", namespaces=ns)
            data_paths, json_paths = get_eventdata_paths(elm)
            for data_path in data_paths:
                if providers[0] not in dict:
                    dict[providers[0]] = {}
                    dict[providers[0]][data_path] = 1
                else:
                    dict[providers[0]][data_path] = 1
            for json_path in json_paths:
                if providers[0] not in json_dict:
                    json_dict[providers[0]] = {}
                    json_dict[providers[0]][json_path] = 1
                else:
                    json_dict[providers[0]][json_path] = 1

    yml = {
        "name": "mappings file",
        "kind": "evtx",
        "rules": "sigma",
        "extensions": {"preconditions": []},
        "groups": [],
    }
    for provider, data in dict.items():
        yml["extensions"]["preconditions"].append({})
        yml["extensions"]["preconditions"][-1]["for"] = {
            "logsource.category": str(provider)
        }
        yml["extensions"]["preconditions"][-1]["filter"] = {
            "Provider": str(provider)}
        yml["groups"].append(
            {
                "name": str(provider),
                "timestamp": "Event.System.TimeCreated",
                "filter": {"Provider": str(provider)},
                "fields": [],
            }
        )
        for key in data.keys():
            yml["groups"][-1]["fields"].append({})
            yml["groups"][-1]["fields"][-1]["from"] = key.split(".")[-1]
            yml["groups"][-1]["fields"][-1]["to"] = key
            yml["groups"][-1]["fields"][-1]["visible"] = False

        if provider in json_dict:
            for key in json_dict[provider].keys():
                yml["groups"][-1]["fields"].append({})
                yml["groups"][-1]["fields"][-1]["container"] = {}
                yml["groups"][-1]["fields"][-1]["container"]["field"] = key[1]
                yml["groups"][-1]["fields"][-1]["container"]["format"] = "json"
                # duplicate key (todo)
                if key[0].split(".")[-1] in [field.get("from", None) for field in yml["groups"][-1]["fields"]]:
                    yml["groups"][-1]["fields"][-1]["from"] = f"{key[0].split('.')[-1]}_json"
                else:
                    yml["groups"][-1]["fields"][-1]["from"] = key[0].split(".")[-1]
                yml["groups"][-1]["fields"][-1]["to"] = key[0]
                yml["groups"][-1]["fields"][-1]["visible"] = False

    with open("mappings.yaml", "w") as f:
        yaml.dump(yml, f, default_flow_style=False, allow_unicode=True)

def main():
    print(f'{ascii_art}')
    parser = argparse.ArgumentParser(
        description=f'this script generates a mappings file for evtx files')
    parser.add_argument('evtx_file', metavar='evtx_file', help='input evtx file')

    args = parser.parse_args()

    chainmapper(args.evtx_file)

if __name__ == "__main__":
    main()