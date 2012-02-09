from argparse import ArgumentParser
from jinja2 import Environment
from virtstrap.log import logger
from virtstrap.templating import environment
from virtstrap.project import Project

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
        return_code = 0
        try:
            self.run(options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return_code = 2
        finally:
            self.options = None
        return return_code

    def render_template_string(self, source, **context):
        """Render's a string using Jinja2 templates"""
        env = self.template_environment()
        template = env.from_string(source)
        return self._render(template, context)

    def render_template(self, template_name, **context):
        env = self.template_environment()
        template = env.get_template(template_name)
        return self._render(template, context)

    def template_context(self):
        return dict(options=self.options, command=self)

    def template_environment(self):
        return environment()

    def _render(self, template, context):
        base_context = self.template_context()
        base_context.update(context)
        return template.render(base_context)

    def run(self, options):
        raise NotImplementedError('This command does nothing')

class ProjectMixin(object):
    def load_project(self, options):
        return Project.load(options)

class ProjectCommand(Command, ProjectMixin):
    def execute(self, options, project=None, **kwargs):
        if not project:
            project = self.load_project(options)
        self.project = project
        self.logger.info('Running "%s" command' % self.name)
        return_code = 0
        try:
            self.run(project, options)
        except:
            self.logger.exception('An error occured executing command "%s"' %
                    self.__class__.__name__)
            return_code = 2
        finally:
            self.project = None
        return return_code

    def template_context(self):
        base_dict = super(ProjectCommand, self).template_context()
        base_dict.update(dict(project=self.project))
        return base_dict

    def run(self, project):
        raise NotImplementedError('This command does nothing')

