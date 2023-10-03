from matdocmd.extract import DocumentationExtractor
from matdocmd.types import FunctionDocumentationResult
from . import test_dir_path


def test_extract():
    file = test_dir_path / "reconstruction.m"
    e: FunctionDocumentationResult = DocumentationExtractor(file.absolute().__str__()).result
    print("\n\n")
    print(f"Type Info: {e.type}")
    print(f"Function Signature: {e.signature}")
    print(f"Doc String: \n{e.doc_comment}")
