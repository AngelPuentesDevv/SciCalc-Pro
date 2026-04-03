"""Prueba 3: Trigonometría modo RAD con mpmath — RF-002."""
import pytest
import math
from src.domain.engine.lexer import Lexer
from src.domain.engine.parser import Parser
from src.domain.engine.evaluator import Evaluator
from src.domain.value_objects.angle_mode import AngleMode


def _eval_rad(expr: str, precision: int = 20) -> float:
    """Usa mpmath (precision > 15) para modo RAD."""
    tokens = Lexer(expr).tokenize()
    ast = Parser(tokens).parse()
    result_str = Evaluator(AngleMode.RAD, precision).evaluate(ast)
    return float(result_str)


def test_sin_pi_over_2_rad():
    """sin(π/2) en RAD debe ser 1.0 con alta precisión."""
    result = _eval_rad(f"sin({math.pi / 2})")
    assert math.isclose(result, 1.0, abs_tol=1e-15)


def test_cos_pi_rad():
    """cos(π) en RAD debe ser -1.0."""
    result = _eval_rad(f"cos({math.pi})")
    assert math.isclose(result, -1.0, abs_tol=1e-15)


def test_sin_0_rad():
    result = _eval_rad("sin(0)")
    assert math.isclose(result, 0.0, abs_tol=1e-15)


def test_cos_0_rad():
    result = _eval_rad("cos(0)")
    assert math.isclose(result, 1.0, abs_tol=1e-15)


def test_tan_pi_over_4_rad():
    """tan(π/4) en RAD debe ser 1.0."""
    result = _eval_rad(f"tan({math.pi / 4})")
    assert math.isclose(result, 1.0, abs_tol=1e-12)


def test_mpmath_activated_for_high_precision():
    """Verificar que precision > 15 activa mpmath (resultado tiene más decimales)."""
    tokens = Lexer("sin(1)").tokenize()
    ast = Parser(tokens).parse()
    result_hp = Evaluator(AngleMode.RAD, 25).evaluate(ast)
    # El resultado con mpmath debe tener más de 15 dígitos significativos
    digits = len(result_hp.replace(".", "").replace("-", "").lstrip("0"))
    assert digits >= 15, f"Se esperaban ≥15 dígitos, obtenidos {digits} en {result_hp!r}"
