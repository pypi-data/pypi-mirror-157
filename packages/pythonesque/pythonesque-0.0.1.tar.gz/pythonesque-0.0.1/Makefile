.PHONY: test pdoc pdoc_live

test:
	# run tests
	python -m pytest

# docstring:
# 	pyment -w -o numpydoc series.py 

pdoc:
	# pdoc to reads docstrings, generates html
	pdoc --force --html pythonesque/ --output-dir docs

	# keep README.md in sync with docstring in pythonesque/__init__.py
	python -c 'import pythonesque; print(pythonesque.__doc__, file=open("README.md","w"))'

pdoc_live:
	# pdoc server to see live update to docs
	pdoc --http localhost:8080 pythonesque
