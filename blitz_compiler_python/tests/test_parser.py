"""
Unit tests for the Blitz parser.
"""

import unittest
import sys
import os

# Add parent directory to path to import parser and lexer
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lexer import Lexer
from parser import Parser, NumberNode, ReturnNode, FunctionNode, BinaryOpNode, ParseError

class TestParser(unittest.TestCase):
    def test_simple_function(self):
        source = "fn main() -> i32 { return 42; }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        # Check program structure
        self.assertEqual(len(program.functions), 1)
        
        # Check function
        func = program.functions[0]
        self.assertEqual(func.name, "main")
        self.assertEqual(func.return_type, "i32")
        self.assertEqual(len(func.parameters), 0)
        self.assertEqual(len(func.body), 1)
        
        # Check return statement
        ret_stmt = func.body[0]
        self.assertIsInstance(ret_stmt, ReturnNode)
        self.assertIsInstance(ret_stmt.expression, NumberNode)
        self.assertEqual(ret_stmt.expression.value, 42)
    
    def test_arithmetic_expression(self):
        source = "fn test() -> i32 { return 2 + 3 * 4; }"
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        # Get the return expression
        ret_stmt = program.functions[0].body[0]
        expr = ret_stmt.expression
        
        # Check expression structure (should be 2 + (3 * 4) due to precedence)
        self.assertIsInstance(expr, BinaryOpNode)
        self.assertIsInstance(expr.left, NumberNode)
        self.assertEqual(expr.left.value, 2)
        
        # Check right side (3 * 4)
        self.assertIsInstance(expr.right, BinaryOpNode)
        self.assertIsInstance(expr.right.left, NumberNode)
        self.assertEqual(expr.right.left.value, 3)
        self.assertIsInstance(expr.right.right, NumberNode)
        self.assertEqual(expr.right.right.value, 4)
    
    def test_multiple_functions(self):
        source = """
        fn add(i32 a, i32 b) -> i32 { return a + b; }
        fn main() -> i32 { return add(2, 3); }
        """
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        program = parser.parse()
        
        # Check program structure
        self.assertEqual(len(program.functions), 2)
        self.assertEqual(program.functions[0].name, "add")
        self.assertEqual(program.functions[1].name, "main")
    
    def test_syntax_error(self):
        source = "fn main() -> i32 { return 42 }"  # Missing semicolon
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        
        with self.assertRaises(ParseError):
            parser.parse()

if __name__ == "__main__":
    unittest.main()