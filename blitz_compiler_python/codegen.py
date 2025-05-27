"""
Code Generator for the Blitz programming language.
Converts AST into x86_64 assembly code.
"""

import os

from parser import (
    ASTNode, ProgramNode, FunctionNode, ReturnNode, 
    NumberNode, StringNode, BinaryOpNode, VariableNode, DeclarationNode, CallNode
)
from lexer import TokenType
import os

class CodeGenError(Exception):
    """Exception raised for errors during code generation."""
    pass

class CodeGen:
    def __init__(self, ast: ProgramNode):
        self.ast = ast
        self.output = []
        self.current_function = None
        self.local_vars = {}
        self.stack_offset = 0
        self.string_literals = {}
        self.string_literal_count = 0
    
    def generate(self) -> str:
        """Generate assembly code from the AST."""
        self._emit_header()
        
        # Generate code for each function
        for function in self.ast.functions:
            self._generate_function(function)
        
        # Generate helper functions
        self._generate_helper_functions()
        
        return "\n".join(self.output)
    
    def _emit(self, line: str):
        """Add a line to the output."""
        self.output.append(line)
    
    def _emit_header(self):
        """Emit assembly header."""
        self._emit("; Blitz compiler output")
        self._emit("bits 64")
        self._emit("default rel")
        self._emit("")
        
        # Check if we're on Windows
        is_windows = os.name == 'nt'
        
        if is_windows:
            # Windows-specific header
            self._emit("section .text")
            
            # Check if we have a main function to set as the entry point
            has_main = any(func.name == "main" for func in self.ast.functions)
            if has_main:
                self._emit("global main")
                self._emit("extern GetStdHandle   ; Windows API function")
                self._emit("extern WriteConsoleA   ; Windows API function")
                self._emit("extern ExitProcess     ; Windows API function")
                
                # Add data section for string constants
                self._emit("")
                self._emit("section .data")
                self._emit("    last_printed_value dd 0  ; Store the last printed value here")
                self._emit("    digit_buffer db '0123456789', 0  ; Buffer for converting digits")
                self._emit("    output_buffer times 256 db 0  ; Buffer for output")
                self._emit("    newline db 13, 10  ; CRLF newline for Windows")
                self._emit("    STD_OUTPUT_HANDLE equ -11  ; Windows constant for stdout")
                self._emit("    chars_written dq 0        ; Used by WriteConsoleA")
                
                # Process the AST to find all string literals
                self._collect_string_literals(self.ast)
                
                # Emit string literals
                for string_id, string_value in self.string_literals.items():
                    escaped_value = string_value.replace('\\', '\\\\').replace('"', '\\"')
                    self._emit(f"    {string_id} db \"{escaped_value}\", 0  ; String literal")
                
                self._emit("")
                self._emit("section .text  ; Back to text section")
            else:
                self._emit("; Warning: No main function found")
        else:
            # Linux-specific header
            self._emit("section .text")
            
            # Check if we have a main function to set as the entry point
            has_main = any(func.name == "main" for func in self.ast.functions)
            if has_main:
                self._emit("global main")
            else:
                self._emit("; Warning: No main function found")
    
    def _generate_function(self, function: FunctionNode):
        """Generate code for a function."""
        self.current_function = function.name
        self.local_vars = {}
        self.stack_offset = 0
        
        # Function label
        self._emit("")
        self._emit(f"{function.name}:")
        
        # Function prologue
        self._emit("    push rbp")
        self._emit("    mov rbp, rsp")
        
        # Reserve stack space for local variables (will be adjusted later)
        self._emit("    sub rsp, 0")  # Placeholder
        
        # Generate code for function body
        for statement in function.body:
            self._generate_statement(statement)
        
        # Function epilogue (if not already returned)
        if not function.body or not isinstance(function.body[-1], ReturnNode):
            if function.name == "main":
                self._emit("    mov rax, 0")  # Default return 0 for main
            self._emit("    leave")
            self._emit("    ret")
        
        # Update stack space reservation if needed
        if self.stack_offset > 0:
            # Find the placeholder and replace it
            for i, line in enumerate(self.output):
                if line == "    sub rsp, 0":  # Our placeholder
                    # Align stack to 16 bytes
                    aligned_offset = (self.stack_offset + 15) & ~15
                    self.output[i] = f"    sub rsp, {aligned_offset}"
                    break
    
    def _generate_statement(self, statement: ASTNode):
        """Generate code for a statement."""
        if isinstance(statement, ReturnNode):
            self._generate_return(statement)
        elif isinstance(statement, DeclarationNode):
            self._generate_declaration(statement)
        else:
            # Expression statement
            self._generate_expression(statement)
            # Discard the result
            self._emit("    ; Expression result discarded")
    
    def _generate_return(self, return_node: ReturnNode):
        """Generate code for a return statement."""
        # Generate the return expression
        self._generate_expression(return_node.expression)
        
        # Check if we're on Windows and in the main function
        is_windows = os.name == 'nt'
        if is_windows and self.current_function == "main":
            # On Windows, we'll just return normally from main
            # The linker will handle the exit process
            self._emit("    ; Windows: Return from main")
            self._emit("    leave")
            self._emit("    ret")
        else:
            # Standard return
            self._emit("    leave")
            self._emit("    ret")
    
    def _generate_declaration(self, decl_node: DeclarationNode):
        """Generate code for a variable declaration."""
        # Allocate space on the stack
        var_size = 8  # Default to 64-bit (8 bytes)
        if decl_node.type == "i32":
            var_size = 4
        
        # Align to proper boundary
        self.stack_offset += var_size
        
        # Store variable location
        self.local_vars[decl_node.name] = {
            "offset": -self.stack_offset,
            "size": var_size
        }
        
        # Generate initializer if present
        if decl_node.initializer:
            self._generate_expression(decl_node.initializer)
            
            # Store the result in the variable
            if var_size == 4:
                self._emit(f"    mov dword [rbp-{self.stack_offset}], eax")
            else:
                self._emit(f"    mov qword [rbp-{self.stack_offset}], rax")
    
    def _collect_string_literals(self, node):
        """Recursively collect string literals from the AST."""
        if isinstance(node, StringNode):
            # Add string literal to the collection if not already present
            if node.value not in self.string_literals.values():
                string_id = f"str_{self.string_literal_count}"
                self.string_literals[string_id] = node.value
                self.string_literal_count += 1
        
        # Recursively process child nodes
        if isinstance(node, ProgramNode):
            for func in node.functions:
                self._collect_string_literals(func)
        elif isinstance(node, FunctionNode):
            for stmt in node.body:
                self._collect_string_literals(stmt)
        elif isinstance(node, ReturnNode):
            self._collect_string_literals(node.expression)
        elif isinstance(node, DeclarationNode) and node.initializer:
            self._collect_string_literals(node.initializer)
        elif isinstance(node, BinaryOpNode):
            self._collect_string_literals(node.left)
            self._collect_string_literals(node.right)
        elif isinstance(node, CallNode):
            for arg in node.arguments:
                self._collect_string_literals(arg)
    
    def _get_string_id(self, string_value):
        """Get the ID for a string literal."""
        for string_id, value in self.string_literals.items():
            if value == string_value:
                return string_id
        return None
    
    def _generate_expression(self, expr: ASTNode):
        """Generate code for an expression."""
        if isinstance(expr, NumberNode):
            self._emit(f"    mov rax, {expr.value}")
        
        elif isinstance(expr, StringNode):
            # Get the ID for this string literal
            string_id = self._get_string_id(expr.value)
            if string_id:
                # Load the address of the string into rax
                self._emit(f"    mov rax, {string_id}  ; Load address of string literal")
            else:
                raise CodeGenError(f"String literal not found: '{expr.value}'")
        
        elif isinstance(expr, VariableNode):
            if expr.name not in self.local_vars:
                raise CodeGenError(f"Undefined variable '{expr.name}'")
            
            var_info = self.local_vars[expr.name]
            if var_info["size"] == 4:
                self._emit(f"    mov eax, dword [rbp{var_info['offset']}]")
            else:
                self._emit(f"    mov rax, qword [rbp{var_info['offset']}]")
        
        elif isinstance(expr, CallNode):
            # Handle function calls
            if expr.callee == "printnl":
                # Special case for printnl function
                self._generate_printnl(expr.arguments)
            else:
                raise CodeGenError(f"Unknown function: {expr.callee}")
        
        elif isinstance(expr, BinaryOpNode):
            # Check for string concatenation
            if expr.operator == TokenType.PLUS and (isinstance(expr.left, StringNode) or isinstance(expr.right, StringNode)):
                self._generate_string_concat(expr)
            else:
                # Regular numeric operation
                # Generate right operand first (to handle nested expressions correctly)
                self._generate_expression(expr.right)
                self._emit("    push rax")  # Save right operand
                
                # Generate left operand
                self._generate_expression(expr.left)
                
                # Right operand is on the stack
                self._emit("    pop rcx")  # Get right operand
                
                # Perform operation
                if expr.operator == TokenType.PLUS:
                    self._emit("    add rax, rcx")
                elif expr.operator == TokenType.MINUS:
                    self._emit("    sub rax, rcx")
                elif expr.operator == TokenType.STAR:
                    self._emit("    imul rax, rcx")
                elif expr.operator == TokenType.SLASH:
                    self._emit("    cqo")  # Sign-extend rax into rdx:rax
                    self._emit("    idiv rcx")  # Divide rdx:rax by rcx, result in rax
                else:
                    raise CodeGenError(f"Unsupported binary operator: {expr.operator}")
        
        else:
            raise CodeGenError(f"Unsupported expression type: {type(expr)}")
            
    # Counter for generating unique labels
    _label_counter = 0
    
    def _generate_unique_label(self, base_name):
        """Generate a unique label name."""
        label = f"{base_name}_{self._label_counter}"
        self._label_counter += 1
        return label
    
    def _generate_string_concat(self, expr: BinaryOpNode):
        """Generate code for string concatenation."""
        # For simplicity, we'll just store the concatenated string in the output buffer
        self._emit("    ; String concatenation")
        self._emit("    mov rdi, output_buffer  ; Destination buffer")
        
        # Generate left operand (could be string or number)
        self._generate_expression(expr.left)
        
        # If left operand is a string, copy it to the output buffer
        if isinstance(expr.left, StringNode):
            self._emit("    mov rsi, rax         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
            self._emit("    add rdi, rax         ; Move buffer pointer")
        elif isinstance(expr.left, VariableNode):
            # Handle variable - need to check if it's a number or string
            # For now, we'll assume it's a number and convert it to string
            num_loop_label = self._generate_unique_label("num_to_str_loop")
            
            # Save the current value (which is in rax) to a temporary register
            self._emit("    mov r10, rax         ; Save variable value temporarily")
            
            self._emit("    push rdi             ; Save buffer pointer")
            self._emit("    mov rcx, 10          ; Base 10")
            self._emit("    mov rbx, digit_buffer ; Use digit buffer")
            self._emit("    add rbx, 10          ; Start at end of buffer")
            self._emit("    mov byte [rbx], 0    ; Null terminator")
            
            # Division loop to convert number to string
            self._emit(f"    {num_loop_label}:")
            self._emit("    xor rdx, rdx         ; Clear rdx for division")
            self._emit("    div rcx              ; rax / 10, remainder in rdx")
            self._emit("    add dl, '0'          ; Convert to ASCII")
            self._emit("    dec rbx              ; Move back one byte")
            self._emit("    mov [rbx], dl        ; Store digit")
            self._emit("    test rax, rax        ; Check if done")
            self._emit(f"    jnz {num_loop_label} ; Continue if not zero")
            
            # Copy the number string to the output buffer
            self._emit("    pop rdi              ; Restore buffer pointer")
            self._emit("    mov rsi, rbx         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
            self._emit("    add rdi, rax         ; Move buffer pointer")
            
            # Restore the original value
            self._emit("    mov rax, r10         ; Restore original value")
        else:
            # If left operand is a number, convert it to string
            num_loop_label = self._generate_unique_label("num_to_str_loop")
            
            self._emit("    push rdi             ; Save buffer pointer")
            self._emit("    mov rcx, 10          ; Base 10")
            self._emit("    mov rbx, digit_buffer ; Use digit buffer")
            self._emit("    add rbx, 10          ; Start at end of buffer")
            self._emit("    mov byte [rbx], 0    ; Null terminator")
            
            # Division loop to convert number to string
            self._emit(f"    {num_loop_label}:")
            self._emit("    xor rdx, rdx         ; Clear rdx for division")
            self._emit("    div rcx              ; rax / 10, remainder in rdx")
            self._emit("    add dl, '0'          ; Convert to ASCII")
            self._emit("    dec rbx              ; Move back one byte")
            self._emit("    mov [rbx], dl        ; Store digit")
            self._emit("    test rax, rax        ; Check if done")
            self._emit(f"    jnz {num_loop_label} ; Continue if not zero")
            
            # Copy the number string to the output buffer
            self._emit("    pop rdi              ; Restore buffer pointer")
            self._emit("    mov rsi, rbx         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
            self._emit("    add rdi, rax         ; Move buffer pointer")
        
        # Generate right operand (could be string or number)
        self._generate_expression(expr.right)
        
        # If right operand is a string, copy it to the output buffer
        if isinstance(expr.right, StringNode):
            self._emit("    mov rsi, rax         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
        elif isinstance(expr.right, VariableNode):
            # Handle variable - need to check if it's a number or string
            # For now, we'll assume it's a number and convert it to string
            num_loop_label = self._generate_unique_label("num_to_str_loop")
            
            # Save the current value (which is in rax) to a temporary register
            self._emit("    mov r10, rax         ; Save variable value temporarily")
            
            self._emit("    push rdi             ; Save buffer pointer")
            self._emit("    mov rcx, 10          ; Base 10")
            self._emit("    mov rbx, digit_buffer ; Use digit buffer")
            self._emit("    add rbx, 10          ; Start at end of buffer")
            self._emit("    mov byte [rbx], 0    ; Null terminator")
            
            # Division loop to convert number to string
            self._emit(f"    {num_loop_label}:")
            self._emit("    xor rdx, rdx         ; Clear rdx for division")
            self._emit("    div rcx              ; rax / 10, remainder in rdx")
            self._emit("    add dl, '0'          ; Convert to ASCII")
            self._emit("    dec rbx              ; Move back one byte")
            self._emit("    mov [rbx], dl        ; Store digit")
            self._emit("    test rax, rax        ; Check if done")
            self._emit(f"    jnz {num_loop_label} ; Continue if not zero")
            
            # Copy the number string to the output buffer
            self._emit("    pop rdi              ; Restore buffer pointer")
            self._emit("    mov rsi, rbx         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
            
            # Restore the original value
            self._emit("    mov rax, r10         ; Restore original value")
        else:
            # If right operand is a number, convert it to string
            num_loop_label = self._generate_unique_label("num_to_str_loop")
            
            self._emit("    push rdi             ; Save buffer pointer")
            self._emit("    mov rcx, 10          ; Base 10")
            self._emit("    mov rbx, digit_buffer ; Use digit buffer")
            self._emit("    add rbx, 10          ; Start at end of buffer")
            self._emit("    mov byte [rbx], 0    ; Null terminator")
            
            # Division loop to convert number to string
            self._emit(f"    {num_loop_label}:")
            self._emit("    xor rdx, rdx         ; Clear rdx for division")
            self._emit("    div rcx              ; rax / 10, remainder in rdx")
            self._emit("    add dl, '0'          ; Convert to ASCII")
            self._emit("    dec rbx              ; Move back one byte")
            self._emit("    mov [rbx], dl        ; Store digit")
            self._emit("    test rax, rax        ; Check if done")
            self._emit(f"    jnz {num_loop_label} ; Continue if not zero")
            
            # Copy the number string to the output buffer
            self._emit("    pop rdi              ; Restore buffer pointer")
            self._emit("    mov rsi, rbx         ; Source string")
            self._emit("    call _string_copy    ; Copy string to buffer")
        
        # Return the address of the output buffer
        self._emit("    mov rax, output_buffer  ; Return address of output buffer")
        
        # Null-terminate the output buffer
        self._emit("    mov byte [rdi], 0      ; Null-terminate the output buffer")
    
    def _generate_printnl(self, arguments):
        """Generate code for printnl function."""
        if not arguments:
            raise CodeGenError("printnl requires at least one argument")
        
        # Check if we're on Windows
        is_windows = os.name == 'nt'
        
        # Generate code for the argument
        self._generate_expression(arguments[0])
        
        # Check if the argument is a string or a string concatenation
        if isinstance(arguments[0], StringNode) or (
            isinstance(arguments[0], BinaryOpNode) and 
            (isinstance(arguments[0].left, StringNode) or isinstance(arguments[0].right, StringNode))
        ):
            # For strings, we've already set up the output buffer in rax
            # Store 1 in the last_printed_value to indicate success
            self._emit("    mov dword [last_printed_value], 1  ; Store 1 to indicate success")
            
            # Save the string pointer (in rax)
            self._emit("    ; Save the string pointer")
            self._emit("    mov rsi, rax              ; Save string pointer in rsi")
            
            # Get stdout handle
            self._emit("    ; Get handle to stdout")
            self._emit("    mov rcx, STD_OUTPUT_HANDLE ; First argument: handle type (stdout)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call GetStdHandle         ; Get handle to stdout")
            self._emit("    add rsp, 32               ; Restore stack")
            
            # Store the handle for later use
            self._emit("    mov rbx, rax              ; Store handle in rbx")
            
            # Calculate string length (find null terminator)
            self._emit("    ; Calculate string length")
            self._emit("    mov rdi, rsi              ; String pointer")
            self._emit("    xor rcx, rcx              ; Counter = 0")
            self._emit("    .strlen_loop:")
            self._emit("    cmp byte [rdi+rcx], 0     ; Check for null terminator")
            self._emit("    je .strlen_done           ; If found, we're done")
            self._emit("    inc rcx                   ; Increment counter")
            self._emit("    jmp .strlen_loop          ; Continue loop")
            self._emit("    .strlen_done:")
            self._emit("    mov r8, rcx               ; Store length in r8 for WriteConsoleA")
            
            # Call WriteConsoleA to print the string
            self._emit("    ; Print the string")
            self._emit("    mov rcx, rbx              ; First argument: handle to stdout")
            self._emit("    mov rdx, rsi              ; Second argument: string to print")
            self._emit("    ; r8 already contains the string length")
            self._emit("    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written")
            self._emit("    push 0                    ; Fifth argument: reserved (NULL)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call WriteConsoleA        ; Call WriteConsoleA")
            self._emit("    add rsp, 40               ; Restore stack (32 + 8 for the push)")
            
            # Print a newline
            self._emit("    ; Print a newline")
            self._emit("    mov rcx, rbx              ; First argument: handle to stdout")
            self._emit("    mov rdx, newline          ; Second argument: newline string")
            self._emit("    mov r8, 2                 ; Third argument: string length (CR+LF = 2 bytes)")
            self._emit("    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written")
            self._emit("    push 0                    ; Fifth argument: reserved (NULL)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call WriteConsoleA        ; Call WriteConsoleA")
            self._emit("    add rsp, 40               ; Restore stack (32 + 8 for the push)")
            
            # Restore rax to the original string pointer
            self._emit("    mov rax, rsi              ; Restore string pointer to rax")
        else:
            # For numbers, store the value in the global variable for inspection
            self._emit("    mov dword [last_printed_value], eax  ; Store the integer value")
            
            # Convert the integer to a string
            self._emit("    ; Convert integer to string")
            self._emit("    mov rcx, 10                ; Base 10")
            self._emit("    mov rbx, output_buffer     ; Use our output buffer")
            self._emit("    add rbx, 30                ; Start at the end of buffer")
            self._emit("    mov byte [rbx], 0          ; Null terminator")
            self._emit("    dec rbx                    ; Move back one byte")
            
            # Division loop to convert number to string
            self._emit("    .int_to_str_loop:")
            self._emit("    xor rdx, rdx               ; Clear rdx for division")
            self._emit("    div rcx                    ; rax / 10, remainder in rdx")
            self._emit("    add dl, '0'                ; Convert to ASCII")
            self._emit("    mov [rbx], dl              ; Store digit")
            self._emit("    dec rbx                    ; Move back one byte")
            self._emit("    test rax, rax              ; Check if done")
            self._emit("    jnz .int_to_str_loop       ; Continue if not zero")
            
            # Calculate string pointer and length
            self._emit("    inc rbx                    ; Point to first digit")
            
            # Get stdout handle
            self._emit("    ; Print the integer to the console using Windows API")
            self._emit("    mov rcx, STD_OUTPUT_HANDLE ; First argument: handle type (stdout)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call GetStdHandle         ; Get handle to stdout")
            self._emit("    add rsp, 32               ; Restore stack")
            
            # Store the handle for later use
            self._emit("    mov rsi, rax              ; Store handle in rsi")
            
            # Calculate string length
            self._emit("    mov rdi, rbx              ; String to print")
            self._emit("    mov rcx, output_buffer")
            self._emit("    add rcx, 30               ; End of buffer")
            self._emit("    sub rcx, rdi              ; Calculate length")
            self._emit("    mov r8, rcx               ; Store length in r8 for WriteConsoleA")
            
            # Call WriteConsoleA to print the string
            self._emit("    mov rcx, rsi              ; First argument: handle to stdout")
            self._emit("    mov rdx, rdi              ; Second argument: string to print")
            self._emit("    ; r8 already contains the string length")
            self._emit("    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written")
            self._emit("    push 0                    ; Fifth argument: reserved (NULL)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call WriteConsoleA        ; Call WriteConsoleA")
            self._emit("    add rsp, 40               ; Restore stack (32 + 8 for the push)")
            
            # Print a newline
            self._emit("    ; Print a newline")
            self._emit("    mov rcx, rsi              ; First argument: handle to stdout")
            self._emit("    mov rdx, newline          ; Second argument: newline string")
            self._emit("    mov r8, 2                 ; Third argument: string length (CR+LF = 2 bytes)")
            self._emit("    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written")
            self._emit("    push 0                    ; Fifth argument: reserved (NULL)")
            self._emit("    sub rsp, 32               ; Shadow space for Win64 calling convention")
            self._emit("    call WriteConsoleA        ; Call WriteConsoleA")
            self._emit("    add rsp, 40               ; Restore stack (32 + 8 for the push)")
        
        # Return the value in rax
        self._emit("    mov eax, dword [last_printed_value]  ; Return the value")
    
    def _generate_helper_functions(self):
        """Generate helper functions used by the generated code."""
        # String copy function
        self._emit("")
        self._emit("; Helper function to copy a string")
        self._emit("_string_copy:")
        self._emit("    xor rcx, rcx         ; Clear counter")
        self._emit("    .copy_loop:")
        self._emit("    mov al, [rsi+rcx]    ; Load byte from source")
        self._emit("    mov [rdi+rcx], al    ; Store byte to destination")
        self._emit("    inc rcx              ; Increment counter")
        self._emit("    test al, al          ; Check for null terminator")
        self._emit("    jnz .copy_loop       ; Continue if not null")
        self._emit("    dec rcx              ; Don't count null terminator")
        self._emit("    mov rax, rcx         ; Return length")
        self._emit("    ret")
    
    def _peek_value_if_constant(self, expr: ASTNode) -> str:
        """Try to peek at the value of an expression if it's a constant."""
        if isinstance(expr, NumberNode):
            return str(expr.value)
        elif isinstance(expr, VariableNode) and expr.name in self.local_vars:
            return f"<variable {expr.name}>"
        else:
            return "<computed value>"
    
    def _syscall_exit(self, code: int):
        """Generate code for exit syscall."""
        self._emit(f"    mov rax, 60")  # syscall number for exit
        self._emit(f"    mov rdi, {code}")  # exit code
        self._emit(f"    syscall")