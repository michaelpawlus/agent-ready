"""Check dataclass and registry."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..models import Repo


DetectFn = Callable[[Repo], tuple[bool, str]]


@dataclass
class Check:
    id: str
    category: str
    weight: int
    title: str
    description: str
    remediation: str
    detect: DetectFn
    has_fix_template: bool = False
