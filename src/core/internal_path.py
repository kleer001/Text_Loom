from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING

class InternalPath:

    def __init__(self, path: str):
        self.path = self._normalize_path(path)

    def _normalize_path(self, path: str) ->str:
        return '/' + '/'.join(part for part in path.split('/') if part)

    def parent(self) ->'InternalPath':
        parent_path = '/'.join(self.path.split('/')[:-1])
        return InternalPath(parent_path if parent_path else '/')

    def name(self) ->str:
        return self.path.split('/')[-1]

    def relative_to(self, other: 'InternalPath') ->str:
        self_parts = self.path.split('/')
        other_parts = other.path.split('/')
        i = 0
        while i < len(self_parts) and i < len(other_parts) and self_parts[i
            ] == other_parts[i]:
            i += 1
        up_count = len(other_parts) - i
        down_parts = self_parts[i:]
        relative_parts = ['..'] * up_count + down_parts
        return '/'.join(relative_parts) if relative_parts else '.'

    def __str__(self) ->str:
        return self.path
