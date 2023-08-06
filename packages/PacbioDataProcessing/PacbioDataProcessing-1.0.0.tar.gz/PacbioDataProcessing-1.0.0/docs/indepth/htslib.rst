.. highlight:: shell

.. _htslib:

HTSlib
======

Installing HTSlib
-----------------

Standard installation
^^^^^^^^^^^^^^^^^^^^^

Probably, the easiest way to install ``htslib`` is through your package
manager. But it can be installed from sources; have a look at the
`HTSlib webpage`_.


Spack
^^^^^

Another nice and simple possibility is to use `Spack`_, particularly
if you are going to work on a cluster where using its package manager is
cumbersome, or even impossible. In this case the installation goes as
follows.

1. (Optional) Choosing the compiler. ``HTSlib`` will be compiled from source
   code by ``Spack``. You might need to choose an up-to-date compiler (clusters
   tend to have very stable, ie. old, default compilers).
   See :ref:`using-spack` for details.

2. Installing ``HTSlib`` itself. With the default compiler it would be:
   
   .. code-block:: console

      $ spack install htslib

   or if we want to install it with a specific compiler, say ``gcc-11.3``:

   .. code-block:: console

      $ spack install htslib%gcc@11.3

3. Using ``HTSlib``. |project| depends on ``HTSlib`` at runtime. It means that
   after a successfull installation, the created module must be loaded
   whenever it is needed:

   .. code-block:: console

      $ module load htslib-1.9-gcc-11.3.0-gcc-8.2.0-qynjstf

   .. warning::

      Remember to add that line at the beginning of the slurm batch scripts
      used to submit any executable from |project|.
      

.. _`HTSlib webpage`: https://www.htslib.org/
.. _`Spack`: https://spack.readthedocs.io/
