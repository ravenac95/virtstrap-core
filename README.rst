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
For those of you who have not experienced it, ipython does not work well
with Leopard's version of libedit. However, installing readline via
``easy_install`` is the only way to get it to work (oddly enough it won't
work through a pip installation). So this forced me to come up with a 
solution that would solve this problem.

The result is virtstrap.

Is this yet another build tool?
-------------------------------

Yes and no. Virtstrap is not meant to replace pip, virtualenv, or buildout. 
It simply puts all of those tools together so they can work in a friendly
way.

virtstrap Quick Start Guide
---------------------------

The easiest way to get started with virtstrap is to install it
on your local machine by simply doing the following:

``python setup.py install``

or 

``python setup.py develop``

Note: If you don't want to install it into your system. Look below for
an alternative installation.

After the installation is complete you will have PasteScript installed 
on your system, and you can then easily begin a new python project
that utilizes virtstrap.

To start a new project type:

``paster create --template=virtstrap_basic``

Just answer the questions and once it's complete you'll have a project
with virtstrap.py in it's root directory. Finally, you can setup
the virtual environment by typing the following command in the root
directory of the project:

``python virtstrap.py``

Once that's complete you project will contain a new directory called 
vs.env and a file called quickactivate.sh. Be sure to add both into 
your ``.gitignore``, ``.hgignore`` or equivalent. As you won't want 
to pass that around to anyone else you work with.

To get started with the virtual environment simply type:

``source quickactivate.sh``

Now you've got a whole project ready to go with virtstrap.

Doing more with virtstrap
-------------------------

Although convenient, the quick start guide doesn't really show 
you the true power of virtstrap. The best way to use virtstrap 
is with pip and/or buildout. If you configure virtstrap to use
either pip or buildout, virtstrap will automatically execute both 
builds. This allows you to have a completely repeatable project
with all the convenience of using pip or easy_install. 

Environment Types (this is how you make magic happen) 
-----------------------------------------------------

An environment type in virtstrap is any method you'd like to use to
build your environment. Currently the options are to use pip or buildout. 
To use these environment types you add "pip" or "buildout" 
to env_types in the vsettings.json. More is explained in the configurations
section below.

Notes on using buildout
-----------------------

If you use buildout, the only requirement is to create a ``buildout.cfg`` file
in the root of your project. virtstrap will automatically download 
``bootstrap.py`` which is necessary for buildout. 

Configuration Options
---------------------

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

