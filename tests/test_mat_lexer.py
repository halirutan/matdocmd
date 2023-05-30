from matdocmd.matlexer import MatLexer
from . import test_dir_path


def create_lexer_test_result(test_data_file: str) -> None:
    """
    Creates comparison data for the lexer test by storing token types and line numbers
    :param test_data_file: Matlab doc comment file used for creating comparison data
    """
    file = test_dir_path / test_data_file
    with open(file.absolute().__str__()) as f:
        data = f.read()
        lexer = MatLexer(data)
        lexer.tokenize()
        output_file = f"{file}.expected"
        with open(output_file, "w") as out:
            for t in lexer.tokens:
                out.write(f"{t.line_number} {t.type}\n")


def do_lexer_test(input_file: str):
    """
    Loads a file with a Matlab doc comment and compares the lexer result.
    The comparison file needs to have the same file name only with ".expected" appended to it.
    :param input_file: Matlab doc comment input file
    """
    file = test_dir_path / input_file
    file = file.absolute().__str__()
    expected_file = f"{file}.expected"
    with open(expected_file) as f:
        expected_data = f.readlines()
    with open(file) as f:
        data = f.read()
        lexer = MatLexer(data)
        lexer.tokenize()
        actual_data = lexer.tokens
    assert len(expected_data) == len(actual_data), "List of results and comparison data are not of the same length"
    assert len(expected_data) > 0, f"Data file {input_file} doesn't contain any data"
    for act, exp in zip(actual_data, expected_data):
        assert f"{act.line_number} {act.type}\n" == exp


def test_lexer():
    do_lexer_test("test_comment.m")
