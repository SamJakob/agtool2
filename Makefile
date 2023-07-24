# Build documentation (and open browser)
docs:
	make docs\:silent
	python -c "import os; import webbrowser; webbrowser.open('file://' + os.path.realpath('./docs/app/index.html'))"

# Build documentation without opening browser.
docs\:silent:
	rm -rf docs/
	pdoc --html --output-dir docs/ app

# PHONY targets (always build - i.e., don't attempt to cache for these targets)
.PHONY: docs docs\:silent clean
