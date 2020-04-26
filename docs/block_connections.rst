
.. _block_connections:


Block connections from buttons
==============================
Since 2020 your buttons can be bricked in an update from Amazon servers. To continue
using your devices you must configure your router to block Internet connections from
the buttons. An advanced router (DD-Wrt, Open-WRT, Tomato, RouterOS...) is required
to block connections.

There are 3 ways to avoid making connections to Amazon servers.


Block all connections
---------------------
This is the preferred way and it depends on your router. Configure the router's
firewall to block Internet connections from the device.


Block target servers
--------------------
Some routers allow you to enable parental controls to block connections to certain
sites. You must block these sites:

* ``dash-button-na-aws-opf.amazon.com``
* ``0.amazon.pool.ntp.org``
* ``1.amazon.pool.ntp.org``
* ``2.amazon.pool.ntp.org``
* ``3.amazon.pool.ntp.org``

However this method is not so safe.

Use a raspberry pi
------------------
You can use the Raspberry PI as a router using 2 network cards. To block connections
you can use ``iptables``. Advanced knowledge is required for this method.

