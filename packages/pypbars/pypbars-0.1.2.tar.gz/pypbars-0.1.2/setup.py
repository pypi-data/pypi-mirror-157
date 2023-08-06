#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'pypbars',
        version = '0.1.2',
        description = 'Provides a convenient way to dynamically display multiple progress bars to the terminal.',
        long_description = "# pypbars\n[![build](https://github.com/soda480/pypbars/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/soda480/pypbars/actions/workflows/main.yml)\n[![Code Grade](https://api.codiga.io/project/33925/status/svg)](https://app.codiga.io/public/project/33925/pypbars/dashboard)\n[![codecov](https://codecov.io/gh/soda480/pypbars/branch/main/graph/badge.svg?token=1G4T6UYTEX)](https://codecov.io/gh/soda480/pypbars)\n[![vulnerabilities](https://img.shields.io/badge/vulnerabilities-None-brightgreen)](https://pypi.org/project/bandit/)\n[![PyPI version](https://badge.fury.io/py/pypbars.svg)](https://badge.fury.io/py/pypbars)\n[![python](https://img.shields.io/badge/python-3.9-teal)](https://www.python.org/downloads/)\n\nThe `pypbars` module provides a convenient way to dynamically display multiple progress bars to the terminal. The `pypbars.ProgressBars` class is a subclass of [l2term.Lines](https://pypi.org/project/l2term/) that displays lists to the terminal, and uses [progress1bar.ProgressBar](https://pypi.org/project/progress1bar/) to render the progress bar.\n\n### Installation\n```bash\npip install pypbars\n```\n\n#### [example1](https://github.com/soda480/pypbars/blob/main/examples/example1.py)\n\nCreate `ProgressBars` using a lookup list containing unique values, these identifiers will be used to get the index of the appropriate `ProgressBar` to be updated. The convention is for the function to include `logger.write` calls containing the identifier and a message for when and how the respective progress bar should be updated. In this example the default `regex` dict is used but the caller can specify their own, so long as it contains regular expressions for how to detect when `total`, `count` and optional `alias` are set.\n\n<details><summary>Code</summary>\n\n```Python\nimport asyncio\nimport random\nimport uuid\nfrom pypbars import ProgressBars\n\nasync def do_work(worker, logger=None):\n    logger.write(f'{worker}->worker is {worker[0:random.randint(12, 36)]}')\n    total = random.randint(10, 65)\n    logger.write(f'{worker}->processing total of {total} items')\n    for count in range(total):\n        # mimic an IO-bound process\n        await asyncio.sleep(random.choice([.1, .2, .3]))\n        logger.write(f'{worker}->processed {count}')\n    return total\n\nasync def run(workers):\n    with ProgressBars(lookup=workers, show_prefix=False, show_fraction=False, ticker=9644) as logger:\n        doers = (do_work(worker, logger=logger) for worker in workers)\n        return await asyncio.gather(*doers)\n\ndef main():\n    workers = [str(uuid.uuid4()) for _ in range(12)]\n    print(f'Total of {len(workers)} workers working concurrently')\n    results = asyncio.run(run(workers))\n    print(f'The {len(workers)} workers processed a total of {sum(results)} items')\n\nif __name__ == '__main__':\n    main()\n```\n\n</details>\n\n![example1](https://raw.githubusercontent.com/soda480/pypbars/main/docs/images/example1.gif)\n\n### Development\n\nClone the repository and ensure the latest version of Docker is installed on your development server.\n\nBuild the Docker image:\n```sh\ndocker image build \\\n-t \\\npypbars:latest .\n```\n\nRun the Docker container:\n```sh\ndocker container run \\\n--rm \\\n-it \\\n-v $PWD:/code \\\npypbars:latest \\\nbash\n```\n\nExecute the build:\n```sh\npyb -X\n```\n",
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Other Environment',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Topic :: Software Development :: Libraries',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: System :: Networking',
            'Topic :: System :: Systems Administration'
        ],
        keywords = '',

        author = 'Emilio Reyes',
        author_email = 'soda480@gmail.com',
        maintainer = '',
        maintainer_email = '',

        license = 'Apache License, Version 2.0',

        url = 'https://github.com/soda480/pypbars',
        project_urls = {},

        scripts = [],
        packages = ['pypbars'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'l2term~=0.1.5',
            'progress1bar~=0.2.4'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
