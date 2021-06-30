#!/bin/sh

PYTHONWARNINGS=ignore PYTHONPATH=daemon python -m unittest discover -v tests
