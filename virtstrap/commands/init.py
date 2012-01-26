import os
import virtualenv
import sys
from virtstrap import commands
from virtstrap import constants
from virtstrap.lib.command import Command
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('PROJECT_DIR',
        help="project's root directory",
        nargs='?', default='.')

class InitializeCommand(Command):
    name = 'init'
    args = ['[directory]']
    parser = parser
    description = 'Bootstraps a virtstrap virtual environment'

    def run(self, **options):
        logger = self.logger
        virtstrap_dir_relpath = options.get('virtstrap_dir')
        virtstrap_dir = os.path.abspath(virtstrap_dir_relpath)
        logger.info('Creating virtualenv in %s' % virtstrap_dir)
        # FIXME fake virtualenv
        virtualenv.create_environment(virtstrap_dir,
                site_packages=False,
                prompt="(fake)")
        quick_activate = open('./quickactivate.sh', 'w')
        quick_activate.write("test")
        quick_activate.close()

commands.register(InitializeCommand)
