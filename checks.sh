#!/bin/bash

set -euxo pipefail

poetry run black . --check --diff
poetry run isort --check-only --recursive
poetry run flake8
