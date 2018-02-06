Troubleshooting
===============

Requirements and installation
-----------------------------
All dependencies are commonly used on a Linux system, but some may not be installed on your system. The dependencies
are:

* Python 2.7 or 3.4+.
* Python-pip (pip).
* Tcpdump.
* Sudo


Why root is required
--------------------
This program needs permission to open raw sockets on your system. You can set this permission using setcap, but you
must be very careful about who can run the program. Raw sockets permission could allow scaling permissions on the
system::

    setcap cap_net_raw=eip ./scripts/amazon-dash
    setcap cap_net_raw=eip /usr/bin/pythonX.X
    setcap cap_net_raw=eip /usr/bin/tcpdump

http://stackoverflow.com/questions/36215201/python-scapy-sniff-without-root
