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

section .text  ; Back to text section

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov rax, 10
    mov dword [rbp-4], eax
    mov rax, 5
    mov dword [rbp-8], eax
    mov rax, 2
    push rax
    mov eax, dword [rbp-8]
    pop rcx
    imul rax, rcx
    push rax
    mov eax, dword [rbp-4]
    pop rcx
    add rax, rcx
    mov dword [rbp-12], eax
    mov eax, dword [rbp-12]
    mov dword [last_printed_value], eax  ; Store the integer value
    ; Convert integer to string
    mov rcx, 10                ; Base 10
    mov rbx, output_buffer     ; Use our output buffer
    add rbx, 30                ; Start at the end of buffer
    mov byte [rbx], 0          ; Null terminator
    dec rbx                    ; Move back one byte
    .int_to_str_loop:
    xor rdx, rdx               ; Clear rdx for division
    div rcx                    ; rax / 10, remainder in rdx
    add dl, '0'                ; Convert to ASCII
    mov [rbx], dl              ; Store digit
    dec rbx                    ; Move back one byte
    test rax, rax              ; Check if done
    jnz .int_to_str_loop       ; Continue if not zero
    inc rbx                    ; Point to first digit
    ; Print the integer to the console using Windows API
    mov rcx, STD_OUTPUT_HANDLE ; First argument: handle type (stdout)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call GetStdHandle         ; Get handle to stdout
    add rsp, 32               ; Restore stack
    mov rsi, rax              ; Store handle in rsi
    mov rdi, rbx              ; String to print
    mov rcx, output_buffer
    add rcx, 30               ; End of buffer
    sub rcx, rdi              ; Calculate length
    mov r8, rcx               ; Store length in r8 for WriteConsoleA
    mov rcx, rsi              ; First argument: handle to stdout
    mov rdx, rdi              ; Second argument: string to print
    ; r8 already contains the string length
    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written
    push 0                    ; Fifth argument: reserved (NULL)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call WriteConsoleA        ; Call WriteConsoleA
    add rsp, 40               ; Restore stack (32 + 8 for the push)
    ; Print a newline
    mov rcx, rsi              ; First argument: handle to stdout
    mov rdx, newline          ; Second argument: newline string
    mov r8, 2                 ; Third argument: string length (CR+LF = 2 bytes)
    lea r9, [chars_written]   ; Fourth argument: pointer to chars_written
    push 0                    ; Fifth argument: reserved (NULL)
    sub rsp, 32               ; Shadow space for Win64 calling convention
    call WriteConsoleA        ; Call WriteConsoleA
    add rsp, 40               ; Restore stack (32 + 8 for the push)
    mov eax, dword [last_printed_value]  ; Return the value
    ; Expression result discarded
    mov eax, dword [rbp-12]
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