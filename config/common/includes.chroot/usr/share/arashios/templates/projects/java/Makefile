JAVAC ?= javac
JAVA ?= java
SRC := src/main/java/App.java
OUT := build/classes

.PHONY: help test build run clean

help:
	@printf 'ArashiOS proyek Java @NAME@\n'
	@printf 'make test    kompilasi dan jalankan\n'

build:
	@mkdir -p $(OUT)
	$(JAVAC) -d $(OUT) $(SRC)

test: build
	$(JAVA) -cp $(OUT) App

run: test

clean:
	rm -rf build
