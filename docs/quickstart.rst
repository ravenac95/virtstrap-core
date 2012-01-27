.. _quickstart:

Virtstrap Quickstart Guide
==========================

First, make sure you have virtstrap installed. If you do not, head on over to
the :ref:`install` section.

Simplest virtstrap example
--------------------------

After virtstrap has been installed a command, vstrap, will be available on 
your command line. You can create an virtstrap enabled project just by
doing the following::

    $ mkdir myproject
    $ cd myproject
    $ vstrap init

This creates a virtualenv in the directory ``myproject/.vs.env`` and a 
script called bash script at ``myproject/quickactivate.sh``. 

Finally, do::

    $ source quickactivate.sh
