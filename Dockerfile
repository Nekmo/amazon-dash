FROM python:3.6

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY common-requirements.txt common-requirements.txt
COPY py3-requirements.txt py3-requirements.txt

RUN pip install --no-cache-dir -r py3-requirements.txt

COPY . .

RUN pip install . && python -m amazon_dash.install

CMD [ "amazon-dash", "discovery" ]
