import requests
import os
import yaml
from jsonpath import JSONPath
from dotenv import load_dotenv
from collections import ChainMap

def config():
    with open('config.yml') as content:
        return yaml.safe_load(content)

def wrap_segments(path):
    return map(lambda segment: "'{s}'".format(s=segment), path)

def complete_path(path):
    return '.'.join(["$"] + list(wrap_segments(path)))

def entries_full_paths(entry):
    base = entry['base']
    attrs = entry['fields']
    return dict(map(
        lambda attr: [attr, complete_path(base + [attrs[attr]])],
        attrs.keys()
    ))

def all_complete_paths():
    c = config["kismet"]
    return ChainMap(*map(lambda group: entries_full_paths(c[group]), c.keys()))

def extract_data(data):
    return dict(map(
        lambda attr, query: [attr, "".join(JSONPath(query).parse(data))],
        all_complete_paths().keys(),
        all_complete_paths().values()
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
    return all(map(lambda attr: network_data[attr], all_complete_paths().keys()))

config = config()
def main():
    # use local .env to override ENVVARS
    load_dotenv()

    kismet_response = kismet_data() or {'error': {'kismet': 'no data'}}

    return kismet_response['error'] or network_data(kismet_response)
