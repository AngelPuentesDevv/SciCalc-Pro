from enum import Enum, auto
from dataclasses import dataclass


class TokenType(Enum):
    NUMBER = auto()
    OPERATOR = auto()
    FUNC = auto()
    LPAREN = auto()
    RPAREN = auto()
    EOF = auto()


SUPPORTED_FUNCTIONS = {
    "sin", "cos", "tan", "asin", "acos", "atan",
    "sqrt", "log", "log10", "exp", "abs"
}


@dataclass
class Token:
    type: TokenType
    value: str
    position: int

    def __repr__(self) -> str:
        return f"Token({self.type.name}, {self.value!r}, pos={self.position})"
