.PHONY: all install test

all: install .git/hooks/post-commit .git/hooks/pre-commit

install: 
	python setup.py develop
	pyenv rehash

.git/hooks/post-commit: post-commit
	chmod +x post-commit
	ln -s ../../post-commit .git/hooks/post-commit

.git/hooks/pre-commit: pre-commit
	chmod +x pre-commit
	ln -s ../../pre-commit .git/hooks/pre-commit

tests: 
	cd test; py.test

clean:
	rm -rf build dist
