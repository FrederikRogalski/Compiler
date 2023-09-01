	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_main                           ; -- Begin function main
	.p2align	2
_main:                                  ; @main
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #16
	.cfi_def_cfa_offset 16
	mov	w0, #0
	str	wzr, [sp, #12]
	add	sp, sp, #16
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_func1                          ; -- Begin function func1
	.p2align	2
_func1:                                 ; @func1
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #32
	.cfi_def_cfa_offset 32
	mov	w8, #1
	str	w8, [sp, #28]
	ldr	w9, [sp, #28]
	add	w9, w9, #1
	str	w9, [sp, #28]
	str	w8, [sp, #24]
	str	w8, [sp, #20]
	mov	w8, #2
	str	w8, [sp, #16]
	str	w8, [sp, #12]
	mov	w0, #0
	add	sp, sp, #32
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_func2                          ; -- Begin function func2
	.p2align	2
_func2:                                 ; @func2
	.cfi_startproc
; %bb.0:
	mov	w0, #0
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols
