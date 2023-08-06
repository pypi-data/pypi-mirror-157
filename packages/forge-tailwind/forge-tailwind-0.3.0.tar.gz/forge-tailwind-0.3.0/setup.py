# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['forgetailwind', 'forgetailwind.management.commands']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.0', 'forge-core<1.0.0', 'requests>=2.0.0']

entry_points = \
{'console_scripts': ['forge-tailwind = forgetailwind:cli']}

setup_kwargs = {
    'name': 'forge-tailwind',
    'version': '0.3.0',
    'description': 'Work library for Forge',
    'long_description': '# forge-tailwind\n\nUse [Tailwind CSS](https://tailwindcss.com/) with [Django](https://www.djangoproject.com/) *without* requiring npm.\n\nMade possible by the [Tailwind standalone CLI](https://tailwindcss.com/blog/standalone-cli).\n\n## Installation\n\n### Forge installation\n\nThe `forge-tailwind` package is a dependency of [`forge`](https://github.com/forgepackages/forge) and is available as `forge tailwind`.\n\nIf you use the [Forge quickstart](https://www.forgepackages.com/docs/quickstart/),\neverything you need will already be set up.\n\nThe [standard Django installation](#standard-django-installation) can give you an idea of the steps involved.\n\n\n### Standard Django installation\n\nThis package can be used without `forge` by installing it as a regular Django app.\n\nFirst, install `forge-tailwind` from [PyPI](https://pypi.org/project/forge-tailwind/):\n\n```sh\npip install forge-tailwind\n```\n\nThen add it to your `INSTALLED_APPS` in `settings.py`:\n\n```python\nINSTALLED_APPS = [\n    ...\n    "forgetailwind",\n]\n```\n\nCreate a new `tailwind.config.js` file in your project root:\n\n```sh\npython manage.py tailwind init\n```\n\nThis will also create a `tailwind.css` file at `static/src/tailwind.css` where additional CSS can be added.\nYou can customize where these files are located if you need to,\nbut this is the default (requires `STATICFILES_DIRS = [BASE_DIR / "static"]`).\n\nThe `src/tailwind.css` file is then compiled into `dist/tailwind.css` by running `tailwind compile`:\n\n```sh\npython manage.py tailwind compile\n```\n\nWhen you\'re working locally, add `--watch` to automatically compile as changes are made:\n\n```sh\npython manage.py tailwind compile --watch\n```\n\nThen include the compiled CSS in your base template `<head>`:\n\n```html\n<link rel="stylesheet" href="{% static \'dist/tailwind.css\' %}">\n```\n\nIn your repo you will notice a new `.forge` directory that contains `tailwind` (the standalone CLI binary) and `tailwind.version` (to track the version currently installed).\nYou should add `.forge` to your `.gitignore` file.\n\n## Updating Tailwind\n\nThis package manages the Tailwind versioning by comparing `.forge/tailwind.version` to the `FORGE_TAILWIND_VERSION` variable that is injected into your `tailwind.config.js` file.\nWhen you run `tailwind compile`,\nit will automatically check whether your local installation needs to be updated and will update it if necessary.\n\nYou can use the `update` command to update your project to the latest version of Tailwind:\n\n```sh\ntailwind update\n```\n\n## Deployment\n\nIf possible, you should add `static/dist/tailwind.css` to your `.gitignore` and run the `tailwind compile --minify` command as a part of your deployment pipeline.\n\nWhen you run `tailwind compile`, it will automatically check whether the Tailwind standalone CLI has been installed, and install it if it isn\'t.\n\nWhen using Forge on Heroku, we do this for you automatically in our [Forge buildpack](https://github.com/forgepackages/heroku-buildpack-forge/blob/master/bin/files/post_compile).\n',
    'author': 'Dave Gaeddert',
    'author_email': 'dave.gaeddert@dropseed.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.forgepackages.com/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
