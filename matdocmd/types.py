from enum import Enum
from typing import List
from dataclasses import dataclass, field
from miss_hit_core.m_ast import *


@dataclass
class FunctionSignatureInfo:
    """
    Holds information about a Matlab function signature
    """
    name: str = field(default="")
    inputs: List[str] = field(default=lambda: [])
    outputs: List[str] = field(default=lambda: [])

    @classmethod
    def empty(cls):
        return cls()


class DocType(Enum):
    UNKNOWN = 0
    FUNCTION = 1
    CLASS = 2


@dataclass
class DocumentationResult:
    type: DocType = field(default=DocType.UNKNOWN)

    @classmethod
    def empty(cls):
        return cls()


@dataclass
class FunctionDocumentationResult(DocumentationResult):
    signature: FunctionSignatureInfo = field(default=FunctionSignatureInfo())
    doc_comment: str = field(default="")


@dataclass
class ClassDocumentationResult(DocumentationResult):
    name: str = field(default="")
    methods: List[FunctionDocumentationResult] = field(default=lambda: [])
