.. highlight:: console

======
Docker
======
Using Amazon Dash within docker is easy! First, pull the Docker image:

```
$ docker pull nekmo/amazon-dash:latest
```

Then, create a container and run Amazon Dash itself:

```
$ docker run -it --network=host -v <path/to/amazon-dash.yml>:/config/amazon-dash.yml nekmo/amazon-dash:latest amazon-dash run --config /config/amazon-dash.yml
```

Note that :code:`--network=host` is required for the container to be able to
do packet inspection

If you are a docker-compose user, a sample config might look like this::

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
