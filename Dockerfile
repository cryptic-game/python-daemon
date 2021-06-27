FROM python:3.9-alpine AS builder

RUN apk add --no-cache \
    build-base~=0.5 \
    gcc~=10.2 \
    musl-dev~=1.2 \
    libffi-dev~=3.3 \
    postgresql-dev~=13.3

WORKDIR /build

RUN pip install pipenv==2020.11.15

COPY Pipfile /build/
COPY Pipfile.lock /build/

ARG PIPENV_NOSPIN=true
ARG PIPENV_VENV_IN_PROJECT=true
RUN pipenv install --deploy --ignore-pipfile


FROM python:3.9-alpine

LABEL org.opencontainers.image.source="https://github.com/cryptic-game/python-daemon"

WORKDIR /app

RUN set -x \
    && apk add --no-cache libpq~=13.3 \
    && addgroup -g 1000 cryptic \
    && adduser -G cryptic -u 1000 -s /bin/bash -D -H cryptic

USER cryptic

EXPOSE 8000

COPY --from=builder /build/.venv/lib /usr/local/lib

COPY daemon.sh /app/
COPY daemon /app/daemon/

ENTRYPOINT /app/daemon.sh
