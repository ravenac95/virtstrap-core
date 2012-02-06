from argparse import ArgumentParser
from jinja2 import Environment
from virtstrap.project import Project
from virtstrap.log import logger

__all__ = ['Command', 'ProjectMixin', 'ProjectCommand']

class Command(object):
    name = None
    args = None
    parser = ArgumentParser()
    description = None

    def __init__(self):
        # Ensure that name, usage, and description
        # are defined
        assert self.name
        self.options = None
        self.logger = logger

    def execute(self, options, **kwargs):
        self.options = options
        self.logger.info('Running "%s" command' % self.name)
        try:
            self.run(options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return 2
        finally:
            self.options = None
        return 0

    def render_string(self, source):
        """Render's a string using Jinja2 templates"""
        env = self.template_environment()
        template = env.from_string(source)
        context = dict(command=self, options=self.options)
        return template.render(context)

    def template_environment(self):
        return Environment()

    def run(self, options):
        raise NotImplementedError('This command does nothing')

class ProjectMixin(object):
    def load_project(self, options):
        return Project.load(options)

class ProjectCommand(Command, ProjectMixin):
    def execute(self, options, project=None, **kwargs):
        if not project:
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

