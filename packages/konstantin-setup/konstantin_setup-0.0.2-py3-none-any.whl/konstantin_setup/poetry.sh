#!/bin/bash
# установка актуальной версии poetry

curl -sSL https://install.python-poetry.org | python3 -
. ~/.profile
poetry config virtualenvs.in-project true
