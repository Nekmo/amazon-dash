import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def scan(fn, lfilter):
    sniff(prn=fn, store=0, filter="udp", lfilter=lfilter)
