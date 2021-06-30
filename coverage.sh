#!/bin/sh

if PYTHONWARNINGS=ignore coverage run --source=daemon -m unittest discover -v tests
then
    coverage ${1:-xml}
    coverage report
    coverage erase
else
    coverage erase
    exit 1
fi
