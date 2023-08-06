#!/usr/bin/env python3
"""Predefined tasks for doit"""
from doit_tools.tasks import (
    config, task_compile, task_sort_imports, task_sync,
)

__all__ = ['config', 'task_compile', 'task_sort_imports', 'task_sync']
__version__ = '0.1.5'
