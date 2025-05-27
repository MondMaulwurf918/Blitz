# Blitz Standard Library

This document describes the standard library functions available in the Blitz programming language. The standard library is minimal by design, focusing on essential system operations.

## Current Implementation

In the MVP stage, the standard library is extremely minimal and primarily focused on program exit functionality.

### System Functions

#### Exit Code

The `main()` function's return value is used as the program's exit code. This is the primary way to communicate a program's success or failure to the operating system.

```blitz
fn main() -> i32 {
    return 0;  // Success
}
```

## Planned Standard Library Functions

The following functions are planned for future versions of the Blitz standard library:

### I/O Functions

```blitz
// Print an integer to stdout
fn print_i32(i32 value) -> i32

// Print a string to stdout
fn print_str(str value) -> i32

// Read an integer from stdin
fn read_i32() -> i32

// Read a line from stdin
fn read_line() -> str
```

### Memory Management

```blitz
// Allocate memory of specified size
fn malloc(i64 size) -> ptr

// Free previously allocated memory
fn free(ptr memory) -> i32
```

### File Operations

```blitz
// Open a file with specified mode
fn open(str path, i32 mode) -> i32

// Close a file descriptor
fn close(i32 fd) -> i32

// Read from a file descriptor into a buffer
fn read(i32 fd, ptr buffer, i64 length) -> i64

// Write from a buffer to a file descriptor
fn write(i32 fd, ptr buffer, i64 length) -> i64
```

### System Calls

```blitz
// Exit the program with specified code
fn exit(i32 code) -> void

// Get current timestamp
fn time() -> i64
```

## Implementation Details

The standard library functions will be implemented as thin wrappers around system calls on the target platform. This approach ensures minimal runtime overhead while providing essential functionality.

For the MVP, these functions will be implemented directly in the code generator as special cases, rather than as actual Blitz functions. In future versions, they may be implemented as a combination of built-in functions and a standard library written in Blitz itself.