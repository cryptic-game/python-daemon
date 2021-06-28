#!/bin/sh

if PYTHONWARNINGS=ignore PYTHONPATH=daemon coverage run --source=daemon -m unittest discover -v tests
then
    coverage xml
    coverage report
    coverage erase
else
    coverage erase
    exit 1
fi
