from .tokens import Token, TokenType, SUPPORTED_FUNCTIONS
from ..exceptions.domain_exceptions import LexerError


class Lexer:
    def __init__(self, expression: str):
        self._expr = expression
        self._pos = 0

    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self._pos < len(self._expr):
            ch = self._expr[self._pos]

            if ch.isspace():
                self._pos += 1
                continue

            if ch.isdigit() or (ch == '.' and self._pos + 1 < len(self._expr) and self._expr[self._pos + 1].isdigit()):
                tokens.append(self._read_number())
                continue

            if ch.isalpha():
                tokens.append(self._read_identifier())
                continue

            if ch in ('+', '-', '*', '/', '^'):
                tokens.append(Token(TokenType.OPERATOR, ch, self._pos))
                self._pos += 1
                continue

            if ch == '(':
                tokens.append(Token(TokenType.LPAREN, ch, self._pos))
                self._pos += 1
                continue

            if ch == ')':
                tokens.append(Token(TokenType.RPAREN, ch, self._pos))
                self._pos += 1
                continue

            if ch == ',':
                self._pos += 1
                continue

            raise LexerError(char=ch, position=self._pos)

        tokens.append(Token(TokenType.EOF, "", self._pos))
        return tokens

    def _read_number(self) -> Token:
        start = self._pos
        while self._pos < len(self._expr) and (self._expr[self._pos].isdigit() or self._expr[self._pos] == '.'):
            self._pos += 1
        # Scientific notation: e.g. 1.5e10 or 1.5E-3
        if self._pos < len(self._expr) and self._expr[self._pos] in ('e', 'E'):
            self._pos += 1
            if self._pos < len(self._expr) and self._expr[self._pos] in ('+', '-'):
                self._pos += 1
            while self._pos < len(self._expr) and self._expr[self._pos].isdigit():
                self._pos += 1
        return Token(TokenType.NUMBER, self._expr[start:self._pos], start)

    def _read_identifier(self) -> Token:
        start = self._pos
        while self._pos < len(self._expr) and (self._expr[self._pos].isalnum() or self._expr[self._pos] == '_'):
            self._pos += 1
        name = self._expr[start:self._pos]
        if name in SUPPORTED_FUNCTIONS:
            return Token(TokenType.FUNC, name, start)
        # Treat unknown identifiers like pi, e as numbers resolved at eval time
        return Token(TokenType.NUMBER, name, start)
