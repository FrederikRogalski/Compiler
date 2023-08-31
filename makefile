# out dir
tmp = out/

${tmp}hello: ${tmp}hello.o
	ld -o ${tmp}hello ${tmp}hello.o -lSystem -syslibroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk

${tmp}hello.o: ${tmp}hello.s
	as -o ${tmp}hello.o ${tmp}hello.s

${tmp}hello.s: hello.c
	clang -arch arm64 -S -Wall -o ${tmp}hello.s hello.c