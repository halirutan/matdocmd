from miss_hit_core.m_ast import *
from .types import FunctionSignatureInfo


def extract_function_signature_info(node: Function_Signature) -> FunctionSignatureInfo:
    """
    Inspects a function signature node and extracts name, arguments, and outputs as strings
    :param node: The AST node that needs to be an instance of Function_Signature
    :return: Extracted Information wrapped in a dataclass
    """
    assert isinstance(node, Function_Signature)
    name = identifier_to_string(node.n_name)
    inputs = []
    for param in node.l_inputs:
        assert isinstance(param, Identifier)
        inputs.append(identifier_to_string(param))

    outputs = []
    for param in node.l_outputs:
        assert isinstance(param, Identifier)
        outputs.append(identifier_to_string(param))
    return FunctionSignatureInfo(name, inputs, outputs)


def identifier_to_string(identifier: Identifier) -> str:
    assert isinstance(identifier, Identifier)
    return identifier.t_ident.value
