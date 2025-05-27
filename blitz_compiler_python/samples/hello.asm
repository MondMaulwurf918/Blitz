; Blitz compiler output
bits 64
default rel

section .text
global main
extern ExitProcess

main:
    push rbp
    mov rbp, rsp
    sub rsp, 0
    mov rax, 42
    ; Windows: Call ExitProcess with return value
    mov rcx, rax  ; First argument to ExitProcess
    sub rsp, 32    ; Shadow space for Win64 calling convention
    call ExitProcess