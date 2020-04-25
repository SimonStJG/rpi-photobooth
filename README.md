[![Travis CI](https://travis-ci.org/SimonStJG/rpi-photobooth.svg?branch=master)](https://travis-ci.org/SimonStJG/rpi-photobooth)

Simple photobooth for Raspberry Pi, controlled by hardware buttons only.
 
> (Well ok, technically you can use a keyboard if you really want, but it's 
designed for buttons.  You definitely can't use a mouse!  And yes it will
probably actually work on any Linux distro if you can be bothered to track 
down the right Qt5 dependencies.) 

If you'd like to see what sort of configurations are configurable, take a look
 at [the config](default-config.cfg).

# Installation

1. On any Debian-ish distro, including Raspberry Pi: 
    ```
    sudo apt install \
        python3-pyqt5
        python3-pyqt5.qtmultimedia \
        python3-cups \
        libqt5multimedia5 \
        libqt5multimedia5-plugins
    ```
    
    > (It is tempting as it is to use a proper python package manager like Pip,
    or even Poetry, but we want to avoid building PyQt5 as it takes forever on a 
    Raspberry Pi.  And if you don't get all the dependencies installed for 
    QtMultimedia, PyQt5 will still build properly - but then QtMultimedia will 
    just not work at all and no-ones got time for that.)

2. Take a copy of `default-config.cfg` and update it as needed.

3. Run it:
    ```
    python3 -m photobooth --config my-config.cfg
    ```

# Development

Install linting tools with `pip install -r ./dev-requirements.txt` and run linting 
checks with `./checks.sh`.

You can autoformat the code with `./auto-format.sh` too.

# Thanks

Influenced by [reuterbal](https://github.com/reuterbal/)'s excellent 
[photobooth](https://github.com/reuterbal/photobooth).   

In fact theirs is better for almost every use case, except perhaps if you want
 an ultra simple Raspberry Pi-only photobooth.

# License

Code licensed under GPL v3, See [LICENSE.txt](LICENSE.txt)

# TODO 

* Test fresh install
* Support video mirroring (left to right)
* Support scaling background images (right now if the background is too small
  it will be centered and repeated)
  
# Personal notes 

(Some notes specific for my personal setup)

1. Install HP printer drivers via `sudo apt install hplip` - don't install 
via the script on HPs website!  It will try to pull in all sorts of rubbish.
2. Add the printer via cups in the usual way, i.e. http://localhost:631 and 
choose driver `HP Photosmart a610, hpcups 3.18.12 (color)`.
3. Copy over the autostarting .desktop file into the `~/.config/autostart`
folder.