"""" kismet data extract """

import json
import os
from collections import ChainMap

import requests
import yaml
from dotenv import load_dotenv
from jsonpath import JSONPath


def dump_kismet_data():
    with open('kismet_response.json', 'w') as file:
        json.dump(kismet_response(),
                  file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=2)


def config_file_content():
    """ config in json """
    with open('config.yml') as content:
        return yaml.safe_load(content)


def wrap_segments(path):
    """ wrap all jsonpath segments with single quotes """
    return map(lambda segment: "'{s}'".format(s=segment), path)


def jsonpath(path):
    """ generate jsonpath string """
    return '.'.join(["$"] + list(wrap_segments(path)))


def realpaths(entry):
    """ concatenate the base segment with the attr segment """
    base = entry['base']
    paths = entry['fields']

    def path(attr_name):
        return base + [paths[attr_name]]

    def jpaths(attr):
        return (attr, jsonpath(path(attr)))

    return dict(map(jpaths, paths.keys()))


def jsonpaths():
    """ all generate jsonpaths contained in config file """
    cfg = config["kismet"]
    groups = cfg.keys()

    def paths_from_group(group):
        return realpaths(cfg[group])

    return dict(ChainMap(*map(paths_from_group, groups)))


def url():
    """ generate kismet url using ENVVARS to fetch credentials """
    u = os.environ["KISMET_USER"]
    p = os.environ["KISMET_PASSWORD"]
    i = os.environ["KISMET_IP"]
    host = "{user}:{password}@{ip}:2501".format(user=u, password=p, ip=i)

    return "http://{host}/devices/views/all/devices.json".format(host=host)


def kismet_response():
    """ fetch data from kismet endpoint in json format """
    response = {}
    try:
        response = requests.get(url()).json()
        response = {'ok': response} if response else {'error': 'no_data'}
    except requests.exceptions.RequestException:
        response = {'error': {'kismet': 'offline'}}
    return response


def network_data(response):
    """ the networj data with all attributes filleds """
    queries = {attr: JSONPath(query) for attr, query in jsonpaths().items()}

    def sanitize(attr_value):
        return attr_value.pop() if attr_value else ""

    def extract_network_data(kismet_item):
        return {
            attribute: sanitize(jsonpath.parse(kismet_item))
            for attribute, jsonpath in queries.items()
        }

    return filter(valid_data, map(extract_network_data, response))


def valid_data(network_data):
    """verify existence of all fields with non-empty value"""
    return all(map(lambda attr: network_data[attr], jsonpaths().keys()))


def main():
    """ main function """
    # use local .env to override ENVVARS
    load_dotenv()
    resp = kismet_response()
    return resp['error'] if 'error' in resp else list(network_data(resp['ok']))


if __name__ == "__main__":
    config = config_file_content()
    print(main())
