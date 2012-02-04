from argparse import ArgumentParser
from virtstrap.project import Project
from virtstrap.log import logger

__all__ = ['Command', 'ProjectMixin', 'ProjectCommand']

class Command(object):
    name = None
    args = None
    parser = ArgumentParser()
    description = None
    options = None

    def __init__(self):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.options = []
        self.logger = logger

    def execute(self, options):
        self.logger.info('Running "%s" command' % self.name)
        try:
            self.run(options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return 2
        return 0

    def run(self, options):
        raise NotImplementedError('This command does nothing')

class ProjectMixin(object):
    def load_project(self, options):
        return Project.load(options)

class ProjectCommand(Command, ProjectMixin):
    def execute(self, options):
        project = self.load_project(options)
        self.logger.info('Running "%s" command' % self.name)
        try:
            self.run(project, options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return 2
        return 0

    def run(self, project):
        raise NotImplementedError('This command does nothing')

