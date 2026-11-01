.PHONY: all test level2-test level3-test research-test notebooks figures level1-test tooling-test rtl-test benchmark synth clean help reference check
all test level2-test level3-test research-test notebooks figures level1-test tooling-test rtl-test benchmark synth clean help reference check:
	$(MAKE) -C Phase1 $@
