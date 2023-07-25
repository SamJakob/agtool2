# Build documentation (and open browser)
docs:
	make docs\:silent
	python -c "import os; import webbrowser; webbrowser.open('file://' + os.path.realpath('./docs/index.html'))"

# Build documentation without opening browser.
docs\:silent:
	rm -rf docs/
	pdoc --search --logo-link https://github.com/SamJakob/agtool2                               \
	--logo https://raw.githubusercontent.com/SamJakob/agtool2/master/docs-gen/logo.svg          \
	 -t ./docs-gen/agtool-template --output-dir docs/ agtool plugins                            \
	 -e agtool=https://github.com/SamJakob/agtool2/blob/master/agtool/                          \
	 -e plugins=https://github.com/SamJakob/agtool2/blob/master/plugins/

# PHONY targets (always build - i.e., don't attempt to cache for these targets)
.PHONY: docs docs\:silent clean
