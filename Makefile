.PHONY: install test

install: 
	chmod +x pre-commit
	ln -s pre-commit .git/hooks/pre-commit
	python setup.py develop
	python setup.py bdist_egg --dist-dir ~/bin/pypes/plugins/

test: 
	cd test; py.test

clean:
	rm -rf build dist
