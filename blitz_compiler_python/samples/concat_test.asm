; Blitz compiler output
bits 64
default rel

section .text
global main
extern GetStdHandle   ; Windows API function
extern WriteConsoleA   ; Windows API function
extern ExitProcess     ; Windows API function

section .data
    last_printed_value dd 0  ; Store the last printed value here
    digit_buffer db '0123456789', 0  ; Buffer for converting digits
    output_buffer times 256 db 0  ; Buffer for output
    newline db 13, 10  ; CRLF newline for Windows
    STD_OUTPUT_HANDLE equ -11  ; Windows constant for stdout
    chars_written dq 0        ; Used by WriteConsoleA
    str_0 db "The answer is: ", 0  ; String literal

section .text  ; Back to text section

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rax, 42
    mov dword [rbp-4], eax
    ; String concatenation
    mov rdi, output_buffer  ; Destination buffer
    mov rax, str_0  ; Load address of string literal
    mov rsi, rax         ; Source string
    call _string_copy    ; Copy string to buffer
    add rdi, rax         ; Move buffer pointer
    mov eax, dword [rbp-4]
    mov r10, rax         ; Save variable value temporarily
    push rdi             ; Save buffer pointer
    mov rcx, 10          ; Base 10
    mov rbx, digit_buffer ; Use digit buffer
    add rbx, 10          ; Start at end of buffer
    mov byte [rbx], 0    ; Null terminator
    num_to_str_loop_0:
    xor rdx, rdx         ; Clear rdx for division
    div rcx              ; rax / 10, remainder in rdx
    add dl, '0'          ; Convert to ASCII
    dec rbx              ; Move back one byte
    mov [rbx], dl        ; Store digit
    test rax, rax        ; Check if done
    jnz num_to_str_loop_0 ; Continue if not zero
    pop rdi              ; Restore buffer pointer
    mov rsi, rbx         ; Source string
    call _string_copy    ; Copy string to buffer
    mov rax, r10         ; Restore original value
    mov rax, output_buffer  ; Return address of output buffer
    mov byte [rdi], 0      ; Null-terminate the output buffer
    mov dword [last_printed_value], 1  ; Store 1 to indicate success
    ; Save the string pointer
    mov rsi, rax              ; Save string pointer in rsi
    ; Get handle to stdout
    mov rcx, STD_OUTPUT_HANDLE ; First argument: handle type (stdout)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call GetStdHandle         ; Get handle to stdout
    add rsp, 32               ; Restore stack
    mov rbx, rax              ; Store handle in rbx
    ; Calculate string length
    mov rdi, rsi              ; String pointer
    xor rcx, rcx              ; Counter = 0
    .strlen_loop:
    cmp byte [rdi+rcx], 0     ; Check for null terminator
    je .strlen_done           ; If found, we're done
    inc rcx                   ; Increment counter
    jmp .strlen_loop          ; Continue loop
    .strlen_done:
    mov r8, rcx               ; Store length in r8 for WriteConsoleA
    ; Print the string
    mov rcx, rbx              ; First argument: handle to stdout
    mov rdx, rsi              ; Second argument: string to print
    ; r8 already contains the string length
    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written
    push 0                    ; Fifth argument: reserved (NULL)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call WriteConsoleA        ; Call WriteConsoleA
    add rsp, 40               ; Restore stack (32 + 8 for the push)
    ; Print a newline
    mov rcx, rbx              ; First argument: handle to stdout
    mov rdx, newline          ; Second argument: newline string
    mov r8, 2                 ; Third argument: string length (CR+LF = 2 bytes)
    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written
    push 0                    ; Fifth argument: reserved (NULL)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call WriteConsoleA        ; Call WriteConsoleA
    add rsp, 40               ; Restore stack (32 + 8 for the push)
    mov rax, rsi              ; Restore string pointer to rax
    mov eax, dword [last_printed_value]  ; Return the value
    ; Expression result discarded
    mov rax, 0
    ; Windows: Return from main
    leave
    ret

; Helper function to copy a string
_string_copy:
    xor rcx, rcx         ; Clear counter
    .copy_loop:
    mov al, [rsi+rcx]    ; Load byte from source
    mov [rdi+rcx], al    ; Store byte to destination
    inc rcx              ; Increment counter
    test al, al          ; Check for null terminator
    jnz .copy_loop       ; Continue if not null
    dec rcx              ; Don't count null terminator
    mov rax, rcx         ; Return length
    ret