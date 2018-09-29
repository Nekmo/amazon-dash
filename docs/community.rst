.. highlight:: console

=========
Community
=========

Here are some example projects of how to use your Amazon Dash button:

* **Random Episode**: Play a random chapter of your favorite series, like *The Simpsons*, *Futurama*, *Friends*... https://github.com/Nekmo/random-episode
* **Gkeep**: Add tasks to Google Keep (buy milk, beer...). The notes can be associated with a place to run a reminder.
  https://github.com/Nekmo/gkeep

Tell us how you use Amazon Dash and **join the community**. Send a email to ``dev [at] nekmo.com``


The Simpsons Random Episode
---------------------------

.. image:: https://raw.githubusercontent.com/Nekmo/amazon-dash/master/images/simpsons.jpg
    :width: 100%


The creator of the project uses Amazon-dash to play a random episode of The Simpsons on the TV. Things you need:

* A Linux computer with the episodes of The Simpsons downloaded.
* Amazon Dash button
* A chromecast and a TV
* Amazon-dash project installed and configured
* Random-episode project installed and configured

Random episode project link: https://github.com/Nekmo/random-episode

To install Random episode::

    sudo pip install random-episode

And configure it:

.. code-block:: yaml

    # random-episode.yml
    # ------------------

    playlists:
        simpsons:  # playlist name
            directories:  # Multiple directories
              - '/media/videos/simpsons/'
            recursive: true  # Optional
            patterns:  # Optional
              - '*.mkv'  # file pattern
              - '*.mp4'
              - '*.avi'
    players:
        chromecast:  # player name
            type: chromecast  # chromecast or native
            # Chromecast name. Useful if you have more than one
            name: nekmo-chromecast


This is the configuration for Amazon-dash:

.. code-block:: yaml

    # amazon-dash.yml
    # ---------------

    44:65:0D:48:FA:88:
      name: Simpsons
      user: nekmo
      cmd: random-episode chromecast simpsons


Shopping list in Google Keep
----------------------------

.. image:: https://raw.githubusercontent.com/Nekmo/amazon-dash/master/images/pepsi.jpg
    :width: 100%


The creator of the project uses Amazon-dash to add products to buy using Google Keep. Google Keep allows you to
add products to buy to a list and create reminders by date and by places (for example when you are at the supermarket).
Things you need:

* A Linux computer. For example a raspberry PI.
* Amazon Dash button
* Amazon-dash project installed and configured
* Gkeep project installed and configured
* Google account

Gkeep project link: https://github.com/Nekmo/gkeep


This is the configuration for Amazon-dash:

.. code-block:: yaml

    settings:
      delay: 15
    devices:
      34:d2:71:1b:73:13:
        name: Pepsi
        user: alarm
        cmd: gkeep --auth /etc/auth.txt add-item 170ae95c548.78ec8e3cffc10be4 "Pepsi" --uncheck


Play a audio
------------

This is an example created by Nekmo of how to play an audio on your computer when you press the Amazon dash button.
Things you need:

* A linux computer with audio output
* Amazon Dash button
* Amazon-dash project installed and configured
* A audio file to play
* ffmpeg installed


.. code-block:: yaml

    settings:
      delay: 15
    devices:
      34:d2:71:3b:82:17:
        name: Dong Audio
        user: nekmo
        cmd: ffplay -nodisp -autoexit /home/nekmo/Music/dong.png


Externas links
--------------
Send to the email address ``dev [at] nekmo.com`` the articles you write about Amazon Dash. The submitted links will be
added to this list.

* https://github.com/internetfan420/my-amazon-dash-hacks
* http://blog.roy29fuku.com/iot/amazon-dash-button%E3%82%92python%E3%81%A7%E3%83%8F%E3%83%83%E3%82%AF%E3%81%99%E3%82%8B-part1-%E8%A8%AD%E5%AE%9A/
* https://qiita.com/nardtree/items/23c36fa3b989d329a1f3
* https://qiita.com/moyasi98/items/982c9fb0cf73156c23a3
* https://a-zumi.net/python-amazon-dash-button-tweet/
* https://a-zumi.net/python-amazon-dash-button-send-mail/
* https://helpdesk.bluesound.com/discussions/viewtopic.php?t=4331
* http://helloworld-yaruzo.com/author/nardtree/
* http://www.redsilico.com/blog/make-google-home-talk-using-amazon-dash-button
* https://7me.oji.0j0.jp/2018/raspberry-amazon-dash-certbot.html
* https://www.elotrolado.net/hilo_proyecto-hack-amazon-dash-el-boton-que-ejecuta-lo-que-tu-quieras-iot-v0-4-0_2200509
* https://www.youtube.com/watch?v=pjN1oO-l-uM
* https://www.youtube.com/watch?v=alexax8rhgo
* https://www.youtube.com/watch?v=gj7H5WCyMg8
