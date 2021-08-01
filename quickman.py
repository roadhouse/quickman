"""" kismet data extract """

from config import Config
from kismet import Kismet


class Quickman:
    def __init__(self, config):
        self.config = config
        self.kismet = Kismet(config)

    def wireless_data(self):
        """ main function """
        kismet = self.kismet
        resp = kismet.kismet_response()
        return resp.get('error') or list(kismet.network_data(resp['ok']))


if __name__ == "__main__":
    config = Config("config.yml")
    quickman = Quickman(config)

    print(quickman.wireless_data())
