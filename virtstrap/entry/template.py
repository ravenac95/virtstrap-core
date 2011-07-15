import shutil
import os
from paste.script import templates

VIRTSTRAP_PY_FILENAME = "virtstrap.py"
VIRTSTRAP_PY_SRC_ROOT = "../"

class VirtStrapTemplateBase(templates.Template):
    def write_files(self, command, output_dir, vars):
        super(VirtStrapTemplateBase, self).write_files(command, 
                output_dir, vars)

        print "Creating {0} file for virtstrapping".format(
                VIRTSTRAP_PY_FILENAME)
        
        #Get directory for current file
        file_directory = os.path.abspath(os.path.dirname(__file__))
        #Calculate source directory
        virtstrap_src = os.path.join(file_directory, VIRTSTRAP_PY_SRC_ROOT, 
                VIRTSTRAP_PY_FILENAME)
        #Calculate destination directory
        virtstrap_dest = os.path.join(output_dir, VIRTSTRAP_PY_FILENAME)

        #Copy the current virtstrap.py file into the new project
        shutil.copyfile(virtstrap_src, virtstrap_dest)

class VirtStrapBasicTemplate(VirtStrapTemplateBase):

    summary = "Creates a basic virtstrapped project"
    required_templates = ['basic_package']
    _template_dir = "../templates/basic/"
