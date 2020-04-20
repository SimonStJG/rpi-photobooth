#!/bin/bash

set -euxo pipefail

black . --check --diff
isort --check-only --recursive
flake8
