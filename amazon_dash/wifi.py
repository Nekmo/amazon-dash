"""
netstat -i
iwconfig wlan0 essid NETWORK_NAME key WIRELESS_KEY
dhclient wlan0
"""
import subprocess



def get_cmd_output(cmd, split_lines=True, decode='utf-8'):
    output = subprocess.check_output(cmd)
    if decode:
        output = output.decode('utf-8')
    if split_lines:
        output = [line.rstrip('\n') for line in output.split('\n')]
    return output


class Wifi:

    def __init__(self, device=None):
        self.device = device or next(self.get_wireless_devices(), None)
        if self.device is None:
            from amazon_dash.exceptions import ConfigWifiError
            raise ConfigWifiError('Wireless card is not available.')

    def get_wireless_devices(self):
        devices = get_cmd_output(['ip', 'a'])
        devices = map(lambda x: x.split(' ')[1].rstrip(':'), filter(lambda x: not x.startswith(' '), devices))
        return filter(lambda x: x.startswith('wl'), devices)

    def connect(self, essid, key=None):
        cmd = ['iwconfig', self.device, 'essid', essid]
        if key:
            cmd += ['key', key]
        get_cmd_output(cmd)

    def dhcp(self):
        get_cmd_output(['dhclient', self.device])


if __name__ == '__main__':
    w = Wifi()
    w.connect('Amazon ConfigureMe')
