#!/bin/sh

set -ex

mkdir -p build
PYTHONPATH=daemon python -c 'from daemon import app;import json;print(json.dumps(app.openapi()))' | tee build/spec
docker build -t redoc-cli github.com/Redocly/redoc#:cli
docker run --rm -v $(pwd)/build:/build redoc-cli bundle /build/spec -o /build/docs.html
