# Blitz Compiler Architecture

This document describes the architecture and code flow of the Blitz compiler.

## Overview

The Blitz compiler follows a traditional compiler pipeline architecture:

1. **Lexical Analysis** (Lexer): Converts source code into tokens
2. **Syntax Analysis** (Parser): Converts tokens into an Abstract Syntax Tree (AST)
3. **Code Generation** (CodeGen): Converts AST into assembly code
4. **Assembly & Linking**: External tools (NASM and LD) convert assembly to executable

## Component Diagram

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Source Code│    │    Tokens   │    │     AST     │    │  Assembly   │
│   (.blitz)  │───>│             │───>│             │───>│   (.asm)    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │                 │                  │                   │
       ▼                 ▼                  ▼                   ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Lexer    │    │    Parser   │    │   CodeGen   │    │ NASM & LD   │
│  (lexer.py) │    │ (parser.py) │    │(codegen.py) │    │ (external)  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                                                                ▼
                                                         ┌─────────────┐
                                                         │ Executable  │
                                                         │             │
                                                         └─────────────┘
```

## Component Details

### 1. Lexer (`lexer.py`)

The lexer is responsible for breaking down the source code into a stream of tokens. Each token represents a meaningful unit in the language, such as keywords, identifiers, operators, and literals.

**Key Classes:**
- `TokenType`: Enum defining all possible token types
- `Token`: Data class representing a single token with type, value, and position
- `Lexer`: Main class that performs lexical analysis

**Process:**
1. Initialize with source code
2. Scan through source character by character
3. Identify and create tokens based on patterns
4. Handle whitespace and comments
5. Return a list of tokens

### 2. Parser (`parser.py`)

The parser analyzes the token stream according to the language grammar and builds an Abstract Syntax Tree (AST). The AST represents the hierarchical structure of the program.

**Key Classes:**
- `ASTNode`: Base class for all AST nodes
- Various node types (`NumberNode`, `FunctionNode`, etc.)
- `Parser`: Main class that performs syntax analysis

**Process:**
1. Initialize with token stream
2. Parse functions, statements, and expressions recursively
3. Build AST nodes for each language construct
4. Perform basic type checking
5. Return a complete AST

### 3. Code Generator (`codegen.py`)

The code generator traverses the AST and produces assembly code for the target architecture (x86_64).

**Key Classes:**
- `CodeGen`: Main class that generates assembly code

**Process:**
1. Initialize with AST
2. Traverse AST nodes recursively
3. Generate appropriate assembly instructions for each node
4. Handle function prologue/epilogue
5. Manage stack for local variables
6. Return complete assembly code

### 4. Main Compiler (`blitzc.py`)

The main compiler script orchestrates the entire compilation process.

**Process:**
1. Parse command-line arguments
2. Read source file
3. Initialize and run lexer
4. Initialize and run parser
5. Initialize and run code generator
6. Write assembly output to file
7. Invoke NASM to assemble
8. Invoke LD to link
9. Optionally run the resulting executable

## Data Flow

### Source Code → Tokens

```blitz
fn main() -> i32 {
    return 42;
}
```

Becomes a token stream:

```
[FN, IDENTIFIER("main"), LPAREN, RPAREN, ARROW, I32, LBRACE, RETURN, NUMBER("42"), SEMICOLON, RBRACE]
```

### Tokens → AST

The token stream is parsed into an AST:

```
ProgramNode
└── FunctionNode(name="main", return_type="i32")
    └── ReturnNode
        └── NumberNode(value=42)
```

### AST → Assembly

The AST is converted to x86_64 assembly:

```assembly
; Blitz compiler output
bits 64
default rel

section .text
global main

main:
    push rbp
    mov rbp, rsp
    sub rsp, 0
    mov rax, 42
    leave
    ret
```

## Memory Management

The current implementation does not include memory management as it focuses on the MVP features. Local variables are allocated on the stack during function execution and automatically cleaned up when the function returns.

## Future Architecture Extensions

As the Blitz language evolves, the compiler architecture will be extended to include:

1. **Semantic Analysis**: More robust type checking and semantic validation
2. **Intermediate Representation (IR)**: An architecture-independent representation
3. **Optimization Passes**: Various optimization techniques
4. **Multiple Backends**: Support for different target architectures
5. **Standard Library**: Implementation of standard library functions