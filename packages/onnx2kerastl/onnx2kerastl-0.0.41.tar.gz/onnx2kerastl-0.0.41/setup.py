# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['onnx2kerastl', 'onnx2kerastl.customonnxlayer']

package_data = \
{'': ['*']}

install_requires = \
['keras-data-format-converter==0.0.14',
 'onnx>=1.11.0,<2.0.0',
 'tensorflow-addons>=0.17.1,<0.18.0']

extras_require = \
{':platform_machine == "arm64"': ['tensorflow-macos==2.8.0'],
 ':platform_machine == "x86_64"': ['tensorflow==2.8.0']}

setup_kwargs = {
    'name': 'onnx2kerastl',
    'version': '0.0.41',
    'description': '',
    'long_description': None,
    'author': 'dorhar',
    'author_email': 'doron.harnoy@tensorleap.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
