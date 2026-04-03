class DomainError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(message)

    def to_dict(self) -> dict:
        return {"error": True, "code": self.code, "message": self.message}


class DivisionByZeroError(DomainError):
    def __init__(self):
        super().__init__(
            code="DIVISION_BY_ZERO",
            message="Error: División por cero"
        )


class UndefinedResultError(DomainError):
    def __init__(self, expression: str = ""):
        super().__init__(
            code="UNDEFINED_RESULT",
            message=f"Indefinido: {expression}" if expression else "Indefinido"
        )


class LexerError(DomainError):
    def __init__(self, char: str, position: int):
        self.char = char
        self.position = position
        super().__init__(
            code="LEXER_ERROR",
            message=f"Carácter no reconocido '{char}' en posición {position}"
        )


class ParseError(DomainError):
    def __init__(self, message: str):
        super().__init__(code="PARSE_ERROR", message=message)


class ValidationError(DomainError):
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(code="VALIDATION_ERROR", message=f"{field}: {message}")
