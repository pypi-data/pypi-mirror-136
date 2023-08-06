# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pksuid']

package_data = \
{'': ['*']}

install_requires = \
['pybase62==0.4.3']

setup_kwargs = {
    'name': 'pksuid',
    'version': '1.0.0',
    'description': 'Python package for generating prefixed ksuids.',
    'long_description': "# Python-PKSUID\n\n### (Prefixed K-Sortable Unique IDentifier)\n\nThis library provides an enhancement to the KSUID identifier \nfirst proposed and used by Segment.io, whose reference implementation\nexists here: \n\n[https://github.com/segmentio/ksuid](https://github.com/segmentio/ksuid)\n\nThis library extends the KSUID specification as the `PKSUID` specification \nwith a prefix, inspired by the Stripe prefixed IDs, such as `txn_1032HU2eZvKYlo2CEPtcnUvl`.\n\nThis in turn makes it easy for developers to see at a glance the underlying type of the \nresource that the identifier refers to, and makes for easier reading/tracing of resources \nin various locations, such as log files.\n\n## Usage\n\nThis package is tested working with `Python 3.6+`\n\nAn example of how to use this library is as follows:\n\n```python\nfrom pksuid import PKSUID\n\n# generate a new unique identifier with the prefix usr\nuid = PKSUID('usr')\n\n# returns 'usr_24OnhzwMpa4sh0NQmTmICTYuFaD'\nprint(uid)\n\n# returns: usr\nprint(uid.get_prefix())\n\n# returns: 1643510623\nprint(uid.get_timestamp())\n\n# returns: 2022-01-30 02:43:43\nprint(uid.get_datetime())\n\n# returns: b'\\x81>*\\xccDJT\\xf1\\xbe\\xa9\\xf3&\\xe8\\xa5\\xb2\\xc1'\nprint(uid.get_payload())\n\n# convert from a str representation back to PKSUID\nuid_from_string = PKSUID.parse('usr_24OnhzwMpa4sh0NQmTmICTYuFaD')\n\n# this can now be used as usual\n# returns: 1643510623\nprint(uid_from_string.get_timestamp())\n\n# conversion to and parsing from bytes is also possible\nuid_as_bytes = uid.bytes()\nuid_from_bytes = PKSUID.parse_bytes(uid_as_bytes)\n\n# returns: 2022-01-30 02:43:43\nprint(uid_from_bytes.get_datetime())\n```\n\n## Testing\n\nRun the unit tests with `poetry run pytest`.",
    'author': 'Sasha Hilton',
    'author_email': 'sashahilton00@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sashahilton00/python-pksuid',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
