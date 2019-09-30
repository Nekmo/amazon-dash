"""
netstat -i
iwconfig wlan0 essid NETWORK_NAME key WIRELESS_KEY
dhclient wlan0
"""
import subprocess


def get_cmd_output(cmd, split_lines=True):
    output = subprocess.check_output(cmd)
    if split_lines:
        output = [line.rstrip('\n') for line in output.split('\n')]
    return output


class Wifi:

    def get_wireless_devices(self):
        devices = get_cmd_output(['netstat', '-i'])[2:]
        return map(lambda x: x.split(' ')[0], filter(lambda x: x.startswith('wl'), devices))
