PANDOC ?= pandoc
TITLE ?= laporan
OUTDIR ?= build

.PHONY: help report html pdf clean

help:
	@printf 'ArashiOS template laporan @NAME@\n'
	@printf 'make report  bangun laporan\n'

html: report.md
	@mkdir -p $(OUTDIR)
	$(PANDOC) report.md -o $(OUTDIR)/$(TITLE).html --standalone --css style.css

pdf: report.md
	@mkdir -p $(OUTDIR)
	$(PANDOC) report.md -o $(OUTDIR)/$(TITLE).pdf --pdf-engine=wkhtmltopdf

report: html

clean:
	rm -rf $(OUTDIR)
