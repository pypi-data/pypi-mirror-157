=================
setuptools-github
=================

.. image:: https://img.shields.io/pypi/v/click-plus.svg
   :target: https://pypi.org/project/click-plus
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/click-plus.svg
   :target: https://pypi.org/project/click-plus
   :alt: Python versions

.. image:: https://github.com/cav71/click-plus/actions/workflows/master.yml/badge.svg
   :target: https://github.com/cav71/click-plus/actions
   :alt: Build

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Black

.. image:: https://codecov.io/gh/cav71/setuptools-github/branch/master/graph/badge.svg?token=SIUMZ7MT5T
   :target: https://codecov.io/gh/cav71/setuptools-github
   :alt: Coverage

Intro
-----

**setuptools-github** is both a library and a script to support simple life cycle management for
software projects.

It is based on a simple and lightweight approach based on a single **master** branch,
a 'release' branch (**beta/N.M.O**) and finally a 'release' tag (**release/N.M.O**) from which the final
stable packages are generated from.

**setuptools-github** is fully CI/CD integrated (github actions) to eliminate any manual step involved
with software deployment (except code writing).

The generated package provides two important variables (auto updated from the code leveraging automation):

   #. __version__ with the code version
   #. __hash__ with the has commit where the code originates from

To enable..

**Step 1** in your setup.py file::

   from setuptools_github import tools
   initfile = pathlib.Path(__file__).parent / "your_package/__init__.py"
   setup(
        name="a-name",
        version=tools.update_version(initfile, os.getenv("GITHUB_DUMP")),
        ...

*__init__.py* will contain the __version__ and __hash__ variables.

**Step 2** in your .github/workflows/{beta,master,release}.yml action files::

    - name: Build wheel package
      env:
        PYTHONPATH: .
        GITHUB_DUMP: ${{ toJson(github) }}
      run: |
        python -m build

That's all! everytime you'll push code into a branch/N.M.O or tag with release/N.M.O the packages
will be have the __version__/__hash__ variables auto generated.

Initial steps (setup.py)
~~~~~~~~~~~~~~~~~~~~~~~~

First add into the **setup.py** file the function handling the __version__/__hash__ variables::

   from setuptools_github import tools
   initfile = pathlib.Path(__file__).parent / "your_package/__init__.py"

   # this will manage the __version__/__hash__ in initfile using the github envs
   version = tools.update_version(initfile, os.getenv("GITHUB_DUMP"))

   setup(
        name="a-name",
        version=version,
        ...

.. NOTE::
   If the your_package/__init__.py is not present it will be created on the fly when setup.py is run.

Second update the **.github/workflows/{beta,master,release}.yml**

Adds to the workflows yaml files the following::

    - name: Build wheel package
      env:
        PYTHONPATH: .
        GITHUB_DUMP: ${{ toJson(github) }}
      run: |
        python -m build

This will set the environment variable GITHUB_DUMP to a json string from the action context.

Release process
~~~~~~~~~~~~~~~

To begin a new branch from **master**::

    setuptools-github-start-release micro src/your_package/__init__.py

This will create a new branch beta/0.0.0 initially where your-package will build 0.0.0b1, 0.0.0b2 etc. wheels.

Tagging beta/0.0.0 as release/0.0.0, will close the branch and you can restart a new branch::

    setuptools-github-start-release micro src/your_package/__init__.py

This will (1) bump the master __version__ to 0.0.1 (micro), and create a new beta/0.0.1 branch.


The master branch
~~~~~~~~~~~~~~~~~

The **master** holds all the integration work coming from other **dev** branches and for each push
the code undergo the following steps:

    #. unit and integration testing
    #. code coverage
    #. static code check
    #. style check

No package artifact are generated here as the code is not "installable" (eg. is still in source version).

.. image:: maintainer/master-branch.png
   :alt: blha
   :width: 400

The delivery branch
~~~~~~~~~~~~~~~~~~~

The next step is branching **master** into a "delivery" branch using the **beta/N.M.O** name convention.

.. image:: maintainer/delivery-branch.png
   :alt: blha
   :width: 400


package deliveries using beta branches on github:
in a simple model each (automated) commit on a beta/N.M.O branch will result in a package with a __version__
of N.M.Ob<build-number> and a __hash__ corresponding to the commit.

Finally tagging the code with a release/N.M.O tag will result in a package of __version__ N.M.O and "close"
the beta branch (this is the same sorting strategy used in `pep440`).

A script **setuptools-github-start-release** will help to start a beta release branch.


Setup
~~~~~

We start from the master branch (or main, depending on the repository setting).


Requirements
------------

* ``Python`` >= 3.7.
* ``setuptools``


Installation
------------

You can install ``setuptools-github`` via `pip`_ from `PyPI`_::

    $ pip install setuptools-github

Or conda::

    $ conda install -c conda-forge setuptools-github


.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
.. _`pep440`: https://peps.python.org/pep-0440
