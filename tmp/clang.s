	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_main                           ; -- Begin function main
	.p2align	2
_main:                                  ; @main
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #16
	.cfi_def_cfa_offset 16
	str	wzr, [sp, #12]
	mov	w8, #10
	str	w8, [sp, #8]
	ldr	w8, [sp, #8]
	adrp	x9, _b@PAGE
	ldr	w9, [x9, _b@PAGEOFF]
	subs	w0, w8, w9
	add	sp, sp, #16
	ret
	.cfi_endproc
                                        ; -- End function
	.globl	_test                           ; -- Begin function test
	.p2align	2
_test:                                  ; @test
	.cfi_startproc
; %bb.0:
	mov	w0, #0
	ret
	.cfi_endproc
                                        ; -- End function
	.section	__DATA,__data
	.globl	_b                              ; @b
	.p2align	2
_b:
	.long	10                              ; 0xa

.subsections_via_symbols
