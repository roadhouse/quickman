import requests
import os
from jsonpath import JSONPath
from dotenv import load_dotenv

base_path = [
    "$",
    "'dot11.device'",
    "'dot11.device.last_beaconed_ssid_record'",
]

attributes_paths =  {
    "ssid": "'dot11.advertisedssid.ssid'",
    "channel": "'dot11.advertisedssid.channel'",
}

def jsonpath(entry):
    return ".".join(base_path + [entry])

full_paths = dict(zip(
    attributes_paths.keys(),
    map(lambda entry: jsonpath(entry), attributes_paths.values())
))

def extract_data(data):
    return dict(zip(
        full_paths.keys(),
        map(lambda q: "".join(JSONPath(q).parse(data)), full_paths.values())
    ))

def url():
    return "http://{user}:{password}@127.0.0.1:2501/devices/views/all/devices.json".format(
        user = os.environ["KISMET_USER"],
        password = os.environ["KISMET_PASSWORD"]
    )

def kismet_data():
    response = ""
    try:
        response = requests.get(url()).json()
    except Exception as e:
        response = {'error': {'message': 'kismet down', 'response': e}}
    return response

def network_data(kismet_response):
    return filter(valid_data, map(extract_data, kismet_response))


def network_attributes():
    return ['ssid', 'channel']

def valid_data(network_data):
    """verify existence of all fields with non-empty value"""
    return all(map(lambda attr: network_data[attr], network_attributes()))

def main():
    # use local .env to override ENVVARS
    load_dotenv()

    kismet_response = kismet_data()

    return kismet_response['error'] or network_data(kismet_response)

