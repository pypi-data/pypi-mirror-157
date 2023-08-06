# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['instance',
 'statsservice',
 'statsservice.api.v1',
 'statsservice.commands',
 'statsservice.lib',
 'statsservice.models',
 'statsservice.views']

package_data = \
{'': ['*'],
 'statsservice': ['static/*',
                  'static/css/*',
                  'static/img/*',
                  'static/js/*',
                  'templates/*',
                  'translations/*',
                  'translations/fr_FR/LC_MESSAGES/*']}

install_requires = \
['Flask-Babel>=2.0.0,<3.0.0',
 'Flask-Migrate>=3.1.0,<4.0.0',
 'Flask-SQLAlchemy>=2.5.1,<3.0.0',
 'Flask>=2.0.2,<3.0.0',
 'alembic>=1.7.7,<2.0.0',
 'flask_login>=0.6.1,<0.7.0',
 'flask_principal>=0.4.0,<0.5.0',
 'flask_restx>=0.5.1,<0.6.0',
 'jsonschema>=3.2.0,<4.0.0',
 'mypy>=0.950,<0.951',
 'packaging>=21.3,<22.0',
 'psycopg2-binary>=2.9.3,<3.0.0',
 'pymosp>=0.4.2,<0.5.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'types-python-dateutil>=2.8.15,<3.0.0',
 'types-requests>=2.27.25,<3.0.0',
 'types-setuptools>=57.4.14,<58.0.0',
 'typing-extensions>=4.2.0,<5.0.0',
 'werkzeug==2.0.3']

entry_points = \
{'console_scripts': ['monarc-stats-service = runserver:run']}

setup_kwargs = {
    'name': 'statsservice',
    'version': '0.5.2',
    'description': 'Stats Service for MONARC.',
    'long_description': '# Stats Service for MONARC\n\n[![Latest release](https://img.shields.io/github/release/monarc-project/stats-service.svg?style=flat-square)](https://github.com/monarc-project/stats-service/releases/latest)\n[![License](https://img.shields.io/github/license/monarc-project/stats-service.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0.html)\n[![Contributors](https://img.shields.io/github/contributors/monarc-project/stats-service.svg?style=flat-square)](https://github.com/monarc-project/stats-service/graphs/contributors)\n[![Workflow](https://github.com/monarc-project/stats-service/workflows/Python%20application/badge.svg?style=flat-square)](https://github.com/monarc-project/stats-service/actions?query=workflow%3A%22Python+application%22)\n[![CodeQL](https://github.com/monarc-project/stats-service/workflows/CodeQL/badge.svg?style=flat-square)](https://github.com/monarc-project/stats-service/actions?query=workflow%3A%22CodeQL%22)\n[![Translation status](https://translate.monarc.lu/widgets/monarc-stats-service/-/svg-badge.svg)](https://translate.monarc.lu/engage/monarc-stats-service/)\n[![PyPi version](https://img.shields.io/pypi/v/statsservice.svg?style=flat-square)](https://pypi.org/project/statsservice)\n\n## Presentation\n\n[MONARC Stats Service](https://github.com/monarc-project/stats-service) is a libre\nsoftware which is providing:\n\n* an API in order to **collect** statistics from one or several\n  [MONARC](https://github.com/monarc-project/MonarcAppFO) instances and to **return**\n  these statistics with different filters and aggregation methods;\n* a dashboard that summarizes the **current cybersecurity landscape**. The charts are\n  based on the statistics collected.\n\nThis software can be deployed just next to a MONARC instance or on a dedicated server.\n\nThe collected statistics can be sent to an other Stats Service instance.\n\nThe public official instance operated by [CASES](https://www.cases.lu) is\navailable at [https://dashboard.monarc.lu](https://dashboard.monarc.lu).\n\n\n## Documentation\n\nTo be found in the ``docs`` directory of the source code, or\nviewed online [here](https://www.monarc.lu/documentation/stats-service/).\n\nSeveral\n[installation](https://www.monarc.lu/documentation/stats-service/master/installation.html)\nways and the\n[update](https://www.monarc.lu/documentation/stats-service/master/updates.html)\nprocedure are described.\n\n\n## Quick deployment\n\n```bash\n$ git clone https://github.com/monarc-project/stats-service\n$ cd stats-service/\n$ docker-compose up -d\n```\n\nStats Service will be available at:\nhttp://127.0.0.1:5000/api/v1\n\nMore information in the\n[installation section](https://www.monarc.lu/documentation/stats-service/master/installation.html)\nof the documentation.\n\n\n## License\n\n[Stats Service](https://github.com/monarc-project/stats-service) is under the\n[GNU Affero General Public License version 3](https://www.gnu.org/licenses/agpl-3.0.html).\n',
    'author': 'Cédric Bonhomme',
    'author_email': 'cedric@cedricbonhomme.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monarc-project/stats-service',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
