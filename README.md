[![Travis CI](https://travis-ci.org/SimonStJG/rpi-photobooth.svg?branch=master)](https://travis-ci.org/SimonStJG/rpi-photobooth)

Simple and minimal photobooth for Raspberry Pi, controlled by hardware buttons only (well ok technically you can use a 
keyboard, if you really want, but it's not a nice way to control it).

Influenced by [reuterbal](https://github.com/reuterbal/)'s excellent 
[photobooth](https://github.com/reuterbal/photobooth).   
In fact theirs is better for almost every use case, except perhaps if you want a ultra simple Raspberry Pi only 
photobooth which can only be controlled by hardware buttons. 

# Installation

Tempting as it is to use a proper package manager like poetry, or even pip, in this case you probably want to avoid 
building pyqt5 as it will take forever on a raspberry pi, and if you don't get all the dependencies installed it will 
still build properly - but then some parts like QtMultimedia will just not work at all.

So, we're going to use the system versions of everything.  This should work on any debian based distro, including
 Raspberry Pi: 
```
sudo apt install \
    python3-pyqt5
    python3-pyqt5.qtmultimedia \
    python3-cups \
    libqt5multimedia5 \
    libqt5multimedia5-plugins
```

Take a copy of `default-config.cfg` and update it as needed, then run:
```
python3 -m photobooth --config my-config.cfg
```

# Dev

Install linting tools with `./dev-requirements.txt` and run with `./checks.sh`.

# License

Code licensed under GPL v3, See [LICENSE.txt](LICENSE.txt)
