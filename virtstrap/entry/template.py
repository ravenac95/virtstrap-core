import shutil
import os
from virtstrap.templates.base import VirtStrapTemplateBase
from paste.util.template import paste_script_template_renderer


class VirtStrapBasicTemplate(VirtStrapTemplateBase):

    summary = "Creates a basic virtstrap enabled project"
    required_templates = ['basic_package']
    _template_dir = "../paster-templates/basic/"

    template_renderer = staticmethod(paste_script_template_renderer)

class VirtStrapIPythonTemplate(VirtStrapTemplateBase):

    summary = "Creates a virtstrap project adding ipython support (even for Mac)"
    required_templates = ['basic_package']
    _template_dir = "../paster-templates/ipython/"

    template_renderer = staticmethod(paste_script_template_renderer)
