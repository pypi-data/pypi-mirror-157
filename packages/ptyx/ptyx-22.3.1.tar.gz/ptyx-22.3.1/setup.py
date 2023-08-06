# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ptyx',
 'ptyx.extensions',
 'ptyx.extensions.extended_python',
 'ptyx.extensions.extended_python.tests',
 'ptyx.extensions.geophyx',
 'ptyx.extensions.geophyx.tests',
 'ptyx.extensions.questions',
 'ptyx.extensions.questions.tests']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.1.1,<10.0.0',
 'numpy>=1.23.0,<2.0.0',
 'pdf2image>=1.16.0,<2.0.0',
 'sympy>=1.10.1,<2.0.0']

entry_points = \
{'console_scripts': ['autoqcm = ptyx.extensions.autoqcm.cli:main',
                     'ptyx = ptyx.script:ptyx',
                     'scan = ptyx.extensions.autoqcm.cli:scan']}

setup_kwargs = {
    'name': 'ptyx',
    'version': '22.3.1',
    'description': 'pTyX is a python precompiler for LaTeX.',
    'long_description': "pTyX\n====\n\nOverview\n--------\npTyX is a LaTeX precompilator, written in Python.\npTyX enables to generate LaTeX documents, using custom commands or plain python code.\nOne single pTyX file may generate many latex documents, with different values.\nI developped and used pTyX to make several different versions of a same test in exams,\nfor my student, to discourage cheating.\nSince it uses sympy library, pTyX has symbolic calculus abilities too.\n\nInstallation\n------------\npTyX is only tested on GNU/Linux (Ubuntu), but should work on MacOs X too.\n\nObviously, pTyX needs a working Python installation.\nPython version 3.8 (at least) is required for pTyX to run.\n\npTyX also needs a working LaTeX installation. Command *pdflatex* must be available in your terminal.\n\nThe easiest way to install it is using pip.\n\n    $ pip install ptyx\n\nYou may also download and install the latest version from Github:\n\n    $ git clone https://github.com/wxgeo/ptyx.git\n    $ cd ptyx\n    $ pip install -e .\n\nUsage\n-----\n\nTo compile a pTyX file (see below), open a terminal, go to pTyX directory, and write:\n\n    $ ptyx my_file.ptyx\n\nFor more options:\n\n    $ ptyx --help\n\n\npTyX file specification\n-----------------------\nA pTyX file is essentially a LaTeX file, with a .ptyx extension, (optionally) some custom commands, and embedded python code.\n\nTo include python code in a pTyX file, use the #PYTHON and #END balise.\nA special *write()* command is available, to generate latex code on the flow from python.\n\n    This a simple \\emph{addition}:\\quad\n    #PYTHON\n    from random import randint\n    a = randint(5, 9)\n    b = randint(2, 4)\n    write('%s + %s = %s\\\\' % (a, b, a + b))\n    #END\n    Now, some basic \\emph{subtraction}:\\quad\n    #PYTHON\n    write('%s - %s = %s\\\\' % (a, b, a - b))\n    #END\n\nTo access any python variable outside python code scope, simply add a hashtag before the variable name.\n\nAny valid python expression can also be evaluated this way, using syntax #{python_expr}.\n\n    $#a\\mul#b=#{a*b}$\n\nHowever, pTyX has also reserved tags, like conditionals statements #IF, #ELSE, #ENDIF...\n\n(More to come...)\n",
    'author': 'Nicolas Pourcelot',
    'author_email': 'nicolas.pourcelot@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/wxgeo/ptyx',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
