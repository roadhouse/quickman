"""" kismet data extract """

import json
import os
from collections import ChainMap

import requests
import yaml
from dotenv import load_dotenv
from jsonpath import JSONPath


def dump_kistmet_data():
    """ dump kismet data in formated file """
    with open('kismet_response.json', 'w') as file:
        json.dump(kismet_data(),
                  file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=2)


def config():
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
    path = lambda attr_name: base + [paths[attr_name]]
    return dict(map(lambda attr: [attr, jsonpath(path(attr))], paths.keys()))


def jsonpaths():
    """ all generate jsonpaths contained in config file """
    cfg = config["kismet"]
    return dict(
        ChainMap(*map(lambda group: realpaths(cfg[group]), cfg.keys())))


def extract_data(data_node):
    """ parse data from each node in data """
    return dict(
        map(lambda attr, query: [attr, parse_data(query, data_node)],
            jsonpaths().keys(),
            jsonpaths().values()))


def parse_data(query, kismet_json):
    """ return jsonpath return value """
    result = JSONPath(query).parse(kismet_json)
    return "" if not result else result.pop()


def url():
    """ generate kismet url using ENVVARS to fetch credentials """
    return "http://{user}:{password}@127.0.0.1:2501/devices/views/all/devices.json".format(
        user=os.environ["KISMET_USER"], password=os.environ["KISMET_PASSWORD"])


def kismet_response():
    """ fetch data from kismet endpoint in json format """
    response = {}
    try:
        response = requests.get(url()).json()
        response = {'ok': response} if response else {'error': 'no_data'}
    except requests.exceptions.RequestException as exception:
        response = {'error': {'kismet': 'offline', 'response': exception}}
    return response


def data(response):
    """ the networj data with all attributes filleds """
    return filter(valid_data, map(extract_data, response))


def valid_data(network_data):
    """verify existence of all fields with non-empty value"""
    return all(map(lambda attr: network_data[attr], jsonpaths().keys()))


config = config()


def main():
    """ main function """
    # use local .env to override ENVVARS
    load_dotenv()
    resp = kismet_response()
    return resp['error'] or list(data(resp))
