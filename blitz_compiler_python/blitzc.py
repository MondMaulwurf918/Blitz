#!/usr/bin/env python3
"""
Blitz Compiler (blitzc.py)
Main entry point for the Blitz compiler.

Usage:
    python blitzc.py [options] input_file.blitz

Options:
    -o, --output <file>      Specify output file name
    -r, --run                Run the compiled program after compilation
    -s, -S, --assembly-only  Generate assembly only, do not assemble or link
    -h, --help               Show this help message
"""

import sys
import os
import argparse
from lexer import Lexer
from parser import Parser
from codegen import CodeGen

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Blitz compiler')
    parser.add_argument('input_file', help='Input .blitz file')
    parser.add_argument('-o', '-O', '--output', help='Output file name')
    parser.add_argument('-r', '-R', '--run', action='store_true', help='Run after compilation')
    parser.add_argument('-s', '-S', '--assembly-only', action='store_true', help='Generate assembly only, do not assemble or link')
    args = parser.parse_args()
    
    # Check if input file exists and has .blitz extension
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.")
        return 1
    
    if not args.input_file.endswith('.blitz'):
        print(f"Warning: Input file '{args.input_file}' does not have .blitz extension.")
    
    # Determine output file name
    output_file = args.output if args.output else os.path.splitext(args.input_file)[0]
    
    try:
        # Read input file
        with open(args.input_file, 'r') as f:
            source_code = f.read()
        
        # Compilation pipeline
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        codegen = CodeGen(ast)
        asm_code = codegen.generate()
        
        # Write assembly output
        asm_file = f"{output_file}.asm"
        with open(asm_file, 'w') as f:
            f.write(asm_code)
            
        print(f"Generated assembly: {asm_file}")
        
        # If assembly-only option is specified, stop here
        if args.assembly_only:
            print(f"Assembly-only mode: Skipping assembly and linking steps.")
            return 0
            
        # Otherwise, continue with assembly and linking
        # Check if we're on Windows
        is_windows = os.name == 'nt'
        
        # Determine appropriate commands and formats
        if is_windows:
            obj_format = "win64"
            nasm_cmd = f"nasm -f{obj_format} {asm_file} -o {output_file}.obj"
            
            # Try to find Visual Studio installation path
            vs_path = None
            potential_paths = [
                "C:\\Program Files\\Microsoft Visual Studio\\2022",
                "C:\\Program Files\\Microsoft Visual Studio\\2019",
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019",
                "C:\\Program Files (x86)\\Microsoft Visual Studio\\2017"
            ]
            
            for path in potential_paths:
                if os.path.exists(path):
                    vs_path = path
                    break
            
            # If we found Visual Studio, try to use its libraries
            if vs_path:
                # Try to find Windows SDK directory for msvcrt.lib
                sdk_dir = None
                msvcrt_dir = None
                
                # Look for Windows SDK
                for path in ["C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\10.0.19041.0\\um\\x64",
                             "C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\10.0.18362.0\\um\\x64",
                             "C:\\Program Files (x86)\\Windows Kits\\10\\Lib\\10.0.17763.0\\um\\x64"]:
                    if os.path.exists(path):
                        sdk_dir = path
                        break
                
                # Look for Visual Studio CRT library
                for path in ["C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC\\14.29.30133\\lib\\x64",
                             "C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Enterprise\\VC\\Tools\\MSVC\\14.29.30133\\lib\\x64",
                             "C:\\Program Files\\Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC\\14.30.30705\\lib\\x64",
                             "C:\\Program Files\\Microsoft Visual Studio\\2022\\Enterprise\\VC\\Tools\\MSVC\\14.30.30705\\lib\\x64"]:
                    if os.path.exists(path):
                        msvcrt_dir = path
                        break
                
                # Build the link command with necessary libraries
                link_cmd = f"link {output_file}.obj /OUT:{output_file}.exe /NOLOGO /SUBSYSTEM:CONSOLE /ENTRY:main"
                
                # Add library paths if found
                if sdk_dir:
                    link_cmd += f" /LIBPATH:\"{sdk_dir}\""
                
                if msvcrt_dir:
                    link_cmd += f" /LIBPATH:\"{msvcrt_dir}\""
                
                # Add the Windows kernel library for console functions
                link_cmd += " kernel32.lib"
                
            exe_file = f"{output_file}.exe"
        else:
            obj_format = "elf64"
            nasm_cmd = f"nasm -f{obj_format} {asm_file} -o {output_file}.o"
            link_cmd = f"ld -o {output_file} {output_file}.o"
            exe_file = output_file
        
        print(f"Assembling with: {nasm_cmd}")
        nasm_result = os.system(nasm_cmd)
        
        if nasm_result != 0:
            print(f"Error: NASM assembler failed. Make sure NASM is installed and in your PATH.")
            print(f"On Windows, download from https://www.nasm.us/ and add to PATH.")
            return 1
        
        print(f"Linking with: {link_cmd}")
        link_result = os.system(link_cmd)
        
        if link_result != 0:
            print(f"Error: Linker failed. Make sure the linker is installed and in your PATH.")
            print(f"On Windows, you need Visual Studio or the Windows SDK for link.exe.")
            return 1
        
        print(f"Successfully compiled {args.input_file} to {exe_file}")
        
        # Run the compiled program if requested
        if args.run:
            print(f"Running {exe_file}...")
            if is_windows:
                exit_code = os.system(exe_file)
            else:
                exit_code = os.system(f"./{exe_file}")
            print(f"Program exited with code {exit_code >> 8}")
        
        return 0
        
    except Exception as e:
        print(f"Compilation error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())