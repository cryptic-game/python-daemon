#!/bin/sh

set -ex

mkdir -p build
DEBUG=1 python -c 'from daemon.daemon import app;import json;print(json.dumps(app.openapi()))' | tee build/spec
docker build -t redoc-cli github.com/Redocly/redoc#:cli
docker run --rm -v $(pwd)/build:/build redoc-cli bundle /build/spec -o /build/docs.html --options.noAutoAuth --options.noAutoAuth
