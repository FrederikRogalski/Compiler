	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 13, 0	sdk_version 13, 3
	.globl	_main                           ; -- Begin function main
	.p2align	2
_main:                                  ; @main
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #48
	.cfi_def_cfa_offset 48
	str	wzr, [sp, #44]
	str	w0, [sp, #40]
	str	x1, [sp, #32]
	ldr	w8, [sp, #40]
	add	w8, w8, #10
	str	w8, [sp, #28]
	b	LBB0_1
LBB0_1:                                 ; =>This Inner Loop Header: Depth=1
	ldr	w8, [sp, #28]
	subs	w8, w8, #0
	cset	w8, le
	tbnz	w8, #0, LBB0_3
	b	LBB0_2
LBB0_2:                                 ;   in Loop: Header=BB0_1 Depth=1
	ldr	w8, [sp, #40]
	add	w8, w8, #20
	str	w8, [sp, #24]
	ldr	w8, [sp, #40]
	add	w8, w8, #20
	str	w8, [sp, #20]
	ldr	w8, [sp, #40]
	add	w8, w8, #20
	str	w8, [sp, #16]
	ldr	w8, [sp, #40]
	add	w8, w8, #20
	str	w8, [sp, #12]
	ldr	w8, [sp, #28]
	subs	w8, w8, #1
	str	w8, [sp, #28]
	ldr	w8, [sp, #24]
	subs	w8, w8, #1
	str	w8, [sp, #24]
	ldr	w8, [sp, #20]
	subs	w8, w8, #1
	str	w8, [sp, #20]
	ldr	w8, [sp, #16]
	subs	w8, w8, #1
	str	w8, [sp, #16]
	ldr	w8, [sp, #12]
	subs	w8, w8, #1
	str	w8, [sp, #12]
	b	LBB0_1
LBB0_3:
	ldr	w0, [sp, #28]
	add	sp, sp, #48
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols
