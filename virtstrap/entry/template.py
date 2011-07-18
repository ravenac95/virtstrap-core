import shutil
import os
from virtstrap.templates.base import VirtStrapTemplateBase
from paste.util.template import paste_script_template_renderer


class VirtStrapBasicTemplate(VirtStrapTemplateBase):

    summary = "Creates a basic virtstrapped project"
    required_templates = ['basic_package']
    _template_dir = "../paster-templates/basic/"

    template_renderer = staticmethod(paste_script_template_renderer)
