# Blitz Language Grammar

This document describes the grammar of the Blitz programming language in its MVP stage.

## Lexical Grammar

### Keywords

- `fn`: Function definition
- `return`: Return statement
- `let`: Variable declaration
- `i32`, `i64`: Integer types

### Literals

- Integer literals: Sequence of digits (e.g., `42`, `100`)
- String literals: Text enclosed in double quotes (e.g., `"hello"`)

### Operators

- Arithmetic: `+`, `-`, `*`, `/`
- Assignment: `=`
- Function return type: `->`

### Delimiters

- Parentheses: `(`, `)`
- Braces: `{`, `}`
- Semicolon: `;`

### Comments

- Line comments: `// comment`
- Block comments: `/* comment */`

## Syntactic Grammar

### Program

A Blitz program consists of one or more function definitions:

```
program ::= function+
```

### Function Definition

```
function ::= "fn" identifier "(" parameters? ")" ("->" type)? block

parameters ::= parameter ("," parameter)*
parameter ::= type identifier
```

### Statements

```
statement ::= returnStmt
            | declarationStmt
            | expressionStmt

returnStmt ::= "return" expression ";"
declarationStmt ::= "let" type? identifier ("=" expression)? ";"
expressionStmt ::= expression ";"
```

### Expressions

```
expression ::= additive

additive ::= multiplicative (("+" | "-") multiplicative)*
multiplicative ::= primary (("*" | "/") primary)*
primary ::= number
          | identifier
          | "(" expression ")"
```

### Types

```
type ::= "i32" | "i64"
```

## Examples

### Simple Function

```blitz
fn main() -> i32 {
    return 42;
}
```

### Variable Declaration and Arithmetic

```blitz
fn calculate() -> i32 {
    let i32 x = 10;
    let i32 y = 5;
    let i32 result = x + y * 2;
    return result;
}
```

## Future Grammar Extensions

The following grammar elements are planned for future versions:

- Boolean expressions and conditional statements
- Loops (while, for)
- Structs and user-defined types
- Pointers and memory management
- String operations
- Function calls with arguments