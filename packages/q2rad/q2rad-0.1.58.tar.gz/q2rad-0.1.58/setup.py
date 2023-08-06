# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['q2rad']

package_data = \
{'': ['*']}

install_requires = \
['q2db', 'q2gui', 'q2report']

entry_points = \
{'console_scripts': ['q2rad = q2rad.q2rad:main']}

setup_kwargs = {
    'name': 'q2rad',
    'version': '0.1.58',
    'description': 'RAD - database, GUI, reports',
    'long_description': '# The RAD (rapid application development) system.  \n**(code less, make more)**  \n**Based on:**  \n    q2db        (https://pypi.org/project/q2db)  \n    q2gui       (https://pypi.org/project/q2gui)  \n    q2report    (https://pypi.org/project/q2report)  \n## Install & run\n**Linux**\n```bash\npython3 -m venv q2rad && source q2rad/bin/activate && pip install --upgrade q2rad  && q2rad\n```\n**Windows**\n```bash\npy -m venv q2rad && call q2rad/scripts/activate && pip install --upgrade q2rad  && q2rad\n```\n## Concept:\n```python\nForms:        #  may have main menu (menubar) definitions\n              #  may be linked to database table\n    \n    Lines:    #  form fields(type of data and type of form control) and \n              #  layout definitions\n              #  when form is linked to database - database columns definitions\n    \n    Actions:  #  applies for database linked forms\n              #  may be standard CRUD-action \n              #  or \n              #  run a script (run reports, forms and etc)\n              #  or\n              #  may have linked subforms (one-to-many)\n\nQueries:      #  query development and debugging tool\n\nReports:      #  multiformat (HTML, DOCX, XLSX) reporting tool \n```\n',
    'author': 'Andrei Puchko',
    'author_email': 'andrei.puchko@gmx.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
