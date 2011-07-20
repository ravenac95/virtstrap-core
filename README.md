VirtStrap
=========

A simple script that allows you to setup a repeatable project using a
variety of tools. The project came out of a need to use some things
from buildout and some things from pip and virtualenv. 

Why I made virtstrap
--------------------

Essentially, there was a short period of time where I was a little 
obsessed with using zc.buildout. However, I quickly found out that
if I needed to quickly experiment a library it was not as simple
as installing it through pip. In addition, I found buildout's support
for a ``--no-site-packages`` like function to be unsatisfactory. One
package on my Mac, ipython, was particularly finicky when using buildout.
For those of you who have experienced it. ipython on the mac requires
that you install a new version of readline which only seems to work
through using ``easy_install``. So this forced me to come up with a solution
as using ipython is very important to me.

The result is virtstrap.

It this another build tool?
---------------------------

Yes and no. Virtstrap is not meant to replace pip, virtualenv, or buildout. 
It simply puts all of those tools together so they can work in a friendly
way.

Install virtstrap
-----------------

Simply do the usual:

``python setup.py install``

or

``python setup.py develop``

If you don't want to install it into the system you can simply 
copy the virtstrap.py file that is located in the virtstrap 
directory of the this project.

Using virtstrap (the most basic way)
------------------------------------

Using virtstrap is as simple as copying the virtstrap.py file in 
the virtstrap directory of this project and writing a JSON object 
in a file called vsettings. The object requires one property 
``package_name`` which must be set to the desired name of the package.
This name should only contain letters, numbers and underscores.


Using virtstrap with PasteScript (the convenient way)
-----------------------------------------------------

If you install virtstrap using ``python setup.py install`` or 
``python setup.py develop`` virtstrap also includes some convenience 
templates to get you started on a virtstrap based project. The templates
automatically generate a basic virtstrap project. To use the template
simply do:

``paster create --template=virtstrap_basic``

This will invoke PasteScript. Just answer the questions and you'll be setup
with a nice project to run with.

Environment Types (this is how you make magic happen) 
-----------------------------------------------------

An environment type in virtstrap is any method you'd like to use to
build your environment. Currently the options are to use pip or buildout. 
To use these environment types you add "pip" or "buildout" 
to env_types in the vsettings.json. More is explained in the configurations
section below.

Basic Configuration Options
---------------------------

* ``package_name`` - Required. - The desired package name. 
    Letters, Numbers, Underscores only
* ``use_site_packages`` - Default: false - Tells virtualenv whether or 
    not to use site packages
* ``virtualenv_dir`` - Default ``"./vs.env/"`` - Tells virtstrap where to
    place the virtual environment
* ``env_types`` - Default [] - An array with any combination of 
    possible values "pip" or "buildout". See more in the Environment Types
    section above.
* ``pip_requirements_file`` - Required if env_types contains "pip". -
    Path to pip requirements file for this project.
