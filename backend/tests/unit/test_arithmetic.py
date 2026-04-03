"""Prueba 1: Aritmética básica — RF-001."""
import pytest
from src.domain.engine.lexer import Lexer
from src.domain.engine.parser import Parser
from src.domain.engine.evaluator import Evaluator
from src.domain.value_objects.angle_mode import AngleMode
from src.domain.exceptions.domain_exceptions import DivisionByZeroError


def _eval(expr: str, precision: int = 10) -> str:
    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()
    return Evaluator(AngleMode.DEG, precision).evaluate(ast)


@pytest.mark.parametrize("expr, expected", [
    ("5+3", "8"),
    ("10-4", "6"),
    ("3*7", "21"),
    ("10/4", "2.5"),
    ("2+3*4", "14"),          # precedencia: * antes de +
    ("(2+3)*4", "20"),        # paréntesis
    ("-5+3", "-2"),            # unario negativo
    ("2^3", "8"),              # potencia
    ("100/4+5*2", "35"),       # mixto
])
def test_basic_arithmetic(expr, expected):
    assert _eval(expr) == expected


def test_division_by_zero_raises_typed_error():
    """La división por cero DEBE retornar DivisionByZeroError, no excepción genérica."""
    with pytest.raises(DivisionByZeroError) as exc_info:
        _eval("7/0")
    assert exc_info.value.code == "DIVISION_BY_ZERO"
    assert "División por cero" in exc_info.value.message


def test_division_by_zero_not_http_exception():
    """Verifica que la excepción sea de dominio puro, sin dependencias de FastAPI."""
    from src.domain.exceptions.domain_exceptions import DomainError
    try:
        _eval("1/0")
    except DomainError as e:
        assert e.code == "DIVISION_BY_ZERO"
    except Exception as e:
        pytest.fail(f"Se esperaba DomainError, se obtuvo: {type(e).__name__}: {e}")
