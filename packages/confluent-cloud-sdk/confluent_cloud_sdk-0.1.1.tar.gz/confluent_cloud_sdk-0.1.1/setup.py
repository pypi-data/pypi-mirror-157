# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['confluent_cloud_sdk']

package_data = \
{'': ['*']}

install_requires = \
['compose-x-common>=1.0,<2.0', 'requests>=2.27.1,<3.0.0']

setup_kwargs = {
    'name': 'confluent-cloud-sdk',
    'version': '0.1.1',
    'description': 'Confluent Cloud API SDK',
    'long_description': '\n.. meta::\n    :description: Confluent Cloud SDK\n    :keywords: kafka, confluent, cloud, sdk\n\n=======================\nConfluent Cloud SDK\n=======================\n\nSDK to interact with Confluent Cloud API\n\nInstallation\n=============\n\n.. code-block:: bash\n\n    pip install confluent-cloud-sdk\n\nUsage examples\n==================\n\nFor more details, see docs/usage.rst\n\nImports\n---------\n\nTo use Confluent Admin API SDK in a project\n\n\n.. code-block:: python\n\n    from confluent_cloud_sdk.client_factory import ConfluentClient\n    from confluent_cloud_sdk.confluent_iam_v2 import ApiKey\n    from confluent_cloud_sdk.confluent_iam_v2 import ServiceAccount\n\n\n\nInitialize connection\n----------------------\n\n\n.. code-block:: python\n\n    client = ConfluentClient(\n        "cloud_key_key",\n        "cloud_key_secret",\n    )\n\n\nList all service accounts\n--------------------------\n\n.. code-block:: python\n\n    accounts_request = ServiceAccount(client, None).list()\n    for account in accounts_request.json()["data"]\n        print(account)\n\n\nCreate a new service account\n-----------------------------\n\n.. code-block:: python\n\n    new_service_account = ServiceAccount(\n        client, display_name="test_client", description="A simple service account"\n    )\n    try:\n        new_service_account.create() # we try to create the user. If already exists, there will be conflict.\n    except GenericConflict:\n        new_service_account.set_from_read()\n\n    print("SVC ACCOUNT ID IS", new_service_account.obj_id)\n\n\nList all API Keys of the service account\n---------------------------------------------\n\n.. code-block:: python\n\n    new_service_account.import_api_keys()\n    for key in new_service._api_keys:\n        print(key.id)\n\n\nCreate a new API Key for the service account for a given resource\n-------------------------------------------------------------------\n\n.. code-block:: python\n\n    new_api_key = ApiKey(client, display_name="new-test-key")\n    new_api_key.create(\n        owner_id=new_service_account.obj_id,\n        resource_id="cluster_id",\n    )\n',
    'author': 'John Preston',
    'author_email': 'john@ews-network.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
