.PHONY: help test lint format run clean

help:
	@printf 'ArashiOS proyek Python @NAME@\n'
	@printf 'make test    jalankan uji\n'
	@printf 'make lint    cek gaya kode\n'
	@printf 'make run     jalankan CLI\n'

test:
	python3 -m pytest -q

lint:
	ruff check .

format:
	ruff format .

run:
	python3 -m @NAME@.main

clean:
	rm -rf .pytest_cache **/__pycache__
