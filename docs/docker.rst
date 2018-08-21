.. highlight:: console

======
Docker
======
Using Amazon Dash within docker is easy! First, pull the Docker image:


.. code-block:: console

    $ docker pull nekmo/amazon-dash:latest


Then, create a container and run Amazon Dash itself:


.. code-block:: console

    $ docker run -it --network=host \
                 -v </full/path/to/amazon-dash.yml>:/config/amazon-dash.yml \
                 nekmo/amazon-dash:latest \
                 amazon-dash run --ignore-perms --root-allowed \
                                 --config /config/amazon-dash.yml


Note that :code:`--network=host` is required for the container to be able to
do packet inspection

If you are a docker-compose user, a sample config might look like this:


.. code-block:: yaml

    ---
    version: "3"

    services:

    amazon-dash:
      command: amazon-dash run --config /config/amazon-dash.yml
      container_name: amazon-dash
      image: nekmo/amazon-dash:latest
      network_mode: "host"
      restart: unless-stopped
      volumes:
        - <path/to/amazon-dash.yml>:/config/amazon-dash.yml
