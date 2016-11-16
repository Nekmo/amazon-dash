Amazon Dash
###########
Hack your Amazon Dash to run what you want.


1. Install Amazon Dash:

.. code:: bash

    sudo pip install amazon-dash


2. Use discovery mode to know the mac of your Dash (Run the program, and then press the button):

.. code::

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

.. code:: yaml

    sudo amazon-dash run
