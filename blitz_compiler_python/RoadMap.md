# ✅ Blitz Compiler Development Checklist

> ⚡️ Goal: Build a super-simple, whitespace-insensitive, lightning-fast compiled language with a clean syntax and a minimal runtime.

---

## 🚩 Stage 0: Philosophy & Design Principles

- [x] Choose a language name: `Blitz`
- [x] Define core values:
  - [x] Simplicity > Features
  - [x] Compilation speed
  - [x] Executable performance
  - [x] No GC, no runtime
  - [x] No whitespace rules
  - [x] C-like, but friendlier

---

## 🏁 Stage 1: Compiler MVP (Python-Based)

### 📦 File Structure
- [ ] `blitzc.py` – Python compiler entry point
- [ ] `lexer.py` – Optional split-out lexer
- [ ] `parser.py` – Optional split-out parser
- [ ] `codegen.py` – Optional split-out backend
- [ ] `samples/` – Blitz source examples
- [ ] `docs/` – Language reference & grammar
- [ ] `tests/` – Unit tests for components

---

### 🧠 Language Grammar (MVP Subset)

- [x] Functions with `fn` keyword
- [x] `main()` entry point
- [x] Return statement
- [ ] Integer literals only
- [ ] Binary expressions: `+`, `-`, `*`, `/`
- [ ] `let` variable declarations
- [ ] Integer types: `i32`, `i64`
- [ ] Comments: `//` and `/* */`

---

### 🔧 Lexer / Tokenizer

- [ ] Tokenize numbers
- [ ] Tokenize keywords: `fn`, `return`
- [ ] Tokenize symbols: `(`, `)`, `{`, `}`, `->`, `;`
- [ ] Tokenize identifiers
- [ ] Ignore whitespace
- [ ] Error on unknown tokens
- [ ] Tokenize string literals (`"..."`)
- [ ] Tokenize `+`, `-`, `*`, `/`

---

### 🌳 Parser

- [ ] Parse a single `fn main() -> i32 { return N; }`
- [ ] Build AST (Function, Return, Number nodes)
- [ ] Support multiple functions
- [ ] Support binary arithmetic expressions
- [ ] Support variable declarations (`let i32 x = 5;`)
- [ ] Type-checking
- [ ] Scope management
- [ ] Error messages for syntax errors

---

### 🏗️ AST Nodes

- [ ] `Function`
- [ ] `Return`
- [ ] `Number`
- [ ] `BinaryOp`
- [ ] `Variable`
- [ ] `Declaration`

---

### ⚙️ Code Generator (x86_64 Assembly)

- [ ] Generate `global _start` label
- [ ] Emit syscall-based return value
- [ ] Support arithmetic in expressions
- [ ] Emit labels for multiple functions
- [ ] Support local variables on the stack
- [ ] Support calling other functions
- [ ] Add Linux syscall-based print (or use `puts` via libc)

---

### 🧪 Running Code

- [ ] Generate `.asm` file
- [ ] Assemble with `nasm -felf64`
- [ ] Link with `ld -o out`
- [ ] Return code visible via `$?`
- [ ] Add `-run` flag to execute after compile

---

## ✨ Stage 2: Language Expansion

### 💡 Features

- [ ] `let` variables with assignment
- [ ] Arithmetic operators
- [ ] Type inference (`let x = 5;`)
- [ ] Explicit typing (`let i32 x = 5;`)
- [ ] Print integers to stdout
- [ ] Blocks with multiple statements
- [ ] Boolean logic and if/else
- [ ] While loops
- [ ] For loops (C-style)
- [ ] Functions with parameters
- [ ] Structs
- [ ] Pointers and dereferencing

---

### 📦 Standard Library (Built-in Syscalls)

- [ ] `print_i32(val)`
- [ ] `exit(code)`
- [ ] `malloc(size)`
- [ ] `free(ptr)`
- [ ] `read(fd, buf, len)`
- [ ] `write(fd, buf, len)`

---

## 🧪 Stage 3: Testing and Debugging

- [ ] Unit test: Lexer
- [ ] Unit test: Parser
- [ ] Unit test: Codegen
- [ ] Run file and assert `$?` return code
- [ ] Integration test: `blitzc.py test.blitz`
- [ ] Add GitHub Actions CI (optional)

---

## 📚 Stage 4: Documentation

- [ ] `README.md` – Overview and setup
- [ ] `docs/grammar.md` – Blitz grammar
- [ ] `docs/stdlib.md` – Blitz standard library
- [ ] `docs/tutorial.md` – Write your first Blitz program
- [ ] `docs/architecture.md` – Compiler structure and code flow

---

## 🧵 Stage 5: Advanced Roadmap (Future)

- [ ] Add support for `strings`
- [ ] Add basic allocator
- [ ] Implement WASM backend
- [ ] Build a self-hosting Blitz compiler
- [ ] Create `.blitz` package manager (like Cargo)
- [ ] Add optimizer (constant folding, dead code elim)
- [ ] Compile to `.dll` or `.so`
- [ ] Blitz Playground (web interface)
- [ ] Blitz IDE (VS Code extension)

---

## 🧩 Stretch Goals

- [ ] BlitzScript (Blitz with runtime for scripting)
- [ ] BlitzOS (an OS kernel written in Blitz)
- [ ] BlitzVM (write a VM backend)
- [ ] Self-hosting compiler in Blitz
