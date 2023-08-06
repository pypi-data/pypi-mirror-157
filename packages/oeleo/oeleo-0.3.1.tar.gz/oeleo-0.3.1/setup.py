# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['oeleo']

package_data = \
{'': ['*']}

install_requires = \
['Fabric>=2.7.0,<3.0.0',
 'peewee>=3.15.0,<4.0.0',
 'python-dotenv>=0.20.0,<0.21.0',
 'rich>=12.4.4,<13.0.0']

setup_kwargs = {
    'name': 'oeleo',
    'version': '0.3.1',
    'description': 'A one-eyed tool to copy files with.',
    'long_description': '# oeleo\nPython package / app that can be used for transferring files from an instrument-PC to a data server.\n\nIt is not very sophisticated. But I am not very sophisticated either.\n\n\n## Features (or limitations)\n- Transferring using an ssh connection should preferably be used with key-pairs. This might involve some\n  setting up on your server (ACL) to prevent security issues (the `oeleo` user should only have access to\n  the data folder on your server).\n- Accessing ssh can be done using password if you are not able to figure out how to set proper ownerships \n  on your server.\n- `oeleo` is one-eyed. Meaning that tracking of the "state of the duplicates" is only performed on the local side (where `oeleo` is running).\n- However, `oeleo` contains a `check` method that can help you figure out if starting copying is a  \n  good idea or not. And populate the database if you want.\n- The db that stores information about the "state of the duplicates" is stored relative to the folder \n  `oeleo` is running from. If you delete it (by accident?), `oeleo` will make a new empty one from scratch next time you run.\n- Configuration is done using environmental variables. \n\n## Usage\n\n### Install\n\n```bash\n$ pip install oeleo\n```\n### Run\n\n1. Create an `oeleo` worker instance.\n2. Connect the worker\'s `bookkeeper` to a `sqlite3` database.\n3. Filter local files.\n4. Run to copy files.\n5. Repeat from step 3.\n\n### Examples\n\n#### Simple script for copying between local folders\n\n```python\nimport os\nfrom pathlib import Path\nimport time\n\nimport dotenv\n\nfrom oeleo.checkers import  SimpleChecker\nfrom oeleo.models import SimpleDbHandler\nfrom oeleo.movers import simple_mover\nfrom oeleo.workers import Worker\nfrom oeleo.utils import logger\n\ndef main():\n    log = logger()\n    # assuming you have made a .env file:\n    dotenv.load_dotenv()\n    \n    db_name = os.environ["OELEO_DB_NAME"]\n    base_directory_from = Path(os.environ["OELEO_BASE_DIR_FROM"])\n    base_directory_to = Path(os.environ["OELEO_BASE_DIR_TO"])\n    filter_extension = os.environ["OELEO_FILTER_EXTENSION"]\n    \n    # Making a worker using the Worker class.\n    # You can also use the `factory` functions in `oeleo.worker`\n    # (e.g. `ssh_worker` and `simple_worker`)\n    bookkeeper = SimpleDbHandler(db_name)\n    checker = SimpleChecker()\n    \n    worker = Worker(\n        checker=checker,\n        mover_method=simple_mover,\n        from_dir=base_directory_from,\n        to_dir=base_directory_to,\n        bookkeeper=bookkeeper,\n    )\n    \n    worker.connect_to_db()\n    while True:\n        worker.filter_local(filter_extension)\n        worker.run()\n        time.sleep(300)\n\nif __name__ == "__main__":\n    main()\n```\n\n#### Example .env file\n```.env\nOELEO_BASE_DIR_FROM=C:\\data\\local\nOELEO_BASE_DIR_TO=C:\\data\\pub\nOELEO_FILTER_EXTENSION=csv\nOELEO_DB_NAME=local2pub.db\n\n## only needed for SSHConnector:\n# OELEO_EXTERNAL_HOST=<ssh hostname>\n# OELEO_USERNAME=<ssh username>\n# OELEO_PASSWORD=<ssh password>\n# OELEO_KEY_FILENAME=<ssh key-pair filename>\n```\n\n#### The database\n\nThe database contains one table called `filelist`:\n\n| id  | processed_date             | local_name         | external_name                         | checksum                         | code |\n|-----|:---------------------------|:-------------------|:--------------------------------------|:---------------------------------|-----:|\n| 1   | 2022-07-05 15:55:02.521154 | file_number_1.xyz\t | C:\\oeleo\\check\\to\\file_number_1.xyz   | c976e564825667d7c11ba200457af263 |    1 |\n| 2   | 2022-07-05 15:55:02.536152 | file_number_10.xyz | C:\\oeleo\\check\\to\\file_number_10.xyz\t | d502512c0d32d7503feb3fd3dd287376 |    1 |\n| 3   | 2022-07-05 15:55:02.553157 | file_number_2.xyz\t | C:\\oeleo\\check\\to\\file_number_2.xyz   | cb89d576f5bd57566c78247892baffa3 |    1 |\n\nThe `processed_date` is when the file was last updated (meaning last time `oeleo` found a new checksum for it).\n\nThe table below shows what the different values of `code` mean:\n\n| code | meaning                       |\n|:-----|:------------------------------|\n| 0    | `should-be-copied`            |\n| 1    | `should-be-copied-if-changed` |\n| 2    | `should-not-be-copied`        |\n\nHint! You can **lock** (chose to never copy) a file by editing the `code` manually to 2. \n\n## Future planned improvements\n\nJust plans, no promises given.\n\n- implement a `SharePointConnector`.\n- create CLI.\n- create an executable.\n- create a web-app.\n- create a GUI.\n\n## Status\n\n- [x] Works on my PC &rarr; PC\n- [x] Works on my PC &rarr; my server\n- [x] Works on my server &rarr; my server\n- [ ] Works on my instrument PC &rarr; my instrument PC\n- [ ] Works on my instrument PC &rarr; my server\n- [ ] Works OK\n- [x] Deployable\n- [x] On testpypi\n- [x] On pypi\n\n## Licence\nMIT\n\n## Development\n\nDeveloped using `poetry` on `python 3.10`.\n\n### Some useful commands\n\n#### Update version\n\n```bash\n# update version e.g. from 0.3.1 to 0.3.2:\npoetry version patch\n```\nThen edit `__init__.py`:\n```python\n__version__ = "0.3.2"\n```\n#### Build\n\n```bash\npoetry build\n```\n\n#### Publish\n\n```bash\npoetry publish\n```\n\n### Next\n- publish to pypi.\n\n### Development lead\n- Jan Petter Maehlen, IFE\n',
    'author': 'jepegit',
    'author_email': 'jepe@ife.no',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ife-bat/oeleo',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
