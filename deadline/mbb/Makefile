# Makefile for Moving Block Bootstrap C Library

# Variables
CC = gcc
CFLAGS = -shared -fPIC -O2 -Wall
LIBS = -lm
LIB_NAME = functions.so
SOURCE = functions_optimized.c

# Default target
all: $(LIB_NAME)

# Compile C library
$(LIB_NAME): $(SOURCE)
	@echo "Compiling MBB C library..."
	$(CC) $(CFLAGS) -o $@ $< $(LIBS)
	@echo "C library compiled successfully: $(LIB_NAME)"

# Clean build artifacts
clean:
	@echo "Cleaning MBB build artifacts..."
	rm -f $(LIB_NAME)
	@echo "Cleaned"

# Test compilation
test:
	@echo "Testing C library compilation..."
	$(CC) -Wall -Wextra -o test_mbb $(SOURCE) $(LIBS) -DTEST_BUILD
	./test_mbb
	rm -f test_mbb

.PHONY: all clean test

