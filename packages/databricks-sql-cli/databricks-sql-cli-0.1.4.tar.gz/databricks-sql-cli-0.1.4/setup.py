# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dbsqlcli',
 'dbsqlcli.packages',
 'dbsqlcli.packages.literals',
 'dbsqlcli.packages.special',
 'dbsqlcli.packages.tabular_output']

package_data = \
{'': ['*']}

install_requires = \
['Pygments>=2.11.2,<3.0.0',
 'cli-helpers>=2.2.1,<3.0.0',
 'click>=8.1.2,<9.0.0',
 'configobj>=5.0.6,<6.0.0',
 'databricks-sql-connector>=2.0.0,<3.0.0',
 'pandas==1.3.4',
 'prompt-toolkit>=3.0.29,<4.0.0',
 'sqlparse>=0.4.2,<0.5.0']

entry_points = \
{'console_scripts': ['databricks-sql-cli = dbsqlcli.main:cli',
                     'dbsqlcli = dbsqlcli.main:cli']}

setup_kwargs = {
    'name': 'databricks-sql-cli',
    'version': '0.1.4',
    'description': 'A DBCLI client for Databricks SQL',
    'long_description': "# Introduction\n\nDatabricks SQL CLI is a command line interface (CLI) for [Databricks SQL](https://databricks.com/product/databricks-sql) that can do auto-completion and syntax highlighting, and is a proud member of the dbcli community.\n\n![](https://github.com/databricks/databricks-sql-cli/raw/main/dbsqlcli-demo.gif?raw=True)\n\n# Quick Start\n\n### Install via `pip`\n\nYou'll need Python 3.7 or newer.\n\n```bash\npython3 -m pip install databricks-sql-cli\n```\n\nYou can now run `dbsqlcli` from your terminal.\n\n## Authentication\n\nTo connect with SQL Endpoints `dbsqlcli` needs the host name and http path from the [connection details](https://docs.databricks.com/integrations/bi/jdbc-odbc-bi.html#get-connection-details-for-a-sql-warehouse) screen in Databricks SQL and a [personal access token](https://docs.databricks.com/dev-tools/api/latest/authentication.html#token-management). You can provide these to `dbsqlcli` as command line arguments, by setting environment variables, or by writing them into the `[credentials]` section of the `dbsqlclirc` file (see below).\n\n\n## Config\n\nA config file is automatically created at `~/.dbsqlcli/dbsqlclirc` at first launch (run `dbsqlcli`). See the file itself for a description of all available options.\n\n\n## Run a query\n\n``` bash\n$ dbsqlcli -e 'select id, name from minifigs LIMIT 10'\n```\n\n## Run a .sql file\n\n```bash\n$ dbsqlcli -e query.sql\n```\n\n## Run a .sql file and save to CSV\n\n```bash\n$ dbsqlcli -e query.sql > output.csv\n```\n\n## REPL\n\n``` bash\n$ cd <directory containing dbsqlcli binary>\n$ ./dbslqcli [<database_name>]\n```\n\nRun the `help;` command to see a list of shortcuts\n\n# Features\n\n- Auto-completes as you type for SQL keywords as well as tables and columns in the database.\n- Syntax highlighting.\n- Smart-completion will suggest context-sensitive completion.\n    - `SELECT * FROM <tab>` will only show table names.\n    - `SELECT * FROM users WHERE <tab>` will only show column names.\n- Pretty prints tabular data and various table formats.\n- Some special commands. e.g. Favorite queries.\n- Alias support. Column completions will work even when table names are aliased.\n\n# Usages\n\n```bash\n$ dbsqlcli --help\nUsage: dbsqlcli [OPTIONS] [DATABASE]\n\n  A DBSQL terminal querying client with auto-completion and syntax\n  highlighting.\n\n  Examples:\n    - dbsqlcli\n    - dbsqlcli my_database\n\nOptions:\n  -e, --execute TEXT   Execute a command (or a file) and quit.\n  --hostname TEXT      Hostname  [env var: DBSQLCLI_HOST_NAME]\n  --http-path TEXT     HTTP Path  [env var: DBSQLCLI_HTTP_PATH]\n  --access-token TEXT  Access Token  [env var: DBSQLCLI_ACCESS_TOKEN]\n  --clirc FILE         Location of clirc file.\n  --table-format TEXT  Table format used with -e option.\n  --help               Show this message and exit.\n```\n\n\n# Contributions\n\nWe use [Poetry](https://python-poetry.org/docs/) for development. Follow the instructions to install Poetry on your system. \n\n1. Clone this repository\n2. `poetry install` will install its dependencies\n3. `poetry shell` will activate the local virtual environment\n4. `python app.py` will run `dbsqlcli` incorporating any of your local changes\n\n# Credits\n\nHuge thanks to the maintainers of https://github.com/dbcli/athenacli upon which this project is built.\n\n# Similar projects\n\nThe [DBCLI](https://github.com/dbcli) organization on Github maintains CLIs for numerous database platforms including MySQL, Postgres, and MSSQL. \n\n- https://github.com/dbcli/mycli\n- https://github.com/dbcli/pgcli\n- https://github.com/dbcli/mssql-cli\n\n",
    'author': 'Databricks SQL CLI Maintainers',
    'author_email': 'dbsqlcli-maintainers@databricks.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0',
}


setup(**setup_kwargs)
