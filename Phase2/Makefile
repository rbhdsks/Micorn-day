PYTHON ?= python3
YOSYS ?= yosys
OCTAVE ?= octave-cli
.PHONY: all test rtl-test unit-test independent benchmark benchmark-synthetic synth audit figures reference
all: test
test: unit-test rtl-test
unit-test:
	PYTHONPATH=level1 $(PYTHON) -m unittest discover -s level1/tests -v
	PYTHONPATH=level5/scripts $(PYTHON) -m unittest discover -s level5/tests -v
rtl-test:
	$(PYTHON) level4/run_verification.py
independent:
	$(PYTHON) level4/lint/run_checks.py
benchmark:
	$(PYTHON) level5/scripts/run_benchmarks.py --download-corpus
benchmark-synthetic:
	$(PYTHON) level5/scripts/run_benchmarks.py --no-corpus --output build/synthetic_benchmarks
synth:
	$(PYTHON) level4/synth/run_synthesis.py --yosys '$(YOSYS)'
audit:
	$(PYTHON) audit/recompute_results.py
figures:
	$(PYTHON) analysis/prepare_data.py
	$(OCTAVE) --quiet --eval "addpath('matlab'); generate_deep_analysis;"
reference:
	$(PYTHON) tools/export_evidence.py
