from .scan import scan, print_pkt

mac_id_list = []


def discovery_print(pkt):
    if pkt.src in mac_id_list:
        return
    mac_id_list.append(pkt.src)
    print_pkt(pkt)


def discover():
    scan(discovery_print, lfilter=lambda d: d.src not in mac_id_list)
