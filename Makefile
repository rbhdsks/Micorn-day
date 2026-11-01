.PHONY: all test level1-test tooling-test rtl-test benchmark synth clean help reference check
all test level1-test tooling-test rtl-test benchmark synth clean help reference check:
	$(MAKE) -C Phase1 $@
