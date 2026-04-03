from enum import Enum


class AngleMode(Enum):
    DEG = "DEG"
    RAD = "RAD"

    @classmethod
    def from_str(cls, value: str) -> "AngleMode":
        try:
            return cls(value.upper())
        except ValueError:
            raise ValueError(f"AngleMode inválido: {value!r}. Use 'DEG' o 'RAD'.")
