"""
Initialize Command
==================

Very high level tests for the virtstrap runner
"""
import os
import sys
import fudge
from virtstrap.testing import *
from nose.tools import raises
from virtstrap.commands.init import InitializeCommand

def test_initialize_command():
    command = InitializeCommand()
