"""
Command line options
====================
"""
import sys
import pkg_resources
from optparse import OptionParser

# Sorry pip! Stole this from you
try:
    virtstrap_dist = pkg_resources.get_distribution('virtstrap')
    version = '%s from %s (python %s)' % (
        virtstrap_dist, virtstrap_dist.location, sys.version[:3])
except pkg_resources.DistributionNotFound:
    # when running pip.py without installing
    version=None

class CommandOptionParserBuilder(object):
    def __init__(self, command_name=None, args=""):
        self.command_name = command_name or "COMMAND"
        self.args = args or []
    
    def build_parser(self):
        usage_list = ["%prog", self.command_name]
        args = self.args
        if args:
            args_string = " ".join(args)
            usage_list.append(args_string)
        usage_list.append("[OPTIONS]")
        usage = " ".join(usage_list)
        parser = OptionParser(
            usage=usage,
            version=version,
            add_help_option=False,
        )
        parser.add_option('-h', '--help',
                dest='help', action='store_true',
                help='Show help')
        parser.add_option('-q', '--quiet',
                dest='verbosity', action='store_const', const=0,
                help='No output')
        parser.add_option('-v', '--verbose',
                dest='verbosity', action='store_const', const=2,
                help='Verbose output')
        parser.disable_interspersed_args()
        return parser

parser = None
