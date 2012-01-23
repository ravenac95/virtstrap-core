"""
Command line options
====================
"""
import sys
import pkg_resources
from optparse import OptionParser
import constants

# Sorry pip! Stole this from you
try:
    virtstrap_dist = pkg_resources.get_distribution('virtstrap')
    version = '%s from %s (python %s)' % (
        virtstrap_dist, virtstrap_dist.location, sys.version[:3])
except pkg_resources.DistributionNotFound:
    # when running pip.py without installing
    version=None

def create_parser(command_name=None, args=None):
    """OptionParser Factory Method"""
    command_name = command_name or "COMMAND"
    if command_name == "help":
        command_name = "COMMAND"
    args = args or []
    usage_list = ["%prog", command_name]
    args = args
    if args:
        args_string = " ".join(args)
        usage_list.append(args_string)
    usage_list.append("[OPTIONS]")
    usage = " ".join(usage_list)
    parser = OptionParser(
        usage=usage,
        version=version,
    )
    if command_name == "COMMAND":
        # If the command is not specified then we must change settings
        # to accommodate.
        # Disable interspersed args to prevent the parser from throwing 
        # an exception when it encounters an unknown option
        parser.disable_interspersed_args()
        # Remove default help option
        parser.remove_option('--help')
        # Add custom default option
        parser.add_option('-h', '--help',
                dest='help', action='store_true',
                help='show help')
    # Set all default settings
    parser.add_option('-v', '--verbosity', dest='verbosity', 
            action='store', type="int", default=2,
            metavar='LVL',
            help='set verbosity level. [0, 1, 2, 3]')
    parser.add_option('-l', '--log', dest='log_file', metavar='FILE',
            action='store', default=constants.LOG_FILE,
            help='log file')
    parser.add_option('--virtstrap-dir', dest='virtstrap_dir', 
            action='store', default=constants.VIRTSTRAP_DIR,
            metavar='DIR',
            help='the directory to install virtstrap')
    parser.add_option('--no-colored-output', dest='no_colored_output',
            action='store_true', default=False,
            help='do not use output colors')
    return parser

