.PHONY: install test

install: 
	python setup.py develop
	python setup.py bdist_egg --dist-dir ~/bin/pypes/plugins/
	pyenv rehash

.git/hooks/pre-commit: pre-commit
	chmod +x pre-commit
	ln -s pre-commit .git/hooks/pre-commit

tests: 
	cd test; py.test

clean:
	rm -rf build dist
