import logging
import os
from subprocess import call
import platform

vs_logger = logging.getLogger("virtstrap")

def script_run(settings):
    if platform.system().startswith("Darwin"):
        vs_logger.info("Installing Mac OS X specific readline fix for ipython")
        call(["easy_install", "-a", "readline"])
