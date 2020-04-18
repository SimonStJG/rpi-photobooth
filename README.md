[![Travis CI](https://travis-ci.org/SimonStJG/rpi-photobooth.svg?branch=master)](https://travis-ci.org/SimonStJG/rpi-photobooth)

Simple and minimal photobooth for Raspberry Pi, controlled by hardware buttons only (well ok technically you can use a 
keyboard, if you really want, but it's not a nice way to control it).

Influenced by [reuterbal](https://github.com/reuterbal/)'s excellent 
[photobooth](https://github.com/reuterbal/photobooth).   
In fact theirs is better for almost every use case, except perhaps if you want a ultra simple Raspberry Pi only 
photobooth which can only be controlled by hardware buttons. 

# Installation

On a fresh raspberry pi, run: `./rpi-install.sh`

# Running

Take a copy of `default-config.cfg` and update it as needed, then run:
```
photobooth --config my-config.cfg
```

# License

Code licensed under GPL v3, See [LICENSE.txt](LICENSE.txt)