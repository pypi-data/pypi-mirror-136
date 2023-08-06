# doit-tools
## Predefined tasks for [doit](https://github.com/pydoit/doit)

This library contains common tasks for:
* [pip-tools](https://github.com/jazzband/pip-tools)
* [isort](https://github.com/PyCQA/isort)

To use these tasks, just install doit-tools and import them in your dodo.py. You
can also configure their behavior by setting the config object's attributes.

``` python
from doit_tools import config, task_compile, task_sync

config.main_requirements_source = 'setup.py'
```

You can find out how to use each task and the config object by reading the
[docstrings](doit_tools/tasks.py)
