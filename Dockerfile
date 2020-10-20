FROM python:3.8-alpine

RUN set -x \
    && apk add --no-cache bash=5.0.17-r0 gcc=9.3.0-r2 musl-dev=1.1.24-r9 postgresql-dev=12.4-r0 \
    && addgroup -g 1000 cryptic \
    && adduser -G cryptic -u 1000 -s /bin/bash -D cryptic

USER cryptic

ENV PATH="/home/cryptic/.local/bin:${PATH}"

WORKDIR /app

RUN pip install --user pipenv==2020.8.13

COPY Pipfile /app/
COPY Pipfile.lock /app/

RUN pipenv sync

COPY ./daemon /app/daemon/

CMD pipenv run daemon
