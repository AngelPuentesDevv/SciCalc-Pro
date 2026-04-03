from ..exceptions.domain_exceptions import ValidationError

MIN_PRECISION = 2
MAX_PRECISION = 50


class Precision(int):
    """Value Object: número de dígitos decimales en rango [2, 50]."""

    def __new__(cls, value: int) -> "Precision":
        if not (MIN_PRECISION <= value <= MAX_PRECISION):
            raise ValidationError(
                "precision",
                f"La precisión debe estar entre {MIN_PRECISION} y {MAX_PRECISION}, recibido: {value}"
            )
        return super().__new__(cls, value)
