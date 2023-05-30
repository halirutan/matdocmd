from enum import Enum
from typing import List
from dataclasses import dataclass
import re


class CommentType(Enum):
    """
    We need to differentiate what type of comment we're actually processing.
    It's important because doc comments of functions will have a different structure than
    e.g. comments for class methods.
    """
    FUNCTION = 0
    CLASS = 1
    CLASS_METHOD = 2
    CLASS_PROPERTY = 3


class TokenType(Enum):
    """
    We only differentiate between very basic "tokens" aka line-types.
    """
    UNKNOWN = 0
    TEXT = 1
    BULLET = 2
    SECTION = 3
    EMPTY = 4


@dataclass
class Token:
    """
    Tokens contain all information including the tokenized text which not the most efficient
    but easy to work with and probably OK for this kind of application.
    """
    type: TokenType
    line_number: int
    text: str
    indent: int = 0


class MatLexer:
    """
    Tokenizes each line of a MATLAB documentation comment.
    Each line will be wrapped in a `Token` to add additional information.
    Later, the stream of tokens will be processed into Markdown.
    """
    bullet_regex = re.compile("%([ \t]*)[-*](.*)$")
    section_regex = re.compile("%([ \t]*)([A-Z][a-z]+):$")
    empty_regex = re.compile("%[ \t]*$")
    text_regex = re.compile("%([ \t]*)([^\n\r\f\v]+)$")

    def __init__(self, comment_text: str):
        self.data = comment_text
        self.tokens: List[Token] = []

    def tokenize(self) -> None:
        """
        Matches each line of input against known patterns to create tokens from it.
        """
        self.tokens: List[Token] = []
        for n, line in enumerate(iter(self.data.splitlines())):
            if MatLexer.empty_regex.match(line):
                self.tokens.append(Token(TokenType.EMPTY, n, ""))
                continue

            match = MatLexer.bullet_regex.match(line)
            if match:
                self.tokens.append(Token(TokenType.BULLET, n, str(match.group(2)), len(str(match.group(1)))))
                continue

            match = MatLexer.section_regex.match(line)
            if match:
                self.tokens.append(Token(TokenType.SECTION, n, str(match.group(2)), len(str(match.group(1)))))
                continue

            match = MatLexer.text_regex.match(line)
            if match:
                self.tokens.append(Token(TokenType.TEXT, n, str(match.group(2)), len(str(match.group(1)))))
                continue

            self.tokens.append(Token(TokenType.UNKNOWN, n, line))
