import math
from .parser import ASTNode, NumberNode, BinaryOpNode, UnaryOpNode, FunctionNode
from ..value_objects.angle_mode import AngleMode
from ..exceptions.domain_exceptions import DivisionByZeroError, UndefinedResultError

# Constantes reconocidas
_CONSTANTS = {"pi": math.pi, "e": math.e}


class Evaluator:
    """Evalúa un AST.
    - precision <= 15: usa float nativo (IEEE 754) para latencia < 50ms P95.
    - precision > 15: usa mpmath con mp.dps = precision.
    """

    def __init__(self, angle_mode: AngleMode = AngleMode.DEG, precision: int = 15):
        self._angle_mode = angle_mode
        self._precision = precision
        self._use_mpmath = precision > 15

        if self._use_mpmath:
            import mpmath
            mpmath.mp.dps = precision
            self._mp = mpmath
        else:
            self._mp = None

    # ── Public ────────────────────────────────────────────────────────────────

    def evaluate(self, node: ASTNode) -> str:
        result = self._eval(node)
        if self._use_mpmath:
            import mpmath
            return mpmath.nstr(result, self._precision, strip_zeros=False)
        # Float: round to precision digits
        formatted = f"{result:.{self._precision}f}"
        # Strip trailing zeros but keep at least one decimal
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
        return formatted

    # ── Private ───────────────────────────────────────────────────────────────

    def _eval(self, node: ASTNode):
        if isinstance(node, NumberNode):
            return self._resolve_number(node.value)

        if isinstance(node, UnaryOpNode):
            val = self._eval(node.operand)
            return -val

        if isinstance(node, BinaryOpNode):
            return self._eval_binary(node)

        if isinstance(node, FunctionNode):
            return self._eval_function(node)

        raise ValueError(f"Nodo AST desconocido: {type(node)}")

    def _resolve_number(self, raw: str):
        if raw in _CONSTANTS:
            val = _CONSTANTS[raw]
            if self._use_mpmath:
                return self._mp.mpf(val)
            return val
        if self._use_mpmath:
            return self._mp.mpf(raw)
        return float(raw)

    def _eval_binary(self, node: BinaryOpNode):
        left = self._eval(node.left)
        right = self._eval(node.right)
        op = node.op

        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise DivisionByZeroError()
            return left / right
        if op == '^':
            return left ** right
        raise ValueError(f"Operador desconocido: {op!r}")

    def _eval_function(self, node: FunctionNode):
        name = node.name
        arg = self._eval(node.args[0]) if node.args else None

        # Convert angle to radians if needed
        if name in ("sin", "cos", "tan", "asin", "acos", "atan"):
            rad_arg = self._to_radians(arg) if name in ("sin", "cos", "tan") else arg

            if name == "tan":
                result = self._call_math("tan", rad_arg)
                # Detect tan(90°), tan(270°), etc. → undefined
                if abs(result) > 1e14:
                    raise UndefinedResultError("tan(90°)")
                return result

            fn_map = {
                "sin": "sin", "cos": "cos",
                "asin": "asin", "acos": "acos", "atan": "atan"
            }
            return self._call_math(fn_map[name], rad_arg if name in ("sin", "cos") else arg)

        fn_map = {
            "sqrt": "sqrt",
            "log": "log",
            "log10": "log10",
            "exp": "exp",
            "abs": "fabs",
        }
        if name in fn_map:
            return self._call_math(fn_map[name], arg)

        raise ValueError(f"Función desconocida: {name!r}")

    def _to_radians(self, angle):
        if self._angle_mode == AngleMode.DEG:
            if self._use_mpmath:
                return self._mp.radians(angle)
            return math.radians(float(angle))
        return angle

    def _call_math(self, fn_name: str, arg):
        if self._use_mpmath:
            return getattr(self._mp, fn_name)(arg)
        return getattr(math, fn_name)(float(arg))
