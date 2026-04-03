from abc import ABC, abstractmethod
from ...value_objects.angle_mode import AngleMode


class CalculationEnginePort(ABC):
    @abstractmethod
    def evaluate(
        self,
        expression: str,
        angle_mode: AngleMode = AngleMode.DEG,
        precision_digits: int = 15,
    ) -> str:
        """Evalúa una expresión matemática y retorna el resultado como string."""
        ...
