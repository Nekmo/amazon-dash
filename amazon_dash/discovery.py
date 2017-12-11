from .scan import scan

mac_id_list = []


def print_pkt(pkt):
    print(pkt.src)


def discovery_print(pkt):
    if pkt.src in mac_id_list:
        return
    mac_id_list.append(pkt.src)
    print_pkt(pkt)


def discover():
    scan(discovery_print, lfilter=lambda d: d.src not in mac_id_list)
