# Build documentation (and open browser)
docs:
	make docs\:silent
	python -c "import os; import webbrowser; webbrowser.open('file://' + os.path.realpath('./docs/agtool/index.html'))"

# Build documentation without opening browser.
docs\:silent:
	rm -rf docs/
	pdoc --html --output-dir docs/ agtool
	echo "<meta http-equiv=\"refresh\" content=\"0; url=https://nbtx-2.gitbook.io/agtool/\" /><script>window.location.href='https://nbtx-2.gitbook.io/agtool/';</script>" > docs/index.html

# PHONY targets (always build - i.e., don't attempt to cache for these targets)
.PHONY: docs docs\:silent clean
