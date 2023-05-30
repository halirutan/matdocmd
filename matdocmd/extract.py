import miss_hit_core.m_lexer as L
import miss_hit_core.m_parser as P
import miss_hit_core.errors as E
import miss_hit_core.m_language
from miss_hit_core.m_ast import *
from miss_hit_core.m_parse_utils import parse_docstrings

from .types import DocType, DocumentationResult, FunctionDocumentationResult
from .ast_utils import extract_function_signature_info


class DocumentationExtractor(AST_Visitor):
    """
    Parses a Matlab file and extracts documentation comment(s) and additional data.
    """
    def __init__(self, file_path: str):
        self.mode = DocType.UNKNOWN
        self.doc = []
        self.skip = False
        self.result = None
        with open(file_path) as f:
            text = f.read()
        mh = E.Message_Handler("trace")
        mh.register_file(file_path)
        lexer = L.MATLAB_Lexer(miss_hit_core.m_language.MATLAB_2021a_Language(), mh, text, file_path)
        self.tbuf = L.Token_Buffer(lexer, Config())
        slp = P.MATLAB_Parser(mh, self.tbuf, Config())
        root = slp.parse_file()
        parse_docstrings(mh, Config(), root, self.tbuf)
        self.root = root
        root.visit(None, self, "Root")

    def get_documentation(self):
        return self.result

    def visit(self, node: Node, n_parent, relation):
        if self.mode == DocType.UNKNOWN:
            if isinstance(node, Class_Definition):
                self.mode = DocType.CLASS
                self.extract_class_documentation(node)
                return
            if isinstance(node, Function_Definition):
                self.mode = DocType.FUNCTION
                self.result = self.extract_function_documentation(node)
                return

    def extract_function_documentation(self, node: Function_Definition) -> DocumentationResult:
        assert isinstance(node, Function_Definition)
        function_token = node.t_fun
        if function_token is None:
            return DocumentationResult.empty()
        signature = extract_function_signature_info(node.n_sig)

        tokens = self.tbuf.tokens
        index = self.find_index_of_first_token_in_line(function_token.location.line + 1)
        doc_comment = []
        while index < len(tokens) and tokens[index].kind == "COMMENT":
            # We need to preserve the indents in the comments since they might be important later
            # Therefore, we're storing the raw_text instead of just the value of the token
            doc_comment.append(str(tokens[index].raw_text))
            index += 1
            if index < len(tokens) and tokens[index].kind == "NEWLINE":
                index += 1

        return FunctionDocumentationResult(
            type=DocType.FUNCTION,
            signature=signature,
            doc_comment="\n".join(doc_comment)
        )

    def extract_class_documentation(self, node) -> DocumentationResult:
        raise NotImplementedError

    def find_index_of_first_token_in_line(self, n: int) -> int:
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


def extract_documentation(file_path: str):
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
