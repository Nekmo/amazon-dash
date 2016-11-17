Amazon Dash
###########
Hack your Amazon Dash to run what you want. Without welders. For the entire family.


1. Install Amazon Dash:

.. code:: bash

    sudo pip install amazon-dash


2. Use discovery mode to know the mac of your Dash (Run the program, and then press the button):

.. code:: bash

    sudo amazon-dash discovery


3. Create a config file:

.. code:: yaml

    # amazon-dash.yml
    # ---------------
    settings:
      delay: 10
    devices:
      0C:47:C9:98:4A:12:
        name: Hero
        user: nekmo
        cmd: spotify
      44:65:0D:48:FA:88:
        name: Pompadour
        user: nekmo
        cmd: kwrite


4. Run the daemon:

.. code:: bash

    sudo amazon-dash run


Avoid making a purchase by pressing the button
==============================================
This program detects when your button connects to the network to execute actions, but does not prevent the ordering.

There are 3 ways to avoid making a purchase when you press the button.


Easy mode: Do not choose the product to buy when setting up
-----------------------------------------------------------
When you first set your button, you are asked which product you want to buy when you press the button. If you do not
choose an option, the button will work, but an order will not be created.

However, in order to take advantage of the free balance ($5/€5/£5), it is necessary to choose a product. The solution is
 after ordering, deactivate the button, reconfigure it, and not choosing the product the second time.

However, you will receive an alert in the Amazon application every time you press the button asking you to finish the
configuration. You can turn off notifications, delete the application, or use another Amazon account.


Using an advanced router
------------------------
If you have an advanced router (DD-Wrt, Open-WRT, Tomato, RouterOS...), you can block Internet output from the buttons.
This is the preferred option. It is necessary to block the Internet output. Using DNS locks will not work. The button
uses its own DNS server IP, ignoring router DNS.


Raspberry PI solution
---------------------
You can use the Raspberry PI as a router if you have 2 network cards. The method is similar to the previous one, but
being a Linux system you can use iptables.

