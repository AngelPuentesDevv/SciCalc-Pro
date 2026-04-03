import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

from ..dtos.calculation_request import CalculationRequest
from ..dtos.calculation_response import CalculationResponse
from ...domain.ports.input.calculation_engine_port import CalculationEnginePort
from ...domain.ports.output.history_repository_port import HistoryRepositoryPort
from ...domain.entities.calculation import Calculation
from ...domain.value_objects.angle_mode import AngleMode
from ...domain.exceptions.domain_exceptions import DomainError

_executor = ProcessPoolExecutor(max_workers=4)


def _compute_sync(expression: str, angle_mode_str: str, precision: int) -> str:
    """Función top-level para ProcessPoolExecutor (debe ser picklable)."""
    from ...domain.engine.lexer import Lexer
    from ...domain.engine.parser import Parser
    from ...domain.engine.evaluator import Evaluator
    from ...domain.value_objects.angle_mode import AngleMode as AM

    lexer = Lexer(expression)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    evaluator = Evaluator(angle_mode=AM(angle_mode_str), precision=precision)
    return evaluator.evaluate(ast)


class EvaluateExpressionUseCase:
    def __init__(
        self,
        engine: CalculationEnginePort,
        history_repo: HistoryRepositoryPort,
        user_id: str,
    ):
        self._engine = engine
        self._history_repo = history_repo
        self._user_id = user_id

    async def execute(self, request: CalculationRequest) -> CalculationResponse:
        start = time.perf_counter()
        angle_mode = AngleMode.from_str(request.angle_mode)

        try:
            if request.precision_digits > 15:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    _executor,
                    _compute_sync,
                    request.expression,
                    request.angle_mode,
                    request.precision_digits,
                )
            else:
                result = self._engine.evaluate(
                    request.expression, angle_mode, request.precision_digits
                )
        except DomainError as e:
            elapsed = (time.perf_counter() - start) * 1000
            return CalculationResponse(
                result="",
                expression=request.expression,
                precision_digits=request.precision_digits,
                elapsed_ms=round(elapsed, 2),
                error=e.message,
                error_code=e.code,
            )

        elapsed = (time.perf_counter() - start) * 1000

        # RF-008: formatear en notación científica si resultado es muy grande o muy pequeño
        try:
            numeric = float(result)
            if numeric != 0 and (abs(numeric) >= 1e12 or abs(numeric) < 1e-12):
                result = f"{numeric:.6e}"
        except (ValueError, TypeError):
            pass  # resultado no numérico (ej. "Error: ...") — no transformar

        # Persist to history (omitido en modo preview/dry_run — RF-006)
        if not request.dry_run:
            calc = Calculation(
                expression=request.expression,
                result=result,
                user_id=self._user_id,
                precision_digits=request.precision_digits,
            )
            await self._history_repo.save(calc)

        return CalculationResponse(
            result=result,
            expression=request.expression,
            precision_digits=request.precision_digits,
            elapsed_ms=round(elapsed, 2),
        )
