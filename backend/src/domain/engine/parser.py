from __future__ import annotations
from dataclasses import dataclass, field
from .tokens import Token, TokenType
from ..exceptions.domain_exceptions import ParseError


# ── AST Nodes ────────────────────────────────────────────────────────────────

@dataclass
class NumberNode:
    value: str  # raw string; resolved to float/mpf at eval time

@dataclass
class BinaryOpNode:
    op: str
    left: "ASTNode"
    right: "ASTNode"

@dataclass
class UnaryOpNode:
    op: str
    operand: "ASTNode"

@dataclass
class FunctionNode:
    name: str
    args: list["ASTNode"] = field(default_factory=list)

ASTNode = NumberNode | BinaryOpNode | UnaryOpNode | FunctionNode


# ── Parser (recursive descent) ───────────────────────────────────────────────

class Parser:
    """Recursive-descent parser. Precedence (low → high):
       + -  →  * /  →  ^ (right-assoc)  →  unary -  →  func / atom
    """

    def __init__(self, tokens: list[Token]):
        self._tokens = tokens
        self._pos = 0

    def parse(self) -> ASTNode:
        node = self._expr()
        if self._current().type != TokenType.EOF:
            raise ParseError(f"Token inesperado: {self._current().value!r}")
        return node

    # ── Grammar rules ────────────────────────────────────────────────────────

    def _expr(self) -> ASTNode:
        return self._additive()

    def _additive(self) -> ASTNode:
        node = self._multiplicative()
        while self._current().type == TokenType.OPERATOR and self._current().value in ('+', '-'):
            op = self._consume().value
            right = self._multiplicative()
            node = BinaryOpNode(op=op, left=node, right=right)
        return node

    def _multiplicative(self) -> ASTNode:
        node = self._power()
        while self._current().type == TokenType.OPERATOR and self._current().value in ('*', '/'):
            op = self._consume().value
            right = self._power()
            node = BinaryOpNode(op=op, left=node, right=right)
        return node

    def _power(self) -> ASTNode:
        base = self._unary()
        if self._current().type == TokenType.OPERATOR and self._current().value == '^':
            self._consume()
            exp = self._power()  # right-associative
            return BinaryOpNode(op='^', left=base, right=exp)
        return base

    def _unary(self) -> ASTNode:
        if self._current().type == TokenType.OPERATOR and self._current().value == '-':
            self._consume()
            return UnaryOpNode(op='-', operand=self._unary())
        return self._primary()

    def _primary(self) -> ASTNode:
        tok = self._current()

        if tok.type == TokenType.NUMBER:
            self._consume()
            return NumberNode(value=tok.value)

        if tok.type == TokenType.FUNC:
            name = self._consume().value
            self._expect(TokenType.LPAREN, f"Se esperaba '(' después de {name!r}")
            args: list[ASTNode] = []
            if self._current().type != TokenType.RPAREN:
                args.append(self._expr())
            self._expect(TokenType.RPAREN, f"Se esperaba ')' al cerrar {name!r}")
            return FunctionNode(name=name, args=args)

        if tok.type == TokenType.LPAREN:
            self._consume()
            node = self._expr()
            self._expect(TokenType.RPAREN, "Se esperaba ')'")
            return node

        raise ParseError(f"Token inesperado: {tok.value!r} en posición {tok.position}")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _current(self) -> Token:
        return self._tokens[self._pos]

    def _consume(self) -> Token:
        tok = self._tokens[self._pos]
        self._pos += 1
        return tok

    def _expect(self, ttype: TokenType, msg: str) -> Token:
        if self._current().type != ttype:
            raise ParseError(msg)
        return self._consume()
