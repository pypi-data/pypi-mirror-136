# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['views_storage', 'views_storage.backends', 'views_storage.serializers']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.4.29,<2.0.0',
 'azure-storage-blob>=12.9.0,<13.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'environs>=9.3.5,<10.0.0',
 'lz4>=3.1.10,<4.0.0',
 'pandas>=1.3.5,<2.0.0',
 'paramiko>=2.9.1,<3.0.0',
 'psycopg2>=2.9.3,<3.0.0',
 'pyarrow>=6.0.1,<7.0.0',
 'pydantic>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'views-storage',
    'version': '1.1.4',
    'description': 'Storage driver used throughout views 3.',
    'long_description': '\n# Views Storage\n\nThis package contains various classes used for storage and retrieval of data\nwithin views. The main class exposed by the package is\n`views_storage.key_value_store.KeyValueStore`. This class is composed with\n`views_storage.serializers.serializer.Serializer` and\n`views_storage.backends.storage_backend.StorageBackend` subclasses to provide\nstorage in various formats using various backends.\n\n## Example\n\n```\nfrom views_storage.key_value_store import KeyValueStore\nfrom views_storage.backends.azure import AzureBlobStorageBackend\nfrom views_storage.serializers.pickle import Pickle\n\nmy_storage = KeyValueStore(\n      backend = AzureBlobStorageBackend(\n         connection_string = "...",\n         container_name = "..."),\n      serializer = Pickle()\n   )\n\nmy_object = ...\n\nmy_storage.store("key", my_object)\n```\n',
    'author': 'Mihai Croicu',
    'author_email': 'mihai.croicu@pcr.uu.se',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/uppsalaconflictdataprogram/views_storage',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
