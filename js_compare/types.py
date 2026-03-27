from typing import Literal

type AstNodeType = Literal[
    "Identifier",
    "PrivateName",
    "Literals",
    "Programs",
    "Functions",
    "Statements",
    "Declarations",
    "Misc",
    "Expressions",
    "Template Literals",
    "Patterns",
    "Classes",
    "Modules",
]

ast_node_types: list[AstNodeType] = [
    "Identifier",
    "PrivateName",
    "Literals",
    "Programs",
    "Functions",
    "Statements",
    "Declarations",
    "Misc",
    "Expressions",
    "Template Literals",
    "Patterns",
    "Classes",
    "Modules",
]
