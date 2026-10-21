CC ?= cc
CFLAGS ?= -std=c11 -O2 -Wall -Wextra -Wpedantic
PREFIX ?= /usr/local
BIN := bin/@NAME@

.PHONY: help test build install clean

help:
	@printf 'ArashiOS proyek C @NAME@\n'
	@printf 'make test    jalankan uji\n'
	@printf 'make build   bangun biner\n'

build: $(BIN)

$(BIN): src/main.c include/@NAME@.h
	@mkdir -p bin
	$(CC) $(CFLAGS) -Iinclude -o $@ src/main.c

test: build
	./tests/smoke.sh

install: build
	install -Dm755 $(BIN) $(DESTDIR)$(PREFIX)/bin/@NAME@

clean:
	rm -rf bin
