PYTHON ?= python3
SYMBOL ?= aapl.us
START ?= 2024-01-01
END ?= 2024-01-31
OUTPUT_DIR ?= data
REPORT_DIR ?= reports

.PHONY: data validate

data:
	$(PYTHON) -m pipeline.fetch --symbol $(SYMBOL) --start $(START) --end $(END) --output-dir $(OUTPUT_DIR) --format csv

validate:
	$(PYTHON) -m pipeline.validate --input $(OUTPUT_DIR)/$(SYMBOL)_$(START)_$(END).csv --report-dir $(REPORT_DIR)
