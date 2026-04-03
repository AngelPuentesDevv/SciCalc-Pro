from pydantic import BaseModel, field_validator
from ..validators.regex_validators import validate_expression


class CalculationRequest(BaseModel):
    expression: str
    angle_mode: str = "DEG"
    precision_digits: int = 10
    dry_run: bool = False  # RF-006: True = evalúa sin guardar en historial (preview en vivo)

    @field_validator("expression")
    @classmethod
    def expression_must_be_valid(cls, v: str) -> str:
        if not validate_expression(v):
            raise ValueError(f"Expresión matemática inválida: {v!r}")
        return v.strip()

    @field_validator("angle_mode")
    @classmethod
    def angle_mode_must_be_valid(cls, v: str) -> str:
        if v.upper() not in ("DEG", "RAD"):
            raise ValueError("angle_mode debe ser 'DEG' o 'RAD'")
        return v.upper()

    @field_validator("precision_digits")
    @classmethod
    def precision_in_range(cls, v: int) -> int:
        if not (2 <= v <= 50):
            raise ValueError("precision_digits debe estar entre 2 y 50")
        return v
