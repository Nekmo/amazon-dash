
Avoid making a purchase by pressing the button
==============================================
This program detects when your button connects to the network to execute actions, but does not prevent the ordering.

There are 3 ways to avoid making a purchase when you press the button.


Easy mode: Do not choose the product to buy when setting up
-----------------------------------------------------------
When you first set your button, you are asked which product you want to buy when you press the button. If you do not
choose an option, the button will work, but an order will not be created.

However, in order to take advantage of the free balance ($5/€5/£5), it is necessary to choose a product. The solution
is after ordering, reconfigure it (press the button again for 5 seconds), and not choosing the product the second time.

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
