.. highlight:: console

============
Installation
============


Stable release
--------------

To install amazon-dash, run these commands in your terminal:

.. code-block:: console

    $ pip install -U amazon_dash
    $ sudo python -m amazon_dash.install

This is the preferred method to install amazon-dash, as it will always install the most recent stable release.
You must execute both commands in the correct order.

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Other releases
--------------
You can install other versions from Pypi using::

    $ pip install amazon-dash==<version>
    $ sudo python -m amazon_dash.install

For versions that are not in Pypi (it is a development version)::

    $ pip install git+https://github.com/Nekmo/amazon-dash.git@<branch>#egg=amazon-dash
    $ sudo python -m amazon_dash.install


If you do not have git installed:

    $ pip install https://github.com/Nekmo/amazon-dash/archive/<branch>.zip
    $ sudo python -m amazon_dash.install


Distro packages
---------------

Arch Linux
``````````
If you use Arch Linux or an Arch Linux derivative, you can install Amazon Dash from
`AUR <https://aur.archlinux.org/packages/amazon-dash-git/>`_. For example if you use yaourt::

    $ yaourt -S amazon-dash-git


Installation Issues
-------------------
There are many Linux distributions available and not all are tested. If you think there is a bug please
`open a issue <https://github.com/Nekmo/amazon-dash/issues>`_. Before opening a issue, check the following:

# Search similar issues.
#. Your Python version (check the supported versions).
#. Upgrade pip and setuptools (``pip install -U setuptools pip``).
#. Check if it is a configuration error. Errors that start with ``[Error] Amazon Dash Exception`` are usually not bugs.
#. Finally, follow the guidelines for creating issues.



From sources
------------

The sources for amazon-dash can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/Nekmo/amazon-dash

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/Nekmo/amazon-dash/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install
    $ sudo python -m amazon_dash.install


.. _Github repo: https://github.com/Nekmo/amazon-dash
.. _tarball: https://github.com/Nekmo/amazon-dash/tarball/master


Other OS that Linux
-------------------
At the moment only Linux is officially supported by the Amazon-dash project. However Amazon-dash should work on
unix-like systems. Microsoft Windows is not supported and it is unknown if it works. Please do not open issues
requesting support for Windows, I have no chance to try Amazon-dash on Windows.

OS X
````
The configuration file must use these permissions::

    chmod 600 <config file>
    chown root <config file>

OS X is not officially supported. But I've read that it works without problems.
