import json
import os
import requests
import yaml
from collections import ChainMap
from dotenv import load_dotenv
from jsonpath import JSONPath

def dump_kistmet_data():
    with open('kismet_response.json', 'w') as f:
      json.dump(kismet_data(), f, ensure_ascii=False, sort_keys = True, indent = 2)

def config():
    with open('config.yml') as content:
        return yaml.safe_load(content)

def wrap_segments(path):
    return map(lambda segment: "'{s}'".format(s=segment), path)

def jsonpath(path):
    return '.'.join(["$"] + list(wrap_segments(path)))

def full_paths(entry):
    base = entry['base']
    attrs = entry['fields']
    complete_path = lambda attr_name: base + [attrs[attr_name]]
    return dict(map(
        lambda attr: [attr, jsonpath(complete_path(attr))],
        attrs.keys()
    ))

def jsonpaths():
    c = config["kismet"]
    return dict(ChainMap(*map(lambda group: full_paths(c[group]), c.keys())))

def extract_data(data):
    attr_and_data = lambda query: "".join(JSONPath(query).parse(data))
    return dict(map(
        lambda attr, query: [attr, attr_and_data(query)],
        jsonpaths().keys(),
        jsonpaths().values()
    ))

def url():
    return "http://{user}:{password}@127.0.0.1:2501/devices/views/all/devices.json".format(
        user = os.environ["KISMET_USER"],
        password = os.environ["KISMET_PASSWORD"]
    )

def kismet_data():
    response = {}
    try:
        response = requests.get(url()).json()
    except Exception as e:
        response = {'error': {'kismet': 'offline', 'response': e}}
    return response

def network_data(kismet_response):
    return filter(valid_data, map(extract_data, kismet_response))

def valid_data(network_data):
    """verify existence of all fields with non-empty value"""
    return all(map(lambda attr: network_data[attr], jsonpaths().keys()))

config = config()
def main():
    # use local .env to override ENVVARS
    load_dotenv()
    resp = kismet_data() or {'error': {'kismet': 'no data'}}
    return list(network_data(resp)) if isinstance(resp, list) else resp['error']
