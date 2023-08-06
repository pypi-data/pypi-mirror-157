

import time
import logging
import urllib.request
from random import randint

from . import log
from . import config

from .domains import pip
pip.install(config)


def _wait_internet():
    logging.info("Waiting for Internet Connection")
    _connected = False
    while not _connected:
        try:
            urllib.request.urlopen('https://www.google.com', timeout=2)
            _connected = True
        except:
            time.sleep(3)
    logging.info("Got Internet Connection. Continuing.")


def updater():
    _wait_internet()
    logging.info("Jitter Delay")
    time.sleep(randint(1, 30))
    logging.info("Executing EBS Updater")
    for domain_name in config.domains:
        domain = getattr(config, domain_name)
        domain.update()
    logging.info("Update Check Complete")


if __name__ == '__main__':
    updater()
