"""
Unit tests for the Blitz lexer.
"""

import unittest
import sys
import os

# Add parent directory to path to import lexer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lexer import Lexer, TokenType, LexerError

class TestLexer(unittest.TestCase):
    def test_empty_source(self):
        lexer = Lexer("")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.EOF)
    
    def test_function_declaration(self):
        source = "fn main() -> i32 { return 42; }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Check token types (excluding EOF)
        expected_types = [
            TokenType.FN,
            TokenType.IDENTIFIER,  # main
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.ARROW,
            TokenType.I32,
            TokenType.LBRACE,
            TokenType.RETURN,
            TokenType.NUMBER,  # 42
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_variable_declaration(self):
        source = "let i32 x = 10;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.LET,
            TokenType.I32,
            TokenType.IDENTIFIER,  # x
            TokenType.EQUALS,
            TokenType.NUMBER,  # 10
            TokenType.SEMICOLON,
            TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_arithmetic_operators(self):
        source = "a + b - c * d / e;"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        expected_types = [
            TokenType.IDENTIFIER,  # a
            TokenType.PLUS,
            TokenType.IDENTIFIER,  # b
            TokenType.MINUS,
            TokenType.IDENTIFIER,  # c
            TokenType.STAR,
            TokenType.IDENTIFIER,  # d
            TokenType.SLASH,
            TokenType.IDENTIFIER,  # e
            TokenType.SEMICOLON,
            TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_comments(self):
        source = """
        // This is a line comment
        fn main() /* This is a block comment */ {
            return 42; // End of line comment
        }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        
        # Comments should be ignored, so we expect the same tokens as in test_function_declaration
        expected_types = [
            TokenType.FN,
            TokenType.IDENTIFIER,  # main
            TokenType.LPAREN,
            TokenType.RPAREN,
            TokenType.LBRACE,
            TokenType.RETURN,
            TokenType.NUMBER,  # 42
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.EOF
        ]
        
        self.assertEqual(len(tokens), len(expected_types))
        for i, expected_type in enumerate(expected_types):
            self.assertEqual(tokens[i].type, expected_type)
    
    def test_error_handling(self):
        source = "fn main() { return 42; } @"  # Invalid character @
        lexer = Lexer(source)
        with self.assertRaises(LexerError):
            lexer.tokenize()

if __name__ == "__main__":
    unittest.main()