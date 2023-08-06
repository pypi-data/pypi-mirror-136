import os
from dataclasses import dataclass, field
from glob import glob
from pathlib import Path
from typing import Any, Dict, Iterator, Iterable, Tuple, Union, List

from doit import get_var
from doit.action import CmdAction
from doit.tools import result_dep

Dependencies = Dict[str, Iterable[str]]


@dataclass
class Config:
    """Task configuration

    :param main_requirements_source: path to the application's production
    requirements. Usually one of setup.cfg, setup.py or pyproject.toml.
    :param main_requirements_file: path to the application's pinned
    requirements.
    :param extra_dependencies: any other extra dependency files to compile. A
    dictionary mapping each pinned requirements filename to an iterable of
    other requirements that should be compiled before it.
    :param install_editable: whether to run pip install -e . on sync
    """
    main_requirements_source: str = 'setup.py'
    main_requirements_file: str = 'requirements.txt'
    extra_dependencies: Dependencies = field(default_factory=dict)
    install_editable: bool = True


config = Config()


def task_sync() -> Dict[str, Any]:
    """Install all necessary requirements in current environment.

    Compile requirements files if not up-to-date and install them using
    pip-sync, then run pip install -e .
    """
    additional_actions = (['pip install -e .'] if config.install_editable
                          else [])
    return {
        'actions': ['pip-sync requirements/*.txt', *additional_actions],
        'uptodate': [result_dep('compile')],
    }


def task_sort_imports() -> Iterator[Dict[str, Any]]:
    """Sort import statements in the project's python files."""
    for filepath in [path for path in glob('**/*.py', recursive=True)
                     if not path.startswith('build')]:
        yield {
            'name': filepath,
            'file_dep': [filepath],
            'actions': ['isort %(dependencies)s'],
        }


def task_compile() -> Iterator[Dict[str, Any]]:
    """Add or update requirements using *.in files as input.

    Run pip-compile to detect changes in source files and add them to *.txt
    files. This will not upgrade versions if it is not necessary, but passing
    upgrade=True will upgrade all dependencies.
    """
    upgrade = get_var('upgrade', False)
    extra_args = '--upgrade' if upgrade else ''
    env = {**os.environ, 'CUSTOM_COMPILE_COMMAND': 'doit compile'}

    for target, deps in _generate_requirements(config.extra_dependencies):
        command = (f'pip-compile --allow-unsafe --generate-hashes {deps[0]} '
                   f'--output-file {target} {extra_args}')
        yield {
            'name': target,
            'file_dep': deps,
            'targets': [target],
            'actions': [CmdAction(command, env=env)],
            'uptodate': [not upgrade]
        }


def _generate_requirements(dependencies: Dependencies) \
        -> Iterator[Tuple[Path, List[Union[Path, str]]]]:
    requirements_path = Path('requirements')
    main_requirements_path = requirements_path / config.main_requirements_file
    yield main_requirements_path, [config.main_requirements_source]

    for target, extra_deps in dependencies.items():
        dep_path = requirements_path / f'{Path(target).stem}.in'
        extra_deps_paths = [requirements_path / dep for dep in extra_deps]
        yield requirements_path / target, [dep_path, *extra_deps_paths]
