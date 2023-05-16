from matdocmd.extract import DocumentationExtractor
from . import test_dir_path


def test_extract():
    file = test_dir_path / "reconstruction.m"
    e = DocumentationExtractor(file.absolute().__str__()).result
    print(e)
