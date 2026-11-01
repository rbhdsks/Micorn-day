PYTHON ?= python3
IVERILOG ?= iverilog
VVP ?= vvp
YOSYS ?= yosys
IVFLAGS ?=
export IVERILOG VVP IVFLAGS
RTL := $(wildcard level4/rtl/*.sv)
DRAM := level4/tb/dram_model.sv
BENCHES := tb_cache tb_stress tb_predictor tb_next_line tb_adversarial tb_nonpreemptible
COMPILED := $(addprefix build/verification/,$(addsuffix .vvp,$(BENCHES)))

.PHONY: all check test level1-test tooling-test rtl-test benchmark synth clean help reference
all: test benchmark
check: all

test: level1-test level2-test level3-test research-test tooling-test rtl-test
level1-test:
	PYTHONPATH=level1 $(PYTHON) -m unittest discover -s level1/tests -v
tooling-test:
	$(PYTHON) -m unittest discover -s level5/tests -v

build/verification/%.vvp: level4/tb/%.sv $(RTL) $(DRAM)
	mkdir -p build/verification
	$(IVERILOG) $(IVFLAGS) -g2012 -Wall -s $* -o $@ $(RTL) $(DRAM) $<

rtl-test: $(COMPILED)
	$(PYTHON) tools/run_verification.py --vvp '$(VVP)' $(COMPILED)
	$(PYTHON) tools/trace_smoke.py

benchmark:
	$(PYTHON) level5/scripts/run_benchmarks.py --output build/benchmarks

synth:
	mkdir -p build/synthesis
	$(YOSYS) -l build/synthesis/stride.log -s level4/synth/synth.ys
	$(YOSYS) -l build/synthesis/next_line.log -s level4/synth/next_line.ys

reference:
	$(PYTHON) tools/export_reference.py

clean:
	$(PYTHON) -c "import shutil; shutil.rmtree('build', ignore_errors=True)"

help:
	@echo 'make all          Run Level 1/tooling/RTL tests and all three-policy benchmarks'
	@echo 'make test         Run all unit and RTL correctness tests'
	@echo 'make benchmark    Generate traces, replay RTL, and produce measured CSV/report'
	@echo 'make synth        Generic synthesis/check (YOSYS may override executable)'
	@echo 'make reference    Export compact verified benchmark evidence for Git'
	@echo 'make clean        Remove only generated Phase1/build outputs'

.PHONY: level2-test level3-test research-test notebooks figures
level2-test:
	PYTHONPATH=level2 $(PYTHON) -m unittest discover -s level2/tests -v
level3-test:
	PYTHONPATH=level3 $(PYTHON) -m unittest discover -s level3/tests -v
research-test:
	PYTHONPATH=research/cdm $(PYTHON) -m unittest discover -s research/cdm/tests -v
notebooks:
	$(PYTHON) tools/execute_notebooks.py
figures:
	$(PYTHON) research/cdm/cdm_reference.py
	$(PYTHON) level5/scripts/plot_results.py
