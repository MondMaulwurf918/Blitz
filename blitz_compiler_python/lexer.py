"""
Lexer for the Blitz programming language.
Converts source code into a stream of tokens for parsing.
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # Keywords
    FN = auto()
    RETURN = auto()
    LET = auto()
    
    # Types
    I32 = auto()
    I64 = auto()
    
    # Literals
    NUMBER = auto()
    IDENTIFIER = auto()
    STRING = auto()
    
    # Symbols
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    SEMICOLON = auto() # ;
    ARROW = auto()     # ->
    EQUALS = auto()    # =
    COMMA = auto()     # ,
    
    # Operators
    PLUS = auto()      # +
    MINUS = auto()     # -
    STAR = auto()      # *
    SLASH = auto()     # /
    
    # Special
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"

class LexerError(Exception):
    """Exception raised for errors during lexical analysis."""
    pass

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []
        
        # Define keywords
        self.keywords = {
            'fn': TokenType.FN,
            'return': TokenType.RETURN,
            'let': TokenType.LET,
            'i32': TokenType.I32,
            'i64': TokenType.I64,
        }
    
    def tokenize(self) -> List[Token]:
        """Convert source code into a list of tokens."""
        while self.pos < len(self.source):
            # Skip whitespace
            if self.source[self.pos].isspace():
                self._skip_whitespace()
                continue
            
            # Skip comments
            if self.pos + 1 < len(self.source):
                if self.source[self.pos:self.pos+2] == '//':
                    self._skip_line_comment()
                    continue
                elif self.source[self.pos:self.pos+2] == '/*':
                    self._skip_block_comment()
                    continue
            
            # Check for tokens
            current_char = self.source[self.pos]
            
            if current_char.isalpha() or current_char == '_':
                self._tokenize_identifier()
            elif current_char.isdigit():
                self._tokenize_number()
            elif current_char == '"':
                self._tokenize_string()
            elif current_char == '(':
                self._add_token(TokenType.LPAREN, current_char)
            elif current_char == ')':
                self._add_token(TokenType.RPAREN, current_char)
            elif current_char == '{':
                self._add_token(TokenType.LBRACE, current_char)
            elif current_char == '}':
                self._add_token(TokenType.RBRACE, current_char)
            elif current_char == ';':
                self._add_token(TokenType.SEMICOLON, current_char)
            elif current_char == '=':
                self._add_token(TokenType.EQUALS, current_char)
            elif current_char == ',':
                self._add_token(TokenType.COMMA, current_char)
            elif current_char == '+':
                self._add_token(TokenType.PLUS, current_char)
            elif current_char == '-':
                # Check for arrow token
                if self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '>':
                    self._add_token(TokenType.ARROW, '->')
                    self.pos += 1  # Skip the next character
                else:
                    self._add_token(TokenType.MINUS, current_char)
            elif current_char == '*':
                self._add_token(TokenType.STAR, current_char)
            elif current_char == '/':
                self._add_token(TokenType.SLASH, current_char)
            else:
                raise LexerError(f"Unexpected character '{current_char}' at line {self.line}, column {self.column}")
            
            # Move to next character
            self._advance()
        
        # Add EOF token
        self._add_token(TokenType.EOF, "")
        
        return self.tokens
    
    def _add_token(self, token_type: TokenType, value: str):
        """Add a token to the token list."""
        self.tokens.append(Token(token_type, value, self.line, self.column - len(value)))
    
    def _advance(self):
        """Move to the next character in the source."""
        self.pos += 1
        self.column += 1
    
    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < len(self.source) and self.source[self.pos].isspace():
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def _skip_line_comment(self):
        """Skip a line comment (// ...)."""
        while self.pos < len(self.source) and self.source[self.pos] != '\n':
            self.pos += 1
            self.column += 1
    
    def _skip_block_comment(self):
        """Skip a block comment (/* ... */)."""
        self.pos += 2  # Skip /*
        self.column += 2
        
        while self.pos < len(self.source):
            if self.source[self.pos] == '*' and self.pos + 1 < len(self.source) and self.source[self.pos + 1] == '/':
                self.pos += 2  # Skip */
                self.column += 2
                return
            
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            
            self.pos += 1
        
        raise LexerError("Unterminated block comment")
    
    def _tokenize_identifier(self):
        """Tokenize an identifier or keyword."""
        start_pos = self.pos
        
        while self.pos < len(self.source) and (self.source[self.pos].isalnum() or self.source[self.pos] == '_'):
            self.pos += 1
            self.column += 1
        
        # Get the identifier text
        text = self.source[start_pos:self.pos]
        
        # Check if it's a keyword
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        
        # Add the token and adjust position
        self._add_token(token_type, text)
        self.pos -= 1  # Adjust for the _advance() call that follows
        self.column -= 1
    
    def _tokenize_number(self):
        """Tokenize a number literal."""
        start_pos = self.pos
        
        while self.pos < len(self.source) and self.source[self.pos].isdigit():
            self.pos += 1
            self.column += 1
        
        # Get the number text
        text = self.source[start_pos:self.pos]
        
        # Add the token and adjust position
        self._add_token(TokenType.NUMBER, text)
        self.pos -= 1  # Adjust for the _advance() call that follows
        self.column -= 1
    
    def _tokenize_string(self):
        """Tokenize a string literal."""
        start_pos = self.pos
        self.pos += 1  # Skip opening quote
        self.column += 1
        
        while self.pos < len(self.source) and self.source[self.pos] != '"':
            if self.source[self.pos] == '\n':
                raise LexerError(f"Unterminated string at line {self.line}")
            
            if self.source[self.pos] == '\\' and self.pos + 1 < len(self.source):
                # Handle escape sequences
                self.pos += 1
                self.column += 1
            
            self.pos += 1
            self.column += 1
        
        if self.pos >= len(self.source):
            raise LexerError(f"Unterminated string at line {self.line}")
        
        # Skip closing quote
        self.pos += 1
        self.column += 1
        
        # Get the string text (including quotes)
        text = self.source[start_pos:self.pos]
        
        # Add the token and adjust position
        self._add_token(TokenType.STRING, text)
        self.pos -= 1  # Adjust for the _advance() call that follows
        self.column -= 1