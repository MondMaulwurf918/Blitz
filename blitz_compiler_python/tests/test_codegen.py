"""
Unit tests for the Blitz code generator.
"""

import unittest
import sys
import os
import tempfile
import subprocess

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lexer import Lexer
from parser import Parser
from codegen import CodeGen

class TestCodeGen(unittest.TestCase):
    def test_simple_program(self):
        source = "fn main() -> i32 { return 42; }"
        
        # Parse the source
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Generate assembly
        codegen = CodeGen(ast)
        asm_code = codegen.generate()
        
        # Check that the assembly contains expected elements
        self.assertIn("main:", asm_code)
        self.assertIn("mov rax, 42", asm_code)
        self.assertIn("ret", asm_code)
    
    def test_arithmetic(self):
        source = "fn main() -> i32 { return 2 + 3 * 4; }"
        
        # Parse the source
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Generate assembly
        codegen = CodeGen(ast)
        asm_code = codegen.generate()
        
        # Check that the assembly contains expected elements
        self.assertIn("main:", asm_code)
        self.assertIn("mov rax, 3", asm_code)  # Left operand of multiplication
        self.assertIn("mov rcx, 4", asm_code)  # Right operand of multiplication
        self.assertIn("imul", asm_code)  # Multiplication instruction
        self.assertIn("add", asm_code)  # Addition instruction
    
    @unittest.skipIf(os.name != 'posix', "Assembly execution tests only run on Linux")
    def test_execution(self):
        """Test that generated code executes correctly (Linux only)."""
        source = "fn main() -> i32 { return 42; }"
        
        # Parse the source
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Generate assembly
        codegen = CodeGen(ast)
        asm_code = codegen.generate()
        
        # Create temporary files
        with tempfile.NamedTemporaryFile(suffix='.asm') as asm_file, \
             tempfile.NamedTemporaryFile(suffix='.o') as obj_file, \
             tempfile.NamedTemporaryFile() as exe_file:
            
            # Write assembly to file
            asm_file.write(asm_code.encode())
            asm_file.flush()
            
            # Assemble
            subprocess.run(['nasm', '-felf64', asm_file.name, '-o', obj_file.name], check=True)
            
            # Link
            subprocess.run(['ld', obj_file.name, '-o', exe_file.name], check=True)
            
            # Execute
            result = subprocess.run([exe_file.name], check=True)
            
            # Check return code (42)
            self.assertEqual(result.returncode, 42)

if __name__ == "__main__":
    unittest.main()