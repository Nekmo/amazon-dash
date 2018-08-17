import logging

from amazon_dash.exceptions import SocketPermissionError

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


try:
    PermissionError
except NameError:
    import socket
    PermissionError = socket.error


def scan_devices(fn, lfilter, iface=None):
    """Sniff packages

    :param fn: callback on packet
    :param lfilter: filter packages
    :return: loop
    """
    try:
        sniff(prn=fn, store=0,
              # filter="udp",
              filter="arp or (udp and src port 68 and dst port 67 and src host 0.0.0.0)",
              lfilter=lfilter, iface=iface)
    except PermissionError:
        raise SocketPermissionError
