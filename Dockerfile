FROM python:3.7-alpine
LABEL maintainer="Nekmo Com <contacto@nekmo.com>"

VOLUME /config

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . .

COPY common-requirements.txt common-requirements.txt
COPY py3-requirements.txt py3-requirements.txt

RUN apk update \
    && apk add --no-cache --virtual build-dependencies \
      build-base=0.5-r1 \
    && apk add --no-cache \
      libpcap=1.8.1-r1 \
      procps=3.3.15-r0 \
      tcpdump=4.9.2-r3 \
      scapy=2.4.0-r0 \
    && apk add --no-cache \
      bash \
    && pip install --no-cache-dir -r py3-requirements.txt \
    && pip install . \
    && python -m amazon_dash.install \
    && apk del build-dependencies \
    && rm -rf /var/cache/apk/*
