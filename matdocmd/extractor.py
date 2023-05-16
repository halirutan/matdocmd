import sys

import miss_hit_core.m_lexer as L
import miss_hit_core.m_parser as P
import miss_hit_core.errors as E
import miss_hit_core.m_language
from miss_hit_core.config import Config
from miss_hit.m_sem import treewalk
from miss_hit_core.m_ast import *
from miss_hit_core.m_parse_utils import parse_docstrings
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Union
from os import PathLike


class DocType(Enum):
    UNKNOWN: 0
    FUNCTION: 1
    CLASS: 2


@dataclass
class DocumentationResult:
    type: DocType
    name: str
    arguments: List[str]
    doc_comment: str


class DocumentationExtractor(AST_Visitor):

    extraction_modes = {
        "undefined": 0,
        "class": 1,
        "function": 2
    }

    def __init__(self, root_node: Node, token_buffer: L.Token_Buffer):
        self.root = root_node
        self.tbuf = token_buffer
        self.mode = DocumentationExtractor.extraction_modes["undefined"]
        self.doc = []
        self.skip = False
        self.result = None

    def visit(self, node: Node, n_parent, relation):
        if self.mode == DocumentationExtractor.extraction_modes["undefined"]:
            if isinstance(node, Class_Definition):
                self.mode = DocumentationExtractor.extraction_modes["class"]
                self.extractClassDocumentation(node)
                return
            if isinstance(node, Function_Definition):
                self.mode = DocumentationExtractor.extraction_modes["function"]
                self.result = self.extractFunctionDocumentation(node)
                return

    def extractFunctionDocumentation(self, node) -> DocumentationResult:
        function_token = self.findTokenForNode(node)
        if function_token is None:
            return DocumentationResult()
        name = node.__str__()
        tokens = self.tbuf.tokens
        doc_comment = []
        startIndex = self.findIndexOfFirstTokenInLine(function_token.location.line + 1)
        for index in range(startIndex, len(tokens)):
            if tokens[index].kind == "COMMENT":
                doc_comment.append(tokens[index].raw_text)
        return DocumentationResult(DocType.FUNCTION, name, [],  "\n".join(doc_comment))

    def extractClassDocumentation(self, node) -> DocumentationResult:
        return DocumentationResult()

    def findTokenForNode(self, node: Node):
        for t in self.tbuf.tokens:
            if t.ast_link == node:
                return t
        return None

    def findIndexOfFirstTokenInLine(self, n: int) -> int:
        """
        Finds the first token in the token buffer that a certain the line-number.
        :param n: Line number of token
        :return: Index of first token in line or -1
        """
        tokens = self.tbuf.tokens
        for idx in range(len(tokens)):
            if tokens[idx].location.line == n:
                return idx
        return -1


def extractDocumentation(file_path: str):
    with open(file_path) as f:
        text = f.read()
    mh = E.Message_Handler("trace")
    mh.register_file(file_path)
    lexer = L.MATLAB_Lexer(miss_hit_core.m_language.MATLAB_2021a_Language(), mh, text, file_path)
    tbuf = L.Token_Buffer(lexer, Config())
    slp = P.MATLAB_Parser(mh, tbuf, Config())
    root = slp.parse_file()
    parse_docstrings(mh, Config(), root, tbuf)
    visitor = DocumentationExtractor(root, tbuf)
    root.visit(None, visitor, "Root")
    return visitor.result

# if __name__ == '__main__':
#     filename = "/home/patrick/Workspace/cbs/hMRI-toolbox/hmri_create_FieldMap.m"
#     with open(filename) as f:
#         text = f.read()
#     mh = E.Message_Handler("trace")
#     mh.register_file(filename)
#     lexer = L.MATLAB_Lexer(miss_hit_core.m_language.MATLAB_2021a_Language(), mh, text, filename)
#     tbuf = L.Token_Buffer(lexer, Config())
#     slp = P.MATLAB_Parser(mh, tbuf, Config())
#     root = slp.parse_file()
#     parse_docstrings(mh, Config(), root, tbuf)
#     root.visit(None, DocumentationExtractor(root, tbuf), "Root")

