# Getting Started with Blitz

This tutorial will guide you through writing your first Blitz program and using the Blitz compiler.

## Prerequisites

- Python 3.6 or higher
- NASM (Netwide Assembler)
- LD (GNU Linker)

On Linux, you can install these dependencies with:

```bash
sudo apt-get install python3 nasm binutils
```

On Windows, you'll need to install:
- Python from [python.org](https://www.python.org/downloads/)
- NASM from [nasm.us](https://www.nasm.us/)
- MinGW or similar for the linker

## Your First Blitz Program

Let's create a simple "Hello, World!" program in Blitz. Since the current MVP doesn't support string operations yet, we'll create a program that returns the number 42.

Create a file named `hello.blitz` with the following content:

```blitz
// My first Blitz program
fn main() -> i32 {
    return 42;
}
```

This program defines a `main` function that returns the integer value 42. In Blitz, the `main` function is the entry point of the program, and its return value becomes the exit code of the program.

## Compiling Your Program

To compile your Blitz program, use the `blitzc.py` compiler:

```bash
python blitzc.py hello.blitz
```

This will generate:
1. `hello.asm` - The assembly code
2. `hello.o` - The object file
3. `hello` - The executable file

## Running Your Program

After compilation, you can run your program:

```bash
./hello
```

To verify the exit code (which should be 42), you can use:

```bash
echo $?  # On Linux/macOS
```

Or:

```bash
echo %ERRORLEVEL%  # On Windows
```

## Using Variables and Arithmetic

Let's create a more complex program that uses variables and arithmetic operations. Create a file named `calc.blitz`:

```blitz
fn main() -> i32 {
    let i32 x = 10;
    let i32 y = 5;
    let i32 result = x + y * 2;
    return result;
}
```

This program:
1. Declares an integer variable `x` with value 10
2. Declares an integer variable `y` with value 5
3. Computes `x + (y * 2)` (which is 20) and stores it in `result`
4. Returns `result` as the exit code

Compile and run this program the same way as before:

```bash
python blitzc.py calc.blitz
./calc
echo $?  # Should output 20
```

## Compiler Options

The Blitz compiler supports several options:

- `-o, --output <file>`: Specify the output file name
- `-r, --run`: Run the program after compilation

For example:

```bash
python blitzc.py calc.blitz -o calculator -r
```

This compiles `calc.blitz` to an executable named `calculator` and runs it immediately.

## Next Steps

As you become more familiar with Blitz, you can explore:

1. Writing more complex arithmetic expressions
2. Creating multiple functions
3. Experimenting with different integer types (i32, i64)

Remember that Blitz is still in its MVP stage, so many features like strings, conditionals, and loops are planned for future versions.

## Troubleshooting

If you encounter issues:

1. Make sure NASM and LD are installed and in your PATH
2. Check for syntax errors in your Blitz code
3. Verify that the compiler can find your input file

For more information, refer to the [grammar documentation](grammar.md) and [standard library documentation](stdlib.md).