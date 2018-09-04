import logging
from scapy.packet import Packet
from scapy.sendrecv import sniff
from typing import Callable, Any, Union

from amazon_dash.exceptions import SocketPermissionError

logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

try:
    PermissionError
except NameError:
    import socket
    PermissionError = socket.error


def scan_devices(fn: Callable[[Packet], Any], lfilter: Callable[[Packet], bool],
                 iface: Union[str, None]=None) -> None:
    """Sniff packages loop

    :param fn: callback on packet
    :param lfilter: filter packages
    :param iface: Network interface to listen.
    """
    try:
        sniff(prn=fn, store=0,
              # filter="udp",
              filter="arp or (udp and src port 68 and dst port 67 and src host 0.0.0.0)",
              lfilter=lfilter, iface=iface)
    except PermissionError:
        raise SocketPermissionError
