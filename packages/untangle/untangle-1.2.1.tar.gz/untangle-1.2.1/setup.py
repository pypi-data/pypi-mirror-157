# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['untangle']
install_requires = \
['defusedxml>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'untangle',
    'version': '1.2.1',
    'description': 'Converts XML to Python objects',
    'long_description': 'untangle\n========\n\n[![Build Status](https://github.com/stchris/untangle/actions/workflows/build.yml/badge.svg)](https://github.com/stchris/untangle/actions)\n[![PyPi version](https://img.shields.io/pypi/v/untangle.svg)](https://pypi.python.org/pypi/untangle)\n<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>\n\n[Documentation](http://readthedocs.org/docs/untangle/en/latest/)\n\n* Converts XML to a Python object.\n* Siblings with similar names are grouped into a list.\n* Children can be accessed with ``parent.child``, attributes with ``element[\'attribute\']``.\n* You can call the ``parse()`` method with a filename, an URL or an XML string.\n* Substitutes ``-``, ``.`` and ``:`` with ``_`` ``<foobar><foo-bar/></foobar>`` can be accessed with ``foobar.foo_bar``, ``<foo.bar.baz/>`` can be accessed with ``foo_bar_baz`` and ``<foo:bar><foo:baz/></foo:bar>`` can be accessed with ``foo_bar.foo_baz``\n* Works with Python 3.7 - 3.10\n\nInstallation\n------------\n\nWith pip:\n```\npip install untangle\n```\n\nWith conda:\n```\nconda install -c conda-forge untangle\n```\n\nConda feedstock maintained by @htenkanen. Issues and questions about conda-forge packaging / installation can be done [here](https://github.com/conda-forge/untangle-feedstock/issues).\n\nUsage\n-----\n(See and run <a href="https://github.com/stchris/untangle/blob/main/examples.py">examples.py</a> or this blog post: [Read XML painlessly](http://pythonadventures.wordpress.com/2011/10/30/read-xml-painlessly/) for more info)\n\n```python\nimport untangle\nobj = untangle.parse(resource)\n```\n\n``resource`` can be:\n\n* a URL\n* a filename\n* an XML string\n\nRunning the above code and passing this XML:\n\n```xml\n<?xml version="1.0"?>\n<root>\n\t<child name="child1"/>\n</root>\n```\nallows it to be navigated from the ``untangle``d object like this:\n\n```python\nobj.root.child[\'name\'] # u\'child1\'\n```\n\nChangelog\n---------\n\nsee CHANGELOG.md\n',
    'author': 'Christian Stefanescu',
    'author_email': 'hello@stchris.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
