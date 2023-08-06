.PHONY: test pdoc pdoc_live

test:
	# run tests
	python -m pytest

# docstring:
# 	pyment -w -o numpydoc series.py 

pdoc:
	# pdoc to reads docstrings, generates html to docs/
	pdoc --force --html --output-dir docs pythonesque

	# pdoc writes html to subdir of docs/
	# move htmls to docs/ so GitHub pages works correctly
	mv docs/pythonesque/*.html docs/
	rmdir docs/pythonesque/

	# keep README.md in sync with docstring in pythonesque/__init__.py
	python -c 'import pythonesque; print(pythonesque.__doc__, file=open("README.md","w"))'

pdoc_live:
	# pdoc server to see live update to docs
	pdoc --http localhost:8080 pythonesque
