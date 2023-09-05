.globl _main
.p2align 2
mov w8, #10
str w8, [sp, #0]
_main:
sub sp, sp, #16
mov w8, #10
str w8, [sp, #0]
ldr w8, [sp, #0]
mov w9, w8
ldr w8, [sp, #0]
sub w8, w9, w8
mov w0, w8
add sp, sp, #16
ret