
Rescue devices and configure Wifi
=================================
Since August 31, 2019, Amazon `removed the option to configure Amazon Dash buttons <https://www.amazon
.com/gp/help/customer/display.html?nodeId=201746440>`_. In addition, since December 31, 2019, it resets
any device that connects to its servers. This means that any button that connects to Internet will
be bricked forever.

To continue using your buttons with this project, you must have an advanced router that allows you to
:ref:`block requests to Internet <block_connections>`. You can also use a raspberry as a router.

If your button has been connected to the Internet after December 31, 2019, it has probably been
bricked and at the moment there is no solution. If you have never configured your button it is
necessary to hack it first. If you already have it configured but want to change your Wifi network,
go to :ref:`configure_wifi`.


.. _hack:

Hack your device
----------------
The ``hack-device`` command allows you to hack a Amazon-dash device built on May 2016 and earlier.
Even if your device was purchased later, it is likely that it has an older firmware installed. You only
need to use this option if you have never connected your device to Amazon servers.

Sound is used to hack the device (Amazon Dash buttons include a microphone). It is recommended to use
earbuds near the button. Remember to turn up the volume on your computer.

To start the hack use::

    $ amazon-dash hack-device

This command will repeat a recording to hack the device. If the hack has worked, the LED will turn green.


.. _configure_wifi:

Configure wifi
--------------
The ``configure`` command allows you to change the Wi-Fi network of your device. It can also be used to
get device data like MAC Address. This command only works on Linux. This command will change the wifi network
of your computer. Amazon-dash support ``NetworkManager`` and ``iwconfig + dhclient`` but *NetworkManager* is
recommended because it does not require root. To configure your button::

    $ amazon-dash configure


Halfway through the configuration you must block your device on the router. You need an advanced
router to block connections.
