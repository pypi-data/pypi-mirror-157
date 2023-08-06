# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['borgini']

package_data = \
{'': ['*']}

install_requires = \
['borgbackup>=1.1.15,<2.0.0', 'pygments>=2.6.1,<3.0.0']

entry_points = \
{'console_scripts': ['borgini = borgini.__main__:main']}

setup_kwargs = {
    'name': 'borgini',
    'version': '1.1.0',
    'description': 'ini config for borg backup',
    'long_description': "borgini\n=======\n.. image:: https://img.shields.io/badge/License-MIT-yellow.svg\n    :target: https://opensource.org/licenses/MIT\n    :alt: License\n.. image:: https://img.shields.io/pypi/v/borgini\n    :target: https://img.shields.io/pypi/v/borgini\n    :alt: pypi\n.. image:: https://github.com/jshwi/borgini/actions/workflows/ci.yml/badge.svg\n    :target: https://github.com/jshwi/borgini/actions/workflows/ci.yml\n    :alt: CI\n.. image:: https://github.com/jshwi/borgini/actions/workflows/codeql-analysis.yml/badge.svg\n    :target: https://github.com/jshwi/borgini/actions/workflows/codeql-analysis.yml\n    :alt: CodeQL\n.. image:: https://codecov.io/gh/jshwi/borgini/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jshwi/borgini\n    :alt: codecov.io\n.. image:: https://readthedocs.org/projects/borgini/badge/?version=latest\n    :target: https://borgini.readthedocs.io/en/latest/?badge=latest\n    :alt: readthedocs.org\n.. image:: https://img.shields.io/badge/python-3.8-blue.svg\n    :target: https://www.python.org/downloads/release/python-380\n    :alt: python3.8\n.. image:: https://img.shields.io/badge/code%20style-black-000000.svg\n    :target: https://github.com/psf/black\n    :alt: black\n\nini config for borg backup\n--------------------------\n\nA wrapper to quickly get you started backing up with borg\n\nAn easy to use ini style and profile based format\n\nRequires:\n\n    - Python 3 >= 3.5.0, plus development headers\n    - OpenSSL >= 1.0.0, plus development headers\n    - libacl (which depends on libattr), both plus development headers\n    - liblz4 >= 1.7.0 (r129)\n    - libzstd >= 1.3.0\n    - libb2\n\n    For information on how to install these dependencies for Borg:\n    https://borgbackup.readthedocs.io/en/stable/installation.html\n\nInitialize the config\n\n.. code-block:: console\n\n    $ borgini\n    First run detected for profile: default\n    Make all necessary changes to config before running this again\n    You can do this by running the command:\n\n    . borgini EDITOR --config --select default\n\n    Default settings have been written to the ``include`` and ``exclude`` lists\n    These can be edited by running:\n\n    . borgini EDITOR --include --select default\n    . borgini EDITOR --exclude --select default\n..\n\n.. note::\n    the ``--select`` optional argument does not need to be passed if using the default profile\n\nEdit the config\n\n.. code-block:: console\n\n    $ borgini vim --config\n..\n\n.. note::\n    The selected editor is up to the user\n\n    The following would also work (provided they are installed)\n\n.. code-block:: console\n\n    $ borgini code --config\n    $ borgini gedit --config\n    $ borgini notepad --config\n..\n\nEnsure to make necessary changes to the ``DEFAULT`` section\n\nAnd ensure to configure the ``SSH`` section if an ssh repo is configured\n\nThe remaining configurations will suite most people\n\nIf you use the ``BORG_PASSPHRASE`` environment variable edit the ``ENVIRONMENT``\nsection to point to the keyfile\n\n.. note::\n    the file should contain one line and a password stored with safe read-write and ownership permissions\n\nEdit the include and exclude files\n\n.. code-block:: console\n\n    $ borgini vim --include  # add a list of paths to back up\n    $ borgini vim --exclude  # add a list of paths to exclude\n..\n\n.. note::\n    The exclude list can contain subdirectories and files listed within the include list\n\n    This will override their inclusion\n\nTo switch between profiles add ``--select PROFILE``\n\n.. code-block:: console\n\n    $ borgini vim --config  # edit default config\n    $ borgini vim --config --select profile2  # edit profile2's config\n    $ borgini vim --include --select profile2  # edit profile2's include file\n    $ borgini vim --exclude --select profile2  # edit profile2's exclude file\n    $ borgini --select profile2  # run profile2's backup\n..\n\nAdd the following for nightly backups at 12:00 to your crontab\n\n.. code-block:: console\n\n    $ 0 0 * * * /usr/local/bin/borgini\n    $ 0 0 * * * /usr/local/bin/borgini -s profile2  # easy for multiple repos\n..\n\n",
    'author': 'jshwi',
    'author_email': 'stephen@jshwisolutions.com',
    'maintainer': 'jshwi',
    'maintainer_email': 'stephen@jshwisolutions.com',
    'url': 'https://pypi.org/project/borgini/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
