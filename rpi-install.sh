#!/bin/bash
set -euxo pipefail

# TODO test this

deps=(
  # Install Qt build deps from https://wiki.qt.io/Building_Qt_5_from_Git
  #

  # Build essentials
  build-essential
  perl
  # Libxcb
  '^libxcb.*-dev'
  libx11-xcb-dev
  libglu1-mesa-dev
  libxrender-dev
  libxi-dev
  libxkbcommon-dev
  libxkbcommon-x11-dev
  # Qt Multimedia
  libasound2-dev
  libgstreamer0.10-dev
  libgstreamer-plugins-base0.10-dev

  # PyQt5 specific build deps (couldn't find a good source for these
  #   so I've guessed).
  python3-dev
  python3-pip
)

sudo apt install "${deps[@]}"
python3 -m pip install .
