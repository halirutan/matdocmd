from abc import ABC, abstractmethod
from .types import FunctionDocumentationResult, ClassDocumentationResult


class Style(ABC):
    """
    Base class for turning documentation information about a function or class
    into presentable Markdown. Implementations need to take care of processing or
    parsing the raw MATLAB doc comment and turn it into Markdown text.
    """
    @abstractmethod
    def function_markdown(self, doc: FunctionDocumentationResult) -> str:
        pass

    @abstractmethod
    def class_markdown(self, doc: ClassDocumentationResult) -> str:
        pass


class HMRIStyle(Style):
    def function_markdown(self, doc: FunctionDocumentationResult) -> str:
        pass

    def class_markdown(self, doc: ClassDocumentationResult) -> str:
        pass