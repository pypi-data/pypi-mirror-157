# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['armada_client',
 'armada_client.armada',
 'armada_client.github.com.gogo.protobuf.gogoproto',
 'armada_client.github.com.gogo.protobuf.gogoproto',
 'armada_client.google.api',
 'armada_client.k8s.io.api.core.v1',
 'armada_client.k8s.io.api.core.v1',
 'armada_client.k8s.io.api.networking.v1',
 'armada_client.k8s.io.api.networking.v1',
 'armada_client.k8s.io.apimachinery.pkg.api.resource',
 'armada_client.k8s.io.apimachinery.pkg.api.resource',
 'armada_client.k8s.io.apimachinery.pkg.apis.meta.v1',
 'armada_client.k8s.io.apimachinery.pkg.apis.meta.v1',
 'armada_client.k8s.io.apimachinery.pkg.runtime',
 'armada_client.k8s.io.apimachinery.pkg.runtime',
 'armada_client.k8s.io.apimachinery.pkg.runtime.schema',
 'armada_client.k8s.io.apimachinery.pkg.runtime.schema',
 'armada_client.k8s.io.apimachinery.pkg.util.intstr',
 'armada_client.k8s.io.apimachinery.pkg.util.intstr']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.46.1,<2.0.0', 'grpcio>=1.46.1,<2.0.0']

setup_kwargs = {
    'name': 'armada-client',
    'version': '0.1.0.dev0',
    'description': '',
    'long_description': None,
    'author': 'G Research Open Source Software',
    'author_email': 'armada@armadaproject.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
