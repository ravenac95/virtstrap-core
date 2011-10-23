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
solution that would solve my problem with both buildout and virtualenv+pip.

The result is virtstrap.

Is this yet another build tool?
-------------------------------

Yes and no. Virtstrap is meant as a layer above virtualenv+pip to give
the user buildout like capabilities without all the buildout overhead (i hope).

Why not virtualenv-wrapper?
---------------------------

I looked into using it but it did not fit my particular needs. It's a great
tool but I wanted to create a tool that didn't have to be installed system 
wide to see use. Granted, it is easier when it is installed system wide, but
I believe it's still usable without install virtstrap on the system.

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

You should see ``(yourprojectnameenv)`` preceding your bash shell prompt.
Now you've got a whole project ready to go with virtstrap.

Configuration Options
---------------------

The configuration for a virtstrap project is located, by default, in
``[PROJECT_ROOT_DIR]/conf/proj.conf``. Virtstrap uses python's ConfigParser.
Therefore the configuration options look much like an ``ini`` file.

The most basic configuration looks like this::

    [project]
    name = project-name-here # This must have no spaces

