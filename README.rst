Disclaimer
==========

Neither this project (``pytorch_wheel_installer``) nor its author (Philip Meier) are
affiliated with `PyTorch <https://pytorch.org>`_ in any way. PyTorch and any related
marks are trademarks of Facebook, Inc.

``pytorch_wheel_installer``
===========================

Commandline utility and `tox <https://tox.readthedocs.io/en/latest/)>`_ -plugin to
install PyTorch distributions from the latest wheels. The computation backend (CPU,
CUDA), the language version, and the platform are detected automatically but can be
overwritten manually.

.. start-badges

.. list-table::
    :stub-columns: 1

    * - package
      - |license| |status|
    * - code
      - |black| |mypy| |lint|
    * - tests
      - |tests| |coverage|

.. end-badges

Installation
============

The latest **stable** version can be installed with

.. code-block:: sh

  pip install pytorch_wheel_installer


The **latest** potentially unstable version can be installed with

.. code-block::

  pip install git+https://github.com/pmeier/pytorch_wheel_installer

Usage
=====

CLI
---

The CLI can be invoked by ``pytorch_wheel_installer`` or its shorthand ``pwi``.

.. code-block:: sh

  $ pwi --help
  usage: pwi [-h] [--version] [--distribution DISTRIBUTION] [--backend BACKEND]
             [--language LANGUAGE] [--platform PLATFORM] [--no-install]
             [--pip-cmd PIP_CMD]

  Install PyTorch from the latest wheels.

  optional arguments:
    -h, --help            show this help message and exit
    --version, -v         Show version and exit.
    --distribution DISTRIBUTION, -d DISTRIBUTION
                          PyTorch distribution e.g. 'torch', 'torchvision'.
                          Multiple distributions can be given as a comma-
                          separated list. Defaults to 'torch,torchvision'.
    --backend BACKEND, -b BACKEND
                          Computation backend e.g. 'cpu' or 'cu102'. If not
                          given the backend is automatically detected from the
                          available hardware preferring CUDA over CPU.
    --language LANGUAGE, -l LANGUAGE
                          Language implementation and version tag e.g. 'py3',
                          'cp36'. Defaults to the language version used to run
                          this.
    --platform PLATFORM, -p PLATFORM
                          Platform e.g. 'linux', 'windows', 'macos', or 'any'.
                          Defaults to the platform that is used to run this.
    --no-install, -ni     If given, the selected wheels are written to STDOUT
                          instead of installed.
    --pip-cmd PIP_CMD, -pc PIP_CMD
                          pip command that is used to install the wheels.
                          Defaults to 'pip install'

The ``--no-install`` option can be used to pipe or redirect the wheel links such as
generating a ``requirements.txt`` file:

.. code-block:: sh

  $ pwi --no-install > requirements.txt
  $ cat requirements.txt
  https://download.pytorch.org/whl/cu102/torch-1.5.1-cp36-cp36m-linux_x86_64.whl
  https://download.pytorch.org/whl/cu102/torchvision-0.6.1-cp36-cp36m-linux_x86_64.whl

tox
---

.. code-block:: sh

  $ tox --help
  ...
  optional arguments:
  ...
  --pytorch-install                Install PyTorch distributions from the latest
                                   wheels before the other dependencies. (default:
                                   False)
  --pytorch-distribution DISTRIBUTION
                                   PyTorch distribution e.g. 'torch', 'torchvision'.
                                   Multiple distributions can be given as a
                                   comma-separated list. Defaults to
                                   'torch,torchvision'. (default:torch,torchvision)
  --pytorch-backend BACKEND        Computation backend e.g. 'cpu' or 'cu102'. If not
                                   given the backend is automatically detected from the
                                   available hardware preferring CUDA over CPU.
                                   (default: None)
  --pytorch-language LANGUAGE      Language implementation and version tag e.g. 'py3',
                                   'cp36'. Defaults to the language version used to run
                                   this. (default: None)
  --pytorch-platform PLATFORM      Platform e.g. 'linux', 'windows', 'macos', or 'any'.
                                   Defaults to the platform that is used to run this.
                                   (default: None)
  ...

If ``--pytorch-install`` is not given, nothing is installed.

.. |license|
  image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
    :alt: License

.. |status|
  image:: https://www.repostatus.org/badges/latest/wip.svg
    :alt: Project Status: WIP
    :target: https://www.repostatus.org/#wip

.. |black|
  image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: black
   
.. |mypy|
  image:: http://www.mypy-lang.org/static/mypy_badge.svg
    :target: http://mypy-lang.org/
    :alt: mypy

.. |lint|
  image:: https://github.com/pmeier/pytorch_wheel_installer/workflows/lint/badge.svg
    :target: https://github.com/pmeier/pytorch_wheel_installer/actions?query=workflow%3Alint+branch%3Amaster
    :alt: Lint status via GitHub Actions

.. |tests|
  image:: https://github.com/pmeier/pytorch_wheel_installer/workflows/tests/badge.svg
    :target: https://github.com/pmeier/pytorch_wheel_installer/actions?query=workflow%3Atests+branch%3Amaster
    :alt: Test status via GitHub Actions

.. |coverage|
  image:: https://codecov.io/gh/pmeier/pytorch_wheel_installer/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/pmeier/pytorch_wheel_installer
    :alt: Test coverage via codecov.io
