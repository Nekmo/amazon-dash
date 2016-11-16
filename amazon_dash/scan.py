
import datetime
import logging

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *


def button_pressed_dash1():
    current_time = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print('Dash button pressed at ' + current_time)


def print_pkt(pkt):
    print(pkt.src)


def scan(fn, lfilter):
    sniff(prn=fn, store=0, filter="udp", lfilter=lfilter)
