"""" kismet data extract """

from config import Config
from kismet import Kismet
from bully_attack import BullyAttack
import pexpect


class Quickman:
    def __init__(self, config):
        self.config = config
        self.kismet = Kismet(config)

    def wireless_data(self):
        """ main function """
        kismet = self.kismet
        resp = kismet.kismet_response()
        return resp.get('error') or list(kismet.network_data(resp['ok']))

    def pixie_attack(self, params):
        return self.running_attack(BullyAttack(**params).command())

    def running_attack(self, command):
        return pexpect.spawn(command)


if __name__ == "__main__":
    config = Config("config.yml")
    quickman = Quickman(config)

    print(quickman.wireless_data())
