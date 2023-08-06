# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['stopwatch', 'tests']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'multi-task-stopwatch',
    'version': '0.1.0',
    'description': 'Simple stop watch, allowing for timing of a number of tasks.',
    'long_description': 'Simple stop watch, allowing for timing of a number of tasks, exposing total running time and running time for each named\ntask - inspired by Spring Framework\n\n## Usage\n\n```python\nimport time\nfrom stopwatch.stopwatch import StopWatch\n\nsw = StopWatch("title")\n\nsw.start("eat")\ntime.sleep(0.12)\nsw.stop()\n\nsw.start("sleep")\ntime.sleep(0.60)\nsw.stop()\n\nsw.start("work")\ntime.sleep(0.35)\nsw.stop()\n\nprint(sw.pretty_print())\n```\n\nresult:\n\n```\n-----------------------------------------\nms     %     Task name\n-----------------------------------------\n120          eat\n605          sleep\n351          work\n-----------------------------------------\n1077         total\n```\n\n## Install\n\n### Pip\n\nInstall via pip:\n\n```shell\npip install simple-stopwatch\n```',
    'author': 'changjian.zcj',
    'author_email': 'changjian.zcj@antfin.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/daya0576/simple-stopwatch',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
