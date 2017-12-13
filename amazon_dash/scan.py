import logging

from amazon_dash.exceptions import SocketPermissionError

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def scan_devices(fn, lfilter):
    try:
        sniff(prn=fn, store=0, filter="udp", lfilter=lfilter)
    except PermissionError:
        raise SocketPermissionError
