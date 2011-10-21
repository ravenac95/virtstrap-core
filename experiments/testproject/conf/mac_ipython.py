import os
from subprocess import call
import platform

def script_run(settings):
    if platform.system().startswith("Darwin"):
        print "Installing Mac specific fix for ipython"
        call(["easy_install", "-a", "readline"])
