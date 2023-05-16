from matdocmd import extractor
import os
from pathlib import Path

test_dir_path = Path(__file__).parent.parent / "test_data"


def test_extractor():
    file = test_dir_path / "avg.m"
    e = extractor.extractDocumentation(file.absolute().__str__())
    print(e)
