.PHONY: help test build run clean

help:
	@printf 'ArashiOS proyek Go @NAME@\n'
	@printf 'make test    jalankan uji\n'
	@printf 'make build   bangun biner\n'

test:
	go test ./...

build:
	go build -trimpath -ldflags '-s -w' -o bin/@NAME@ .

run:
	go run .

clean:
	rm -rf bin
