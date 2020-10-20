FROM python:3.8-alpine AS builder

RUN apk add --no-cache gcc=9.3.0-r2 musl-dev=1.1.24-r9 postgresql-dev=12.4-r0

WORKDIR /build

RUN pip install pipenv==2020.8.13

COPY Pipfile /build/
COPY Pipfile.lock /build/

ARG PIPENV_NOSPIN=true
ARG PIPENV_VENV_IN_PROJECT=true
RUN pipenv install --deploy --ignore-pipfile

FROM python:3.8-alpine

RUN set -x \
    && apk add --no-cache bash=5.0.17-r0 libpq=12.4-r0 \
    && addgroup -g 1000 cryptic \
    && adduser -G cryptic -u 1000 -s /bin/bash -D -H cryptic

WORKDIR /app

USER cryptic

COPY --from=builder /build/.venv/lib /usr/local/lib

COPY ./daemon /app/

CMD python daemon.py
