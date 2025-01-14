from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Any, ClassVar, Dict, List, Optional, Set, Tuple, TYPE_CHECKING


"""
A utility class for handling internal path operations in Text Loom, similar to filesystem paths.

The class manages paths in a Unix-like format, always ensuring proper normalization with
leading slashes and handling relative path calculations.

Path Format:
- Always starts with '/'
- Components separated by '/'
- No trailing slashes
- Empty or root path is represented as '/'

Methods:
   _normalize_path(path): Ensures path follows standard format
       Example: '/a//b/c/' -> '/a/b/c'
   
   parent(): Returns an InternalPath representing the parent directory
       Example: InternalPath('/a/b/c').parent() -> '/a/b'
               InternalPath('/root').parent() -> '/'
   
   name(): Returns the final component of the path
       Example: InternalPath('/a/b/c').name() -> 'c'
               InternalPath('/').name() -> ''
   
   relative_to(other): Calculates relative path from one path to another
       Example: InternalPath('/a/b/c').relative_to(InternalPath('/a')) -> 'b/c'
               InternalPath('/a/b').relative_to(InternalPath('/a/c')) -> '../b'

The class follows similar conventions to Python's pathlib.Path but is specialized
for Text Loom's internal path requirements.
"""

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
