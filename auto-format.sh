#!/bin/bash

set -euxo pipefail

poetry run black .
poetry run isort --atomic --apply
