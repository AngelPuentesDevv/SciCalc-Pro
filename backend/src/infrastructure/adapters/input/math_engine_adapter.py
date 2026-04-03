from ....domain.ports.input.calculation_engine_port import CalculationEnginePort
from ....domain.value_objects.angle_mode import AngleMode
from ....domain.engine.lexer import Lexer
from ....domain.engine.parser import Parser
from ....domain.engine.evaluator import Evaluator


class MpMathCalculationEngine(CalculationEnginePort):
    """Adaptador concreto del motor matemático (Lexer → Parser → Evaluator)."""

    def evaluate(
        self,
        expression: str,
        angle_mode: AngleMode = AngleMode.DEG,
        precision_digits: int = 15,
    ) -> str:
        lexer = Lexer(expression)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        evaluator = Evaluator(angle_mode=angle_mode, precision=precision_digits)
        return evaluator.evaluate(ast)
