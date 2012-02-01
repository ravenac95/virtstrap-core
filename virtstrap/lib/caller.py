"""
virtstrap.lib.caller
====================

A wrapper for the subprocess that automatically stores the stdout
into the log.
"""
import shlex
import subprocess
from cStringIO import StringIO
from virtstrap.log import logger as virtstrap_logger

class LogOutputStream(object):
    def __init__(self, level='info', logger=None):
        self._logger = logger or virtstrap_logger
        self._level = level

    def write(self, string):
        # Get the log method based on level
        log_method = getattr(self._logger, self._level)
        log_method(string)

class SubprocessOutputCollector(object):
    def __init__(self, stdout, output_stream):
        self._stdout = stdout
        self._output_stream = output_stream

    def collect(self):
        while True:
            line = self._stdout.readline()
            if not line:
                break
            self._output_stream.write(line)

def call(command, output_stream=None):
    """A convenience function for collecting a subprocess' output"""
    output_stream = output_stream or LogOutputStream()
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    collector = SubprocessOutputCollector(process.stdout, output_stream)
    collector.collect()
    return_code = process.poll()
    return return_code

