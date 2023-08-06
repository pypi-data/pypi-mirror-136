# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cosmo']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'cosmo',
    'version': '0.2.2',
    'description': 'A web server implementation that uses raw sockets.',
    'long_description': '# Cosmo\n\nCosmo is a multithreaded python webserver that I\'m developing in my spare time. This README will be updated at a later date.\n\n## Example Server\n\n```py\nfrom cosmo import App, Request\n\napp = App("0.0.0.0", 8080)\n\n@app.route("/", "text/html")\ndef index(request: Request):\n    return f"<h1>{request.address}</h1>"\n\napp.serve()\n```',
    'author': 'Kronifer',
    'author_email': '44979306+Kronifer@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kronifer/cosmo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
