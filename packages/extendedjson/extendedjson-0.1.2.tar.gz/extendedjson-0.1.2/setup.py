# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extendedjson']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'extendedjson',
    'version': '0.1.2',
    'description': 'Easily extend JSON to encode and decode arbitrary Python objects.',
    'long_description': '# extendedjson\n\nEasily extend JSON to encode and decode arbitrary Python objects.\n\n\n## Getting started\n\nYou can [get `extendedjson` from PyPI](https://pypi.org/project/extendedjson),\nwhich means it\'s easily installable with `pip`:\n\n```bash\npython -m pip install extendedjson\n```\n\n\n## Example usage\n\nSuppose you want to extend the JSON format to handle complex numbers,\nwhich corresponds to the type `complex` in Python.\n\nTo do that, you need to:\n\n 1. Determine how a complex number could look like as a JSON dictionary.\n For example, a dictionary with keys `"real"` and `"imag"` is enough to determine what complex number we are talking about.\n 2. Subclass `ExtendedEncoder` and implement the method `encode_complex` that accepts a complex number and returns a dictionary with the format you defined.\n 3. Subclass `ExtendedDecoder` and implement a method `decode_complex` that accepts a dictionary with the format you described and returns an instance of a `complex` number.\n\nHere is the code:\n\n```py\nimport extendedjson as xjson\n\n\nclass MyEncoder(xjson.ExtendedEncoder):\n    def encode_complex(self, c):\n        return {"real": c.real, "imag": c.imag}\n\n\nclass MyDecoder(xjson.ExtendedDecoder):\n    def decode_complex(self, dict_):\n        return complex(dict_["real"], dict_["imag"])\n```\n\nThen, you can use your classes with the standard module `json`,\nby specifying the `cls` keyword argument in the functions `json.load`, `json.loads`, `json.dump`, and `json.dumps`:\n\n```py\nimport json\n\nc = complex(1, 2)\nc_json = json.dumps(c, cls=MyEncoder)\nc_ = json.loads(c_json, cls=MyDecoder)\nprint(c_)  # (1+2j)\nprint(c_ == c)  # True\n```\n\nRefer to [this article](https://mathspp.com/blog/custom-json-encoder-and-decoder) to learn more about the internal details of `extendedjson`.\n\n\n## Changelog\n\nRefer to the [CHANGELOG.md](CHANGELOG.md) file.\n',
    'author': 'Rodrigo Girão Serrão',
    'author_email': '5621605+RodrigoGiraoSerrao@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
