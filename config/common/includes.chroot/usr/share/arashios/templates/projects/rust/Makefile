.PHONY: help test lint format run clean

help:
	@printf 'ArashiOS proyek Rust @NAME@\n'
	@printf 'make test    jalankan uji\n'
	@printf 'make lint    jalankan clippy\n'

test:
	cargo test

lint:
	cargo clippy -- -D warnings

format:
	cargo fmt

run:
	cargo run

clean:
	cargo clean
