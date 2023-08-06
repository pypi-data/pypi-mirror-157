# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['health', 'health.classes', 'health.constants']

package_data = \
{'': ['*']}

install_requires = \
['python-dateutil>=2.8.2,<3.0.0', 'xmltodict>=0.13.0,<0.14.0']

setup_kwargs = {
    'name': 'apple-health',
    'version': '2.0.0',
    'description': 'Library to extract information from Apple Health exports.',
    'long_description': '# apple-health\n\n[![Version](https://img.shields.io/pypi/v/apple-health?logo=pypi)](https://pypi.org/project/apple-health)\n[![Quality Gate Status](https://img.shields.io/sonar/alert_status/fedecalendino_apple-health?logo=sonarcloud&server=https://sonarcloud.io)](https://sonarcloud.io/dashboard?id=fedecalendino_apple-health)\n[![CodeCoverage](https://img.shields.io/sonar/coverage/fedecalendino_apple-health?logo=sonarcloud&server=https://sonarcloud.io)](https://sonarcloud.io/dashboard?id=fedecalendino_apple-health)\n\n\nLibrary to extract information from Apple Health exports.\n\n---\n\n## Setup\n\nTo use this library, is required to provide an export file from the iOS Apple Health app. \n\n### How to get the export\n\n1. Open the Apple Health app on your iOS device.\n2. Tap on your profile picture on the top-right corner.\n3. Scroll down until you see a button that reads "Export All Health Data".\n4. After pressing the button, a dialog will appear while the export process is ongoing (it might take a while).\n5. Once the process is finished, a file called `apple_health_export.zip` will be generated.\n6. Finally, from that zip file you\'ll need only the file named `export.xml`.\n \n\n## Usage\n\n```python\nfrom health import HealthData\n\nFILE = "./export/export.xml"\ndata = HealthData.read(\n    FILE,\n    include_me=True,\n    include_activity_summaries=True,\n    include_correlations=False,\n    include_records=False,\n    include_workouts=True,\n)\n\nprint(data.me.biological_sex)\nprint(f"{len(data.activity_summaries)} activity records")\nprint(f"{len(data.correlations)} correlations")\nprint(f"{len(data.records)} records")\nprint(f"{len(data.workouts)} workouts")\n```\n\n```text\n>> HKBiologicalSexMale\n>> 322 activity records\n>> 0 correlations\n>> 0 records\n>> 129 workouts\n```\n\n> note: use the flags on the `HealthData.read` to include only what you need to speed up the reading process.',
    'author': 'Fede Calendino',
    'author_email': 'fede@calendino.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/fedecalendino/apple-health',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
