# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['unshell', 'unshell.utils']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'unshell',
    'version': '0.6.0',
    'description': 'Set your shell free !',
    'long_description': '# ![un](./unshell.png) shell\n\n> Set your shell free !\n\nCombine python and shell command.\n\n\n## Features\n\n* **Light**: There are no dependencies\n* **Async**: Work with async/await\n* **Testable**: Unshell script are easily testable because they yield execution control\n\n\n## Setup\n\n```sh\npip install unshell\n```\n\n\n## Usage\n\n### Execute script through Shell\n```\nExecute script through unshell runtime\n\nUsage:\n  unshell COMMAND [SCRIPT_PATH] [ARGS...]\n\nCommands:\n  help      Print this help message\n  run       run a script through unshell runtime\n```\n\nGiven the script: `pause.py` to pause all docker containers\n```py\ndef pause():\n  ids = yield from fetchContainerIds()\n\n  for id in ids:\n    yield f"docker pause {id}"\n\n\ndef fetchContainerIds():\n  ids = yield f"docker ps -q --no-trunc"\n\n  return ids.splitlines()\n```\n\nRun it through unshell\n```sh\nunshell run pause.py\n```\n\n\n### Embedded script inside apps\nGiven the precedent script `pause.py`\n```py\nfrom unshell import Unshell\nimport os\n\ndef main():\n    script = resolve(\'./scripts/pause.js\') # resolve your python module\n    \n    try:\n        Unshell({"env": os.environ})(script)\n    except Exception as err:\n        print(err)\n\n```\n\n\n## Examples\nHere is some examples of what you can do with unshell\n- [Pause containers](examples/pause-resume-container)\n\n## Contribute\n```sh\npoetry config --local virtualenvs.in-project true\npoetry shell\nmake install\nwatch make dev\n```\n\n## License\n\nThe code is available under the [MIT license](LICENSE.md).\n',
    'author': 'Romain Prignon',
    'author_email': 'pro.rprignon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/romainPrignon/unshellPy',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8.5,<4.0.0',
}


setup(**setup_kwargs)
