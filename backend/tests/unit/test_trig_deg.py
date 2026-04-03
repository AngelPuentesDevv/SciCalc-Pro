"""Prueba 2: Trigonometría modo DEG — RF-002."""
import pytest
import math
from src.domain.engine.lexer import Lexer
from src.domain.engine.parser import Parser
from src.domain.engine.evaluator import Evaluator
from src.domain.value_objects.angle_mode import AngleMode
from src.domain.exceptions.domain_exceptions import UndefinedResultError


def _eval_deg(expr: str, precision: int = 15) -> float:
    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()
    result_str = Evaluator(AngleMode.DEG, precision).evaluate(ast)
    return float(result_str)


def test_sin_90_deg():
    """sin(90°) debe ser exactamente 1.0."""
    result = _eval_deg("sin(90)")
    assert math.isclose(result, 1.0, abs_tol=1e-10), f"Esperado 1.0, obtenido {result}"


def test_cos_0_deg():
    """cos(0°) debe ser exactamente 1.0."""
    result = _eval_deg("cos(0)")
    assert math.isclose(result, 1.0, abs_tol=1e-10)


def test_tan_45_deg():
    """tan(45°) debe ser 1.0."""
    result = _eval_deg("tan(45)")
    assert math.isclose(result, 1.0, abs_tol=1e-10)


def test_sin_0_deg():
    result = _eval_deg("sin(0)")
    assert math.isclose(result, 0.0, abs_tol=1e-10)


def test_cos_90_deg():
    result = _eval_deg("cos(90)")
    assert math.isclose(result, 0.0, abs_tol=1e-10)


def test_tan_90_deg_undefined():
    """tan(90°) debe retornar UndefinedResultError."""
    with pytest.raises(UndefinedResultError) as exc_info:
        tokens = Lexer("tan(90)").tokenize()
        ast = Parser(tokens).parse()
        Evaluator(AngleMode.DEG, 15).evaluate(ast)
    assert exc_info.value.code == "UNDEFINED_RESULT"


@pytest.mark.parametrize("expr, expected", [
    ("sin(30)", 0.5),
    ("cos(60)", 0.5),
    ("sin(180)", 0.0),
    ("cos(180)", -1.0),
])
def test_trig_standard_angles_deg(expr, expected):
    result = _eval_deg(expr)
    assert math.isclose(result, expected, abs_tol=1e-10), f"{expr}: esperado {expected}, obtenido {result}"
