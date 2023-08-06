# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ehrapy',
 'ehrapy.api',
 'ehrapy.api.data',
 'ehrapy.api.io',
 'ehrapy.api.plot',
 'ehrapy.api.preprocessing',
 'ehrapy.api.preprocessing.encoding',
 'ehrapy.api.tools',
 'ehrapy.api.tools.nlp',
 'ehrapy.cli',
 'ehrapy.cli.custom_cli',
 'ehrapy.util']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3.0.1',
 'PyYAML>=5.4.1',
 'anndata>=0.7.6,<0.8.0',
 'camelot-py[base]>=0.10.1',
 'category_encoders>=2.2.2',
 'click>=7.0.0',
 'deep-translator>=1.6.1',
 'deepl>=1.2.0',
 'ipython>=7.30.1',
 'leidenalg>=0.8.7',
 'medcat>=1.2.6',
 'mudata>=0.1.1',
 'pandas>=1.3.3,<2.0.0',
 'pyhpo[all]>=3.0.0',
 'pynndescent>=0.5.4',
 'pypi-latest>=0.1.1',
 'questionary>=1.10.0',
 'requests>=2.26.0',
 'rich>=10.12.0',
 'scanpy>=1.8.2',
 'scikit-learn>=1.0']

entry_points = \
{'console_scripts': ['ehrapy = ehrapy.__main__:main']}

setup_kwargs = {
    'name': 'ehrapy',
    'version': '0.1.0',
    'description': 'Electronic Health Record Analysis with Python.',
    'long_description': '|PyPI| |Python Version| |License| |Read the Docs| |Build| |Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/ehrapy.svg\n   :target: https://pypi.org/project/ehrapy/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/ehrapy\n   :target: https://pypi.org/project/ehrapy\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/github/license/theislab/ehrapy\n   :target: https://opensource.org/licenses/Apache2.0\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/ehrapy/latest.svg?label=Read%20the%20Docs\n   :target: https://ehrapy.readthedocs.io/\n   :alt: Read the documentation at https://ehrapy.readthedocs.io/\n.. |Build| image:: https://github.com/theislab/ehrapy/workflows/Build%20ehrapy%20Package/badge.svg\n   :target: https://github.com/theislab/ehrapy/actions?workflow=Package\n   :alt: Build Package Status\n.. |Tests| image:: https://github.com/theislab/ehrapy/workflows/Run%20ehrapy%20Tests/badge.svg\n   :target: https://github.com/theislab/ehrapy/actions?workflow=Tests\n   :alt: Run Tests Status\n.. |Codecov| image:: https://codecov.io/gh/theislab/ehrapy/branch/master/graph/badge.svg\n   :target: https://codecov.io/gh/theislab/ehrapy\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n.. warning::\n    ehrapy is still in development.\n    If you are willing to try out alpha software feel free to install from source or contact us.\n\nehrapy overview\n===============\n\n.. figure:: https://user-images.githubusercontent.com/21954664/150370356-9f9b170d-76d1-4376-9fd7-54f9f3fb2ae4.png\n   :scale: 100 %\n   :alt: ehrapy overview\n\nFeatures\n--------\n\n* Exploratory analysis of Electronic Health Records\n* Quality control & preprocessing\n* Clustering & trajectory inference\n* Visualization & Exploration\n\n\nInstallation\n------------\n\nYou can install *ehrapy* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install ehrapy\n\n\nUsage\n-----\n\nPlease see the `Usage documentation <Usage_>`_ for details.\n\n.. code:: python\n\n   import ehrapy.api as ep\n\n\nCredits\n-------\n\nThis package was created with cookietemple_ using Cookiecutter_ based on Hypermodern_Python_Cookiecutter_.\n\n.. _cookietemple: https://cookietemple.com\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _PyPI: https://pypi.org/\n.. _Hypermodern_Python_Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _pip: https://pip.pypa.io/\n.. _Usage: https://ehrapy.readthedocs.io/en/latest/usage.html\n',
    'author': 'Lukas Heumos',
    'author_email': 'lukas.heumos@posteo.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/theislab/ehrapy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4',
}


setup(**setup_kwargs)
