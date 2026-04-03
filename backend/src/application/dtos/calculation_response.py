from pydantic import BaseModel


class CalculationResponse(BaseModel):
    result: str
    expression: str
    precision_digits: int
    elapsed_ms: float
    error: str | None = None
    error_code: str | None = None
