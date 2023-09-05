# Define variables
tmp = tmp/
CC = clang
AS = as
LD = ld
PYTHON = python3
CCFLAGS = -O0 -arch arm64 -S -Wall
LDFLAGS = -lSystem -syslibroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk

# Default target
all: clang python

# Compile source.c to generate clang.s and python.s
${tmp}clang.s: source.c
	${CC} ${CCFLAGS} -o $@ $<

${tmp}python.s: source.c
	${PYTHON} -m ccompiler -v -o $@ $<

# Assemble .s files to generate .o files
${tmp}clang.o: ${tmp}clang.s
	${AS} -o $@ $<

${tmp}python.o: ${tmp}python.s
	${AS} -o $@ $<

# Link .o files to generate executables
clang: ${tmp}clang.o
	${LD} -o $@ $< ${LDFLAGS}

python: ${tmp}python.o
	${LD} -o $@ $< ${LDFLAGS}

# Clean up intermediate files
clean:
	rm -f ${tmp}clang ${tmp}python ${tmp}clang.o ${tmp}python.o ${tmp}clang.s ${tmp}python.s