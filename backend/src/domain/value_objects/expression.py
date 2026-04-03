import re
from ..exceptions.domain_exceptions import ValidationError

_KNOWN_FUNCS = r"(?:sin|cos|tan|asin|acos|atan|sqrt|log10|log|exp|abs)"
_CONSTANT = r"(?:pi|e)"
_NUMBER = r"\d+(?:\.\d+)?(?:[eE][+-]?\d+)?"
_OPERATOR = r"[+\-*/^]"
_PAREN = r"[()]"
_SPACE = r"\s+"
EXPRESSION_PATTERN = re.compile(
    r"^(?:" + _NUMBER + r"|" + _KNOWN_FUNCS + r"|" + _CONSTANT + r"|" + _OPERATOR + r"|" + _PAREN + r"|" + _SPACE + r")+$"
)


class Expression(str):
    """Value Object: expresión matemática validada con Regex."""

    def __new__(cls, value: str) -> "Expression":
        value = value.strip()
        if not value:
            raise ValidationError("expression", "La expresión no puede estar vacía")
        if not EXPRESSION_PATTERN.match(value):
            raise ValidationError("expression", f"Expresión inválida: {value!r}")
        return super().__new__(cls, value)
