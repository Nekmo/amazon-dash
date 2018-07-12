import click

from amazon_dash.scan import scan_devices

AMAZON_DEVICES = [
    'F0:D2:F1',
    '88:71:E5',
    'FC:A1:83',
    'F0:27:2D',
    '74:C2:46',
    '68:37:E9',
    '78:E1:03',
    '38:F7:3D',
    '50:DC:E7',
    'A0:02:DC',
    '0C:47:C9',
    '74:75:48',
    'AC:63:BE',
    'FC:A6:67',
    '18:74:2E',
    '00:FC:8B',
    'FC:65:DE',
    '6C:56:97',
    '44:65:0D',
    '50:F5:DA',
    '68:54:FD',
    '40:B4:CD',
    '00:71:47',
    '4C:EF:C0',
    '84:D6:D0',
    '34:D2:70',
    'B4:7C:9C',
    'F0:81:73',
]
"""Amazon Dash Mac Devices. Source: https://standards.ieee.org/develop/regauth/oui/oui.csv

Snippet for Re-generate this list:

>>> import csv
>>> print('\n'.join([':'.join([row[1][i:i+2] for i in range(0, len(row[1]), 2)])
        for row in csv.reader(open('oui.csv')) if row[2] == 'Amazon Technologies Inc.']))
"""


BANNED_DEVICES = ['00:00:00:00:00:00']
"""These mac addresses will not be considered valid results on discovery.
"""

HELP = """\
The discovery command lists the devices that are connected in your network. \
Each device will only be listed once. After executing this command wait approximately \
10 seconds before pressing the Amazon Dash button. After pressing the button, the Mac \
address of the button will immediately appear on the screen. Remember the address to be \
able to create the configuration file.\
"""

mac_id_list = []
"""Mac addresses already known. Mac addresses only appear once.
"""


def pkt_text(pkt):
    """Return source mac address for this Scapy Packet

    :param scapy.packet.Packet pkt: Scapy Packet
    :return: Mac address. Include (Amazon Device) for these devices
    :rtype: str
    """
    if pkt.src.upper() in BANNED_DEVICES:
        body = ''
    elif pkt.src.upper()[:8] in AMAZON_DEVICES:
        body = '{} (Amazon Device)'.format(pkt.src)
    else:
        body = pkt.src
    return body


def discovery_print(pkt):
    """Scandevice callback. Register src mac to avoid src repetition.
    Print device on screen.

    :param scapy.packet.Packet pkt: Scapy Packet
    :return: None
    """
    if pkt.src in mac_id_list:
        return
    mac_id_list.append(pkt.src)
    text = pkt_text(pkt)
    click.secho(text, fg='magenta') if 'Amazon' in text else click.echo(text)


def discover(interface=None):
    """Print help and scan devices on screen.

    :return: None
    """
    click.secho(HELP, fg='yellow')
    scan_devices(discovery_print, lfilter=lambda d: d.src not in mac_id_list, iface=interface)
