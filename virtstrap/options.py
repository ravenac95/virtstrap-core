"""
Command line options
====================
"""
import sys
import pkg_resources
from argparse import ArgumentParser
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
    """ArgumentParser Factory Method"""
    command_name = command_name or "COMMAND"
    if command_name == "help":
        command_name = "COMMAND"
    args = args or []
    usage_list = ["%(prog)s", command_name]
    args = args
    if args:
        args_string = " ".join(args)
        usage_list.append(args_string)
    usage_list.append("[OPTIONS]")
    usage = " ".join(usage_list)
    parser = ArgumentParser(
        usage=usage,
    )
    parser.add_argument('--version', action='version', version=version)
    parser.add_argument('-v', '--verbosity', dest='verbosity', 
            action='store', type=int, default=2,
            metavar='LVL',
            help='set verbosity level. [0, 1, 2, 3]')
    parser.add_argument('-l', '--log', dest='log_file', metavar='FILE',
            action='store', default=constants.LOG_FILE,
            help='log file')
    parser.add_argument('--virtstrap-dir', dest='virtstrap_dir', 
            action='store', default=constants.VIRTSTRAP_DIR,
            metavar='DIR',
            help='the directory to install virtstrap')
    parser.add_argument('--no-colored-output', dest='no_colored_output',
            action='store_true', default=False,
            help='do not use output colors')
    return parser

