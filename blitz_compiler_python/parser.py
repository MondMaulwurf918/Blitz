"""
Parser for the Blitz programming language.
Converts tokens into an Abstract Syntax Tree (AST).
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from lexer import Token, TokenType

class ParseError(Exception):
    """Exception raised for errors during parsing."""
    pass

# AST Node classes
class ASTNode:
    """Base class for all AST nodes."""
    pass

@dataclass
class NumberNode(ASTNode):
    """Node representing a numeric literal."""
    value: int
    
    def __repr__(self):
        return f"Number({self.value})"

@dataclass
class StringNode(ASTNode):
    """Node representing a string literal."""
    value: str
    
    def __repr__(self):
        return f"String({self.value})"

@dataclass
class VariableNode(ASTNode):
    """Node representing a variable reference."""
    name: str
    
    def __repr__(self):
        return f"Variable({self.name})"

@dataclass
class CallNode(ASTNode):
    """Node representing a function call."""
    callee: str
    arguments: List[ASTNode]
    
    def __repr__(self):
        return f"Call({self.callee}, {len(self.arguments)} args)"

@dataclass
class BinaryOpNode(ASTNode):
    """Node representing a binary operation."""
    left: ASTNode
    operator: TokenType
    right: ASTNode
    
    def __repr__(self):
        return f"BinaryOp({self.left}, {self.operator}, {self.right})"

@dataclass
class ReturnNode(ASTNode):
    """Node representing a return statement."""
    expression: ASTNode
    
    def __repr__(self):
        return f"Return({self.expression})"

@dataclass
class DeclarationNode(ASTNode):
    """Node representing a variable declaration."""
    type: Optional[str]  # Optional for type inference
    name: str
    initializer: Optional[ASTNode]
    
    def __repr__(self):
        return f"Declaration({self.type}, {self.name}, {self.initializer})"

@dataclass
class FunctionNode(ASTNode):
    """Node representing a function definition."""
    name: str
    parameters: List[Dict[str, str]]  # List of {name: type} dictionaries
    return_type: Optional[str]
    body: List[ASTNode]
    
    def __repr__(self):
        return f"Function({self.name}, {self.parameters}, {self.return_type}, {len(self.body)} statements)"

@dataclass
class ProgramNode(ASTNode):
    """Root node representing a complete program."""
    functions: List[FunctionNode]
    
    def __repr__(self):
        return f"Program({len(self.functions)} functions)"

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
    
    def parse(self) -> ProgramNode:
        """Parse tokens into an AST."""
        functions = []
        
        while not self._is_at_end():
            functions.append(self._function())
        
        return ProgramNode(functions)
    
    def _function(self) -> FunctionNode:
        """Parse a function definition."""
        self._consume(TokenType.FN, "Expected 'fn' keyword.")
        name = self._consume(TokenType.IDENTIFIER, "Expected function name.").value
        
        self._consume(TokenType.LPAREN, "Expected '(' after function name.")
        parameters = []
        
        # Parse parameters (not implemented in MVP)
        if not self._check(TokenType.RPAREN):
            # TODO: Implement parameter parsing
            pass
        
        self._consume(TokenType.RPAREN, "Expected ')' after parameters.")
        
        # Parse return type
        return_type = None
        if self._match(TokenType.ARROW):
            # Check for i32 or i64 type tokens
            if self._match(TokenType.I32, TokenType.I64):
                return_type = self._previous().value
            else:
                return_type = self._consume(TokenType.IDENTIFIER, "Expected return type.").value
        
        self._consume(TokenType.LBRACE, "Expected '{' before function body.")
        
        # Parse function body
        body = []
        while not self._check(TokenType.RBRACE) and not self._is_at_end():
            body.append(self._statement())
        
        self._consume(TokenType.RBRACE, "Expected '}' after function body.")
        
        return FunctionNode(name, parameters, return_type, body)
    
    def _statement(self) -> ASTNode:
        """Parse a statement."""
        if self._match(TokenType.RETURN):
            return self._return_statement()
        elif self._match(TokenType.LET):
            return self._variable_declaration()
        else:
            return self._expression_statement()
    
    def _return_statement(self) -> ReturnNode:
        """Parse a return statement."""
        value = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after return value.")
        return ReturnNode(value)
    
    def _variable_declaration(self) -> DeclarationNode:
        """Parse a variable declaration."""
        # Check for explicit type
        var_type = None
        if self._match(TokenType.I32) or self._match(TokenType.I64):
            var_type = self._previous().value
        
        name = self._consume(TokenType.IDENTIFIER, "Expected variable name.").value
        
        # Check for initializer
        initializer = None
        if self._match(TokenType.EQUALS):
            initializer = self._expression()
        
        self._consume(TokenType.SEMICOLON, "Expected ';' after variable declaration.")
        
        return DeclarationNode(var_type, name, initializer)
    
    def _expression_statement(self) -> ASTNode:
        """Parse an expression statement."""
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expected ';' after expression.")
        return expr
    
    def _expression(self) -> ASTNode:
        """Parse an expression."""
        return self._addition()
    
    def _addition(self) -> ASTNode:
        """Parse addition and subtraction."""
        expr = self._multiplication()
        
        while self._match(TokenType.PLUS) or self._match(TokenType.MINUS):
            operator = self._previous().type
            right = self._multiplication()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def _multiplication(self) -> ASTNode:
        """Parse multiplication and division."""
        expr = self._primary()
        
        while self._match(TokenType.STAR) or self._match(TokenType.SLASH):
            operator = self._previous().type
            right = self._primary()
            expr = BinaryOpNode(expr, operator, right)
        
        return expr
    
    def _primary(self) -> ASTNode:
        """Parse primary expressions."""
        if self._match(TokenType.NUMBER):
            return NumberNode(int(self._previous().value))
        
        if self._match(TokenType.STRING):
            # Extract the string value without the quotes
            string_token = self._previous().value
            string_value = string_token[1:-1]  # Remove the quotes
            return StringNode(string_value)
        
        if self._match(TokenType.IDENTIFIER):
            name = self._previous().value
            
            # Check if this is a function call
            if self._match(TokenType.LPAREN):
                arguments = []
                
                # Parse arguments if any
                if not self._check(TokenType.RPAREN):
                    arguments.append(self._expression())
                    
                    while self._match(TokenType.COMMA):
                        arguments.append(self._expression())
                
                self._consume(TokenType.RPAREN, "Expected ')' after function arguments.")
                return CallNode(name, arguments)
            
            # Otherwise, it's a variable reference
            return VariableNode(name)
        
        if self._match(TokenType.LPAREN):
            expr = self._expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expr
        
        raise ParseError(f"Expected expression at line {self._peek().line}, column {self._peek().column}")
    
    def _match(self, *types) -> bool:
        """Check if current token matches any of the given types."""
        for type in types:
            if self._check(type):
                self._advance()
                return True
        return False
    
    def _check(self, type) -> bool:
        """Check if current token is of the given type."""
        if self._is_at_end():
            return False
        return self._peek().type == type
    
    def _advance(self) -> Token:
        """Advance to the next token."""
        if not self._is_at_end():
            self.current += 1
        return self._previous()
    
    def _is_at_end(self) -> bool:
        """Check if we've reached the end of the token stream."""
        return self._peek().type == TokenType.EOF
    
    def _peek(self) -> Token:
        """Return the current token."""
        return self.tokens[self.current]
    
    def _previous(self) -> Token:
        """Return the previous token."""
        return self.tokens[self.current - 1]
    
    def _consume(self, type, message) -> Token:
        """Consume the current token if it matches the given type."""
        if self._check(type):
            return self._advance()
        
        token = self._peek()
        raise ParseError(f"{message} Got '{token.value}' at line {token.line}, column {token.column}")