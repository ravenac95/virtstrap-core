"""
virtstrap.lib.caller
====================

A wrapper for the subprocess that automatically stores the stdout
into the log.
"""
import shlex
import subprocess
from cStringIO import StringIO
from virtstrap.log import logger

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

def call(command, output_stream):
    """A convenience function for collecting a subprocess' output"""
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    collector = SubprocessOutputCollector(process.stdout, output_stream)
    collector.collect()
    return_code = process.poll()
    return return_code

