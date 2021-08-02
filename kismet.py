"""Kismet wrapper"""

import os

import requests
from dotenv import load_dotenv
from jsonpath import JSONPath
import json


class Kismet:
    def __init__(self, config):
        self.config = config


def dump_kismet_data(self):
    with open('kismet_response.json', 'w') as file:
        json.dump(self.kismet_response(),
                  file,
                  ensure_ascii=False,
                  sort_keys=True,
                  indent=2)

    def url(self):
        """ generate kismet url using ENVVARS to fetch credentials """
        load_dotenv()
        kismet_info = [
            os.environ["KISMET_USER"], os.environ["KISMET_PASSWORD"],
            os.environ["KISMET_IP"]
        ]
        host = "{user}:{password}@{ip}:2501".format(*kismet_info)
        return "http://{0}/devices/views/all/devices.json".format(host)

    def kismet_response(self):
        """ fetch data from kismet endpoint in json format """
        try:
            response = requests.get(self.url()).json()
            return {'ok': response} if response else {'error': 'no_data'}
        except requests.exceptions.RequestException:
            return {'error': {'kismet': 'offline'}}

    def valid_data(self, network_data):
        """verify existence of all fields with non-empty value"""
        attrs = self.config.jsonpaths().keys()
        return all(map(lambda attr: network_data[attr], attrs))

    def network_data(self, response):
        """ the network data with all attributes filleds """
        queries = {
            attr: JSONPath(query)
            for attr, query in self.config.jsonpaths().items()
        }

        def sanitize(attr_value):
            return attr_value.pop() if attr_value else ""

        def extract_network_data(kismet_item):
            return {
                attribute: sanitize(jsonpath.parse(kismet_item))
                for attribute, jsonpath in queries.items()
            }

        return filter(self.valid_data, map(extract_network_data, response))
