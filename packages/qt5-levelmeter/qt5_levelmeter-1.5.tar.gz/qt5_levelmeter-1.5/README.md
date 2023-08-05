# Level Meter (VU Meter) for QT5

## Installation:

### From source:

    git clone https://gitlab.com/t-5/python3-qt5-levelmeter.git
    cd python3-qt5-levelmeter
    pip3 install .

### Debian Package:

I have a prebuilt debian package for this module.
Please refer to the page https://t-5.eu/hp/Software/Debian%20repository/ to setup the repo.
After the repo is setup you can install the package by issueing

    apt install python3-qt5-levelmeter

in a shell.


## Usage:

Usage:
from qt5_levelmeter import QLevelMeter

meter = QLevelMeter(parent)

call periodically:
meter.levelChanged(levelInDb)
