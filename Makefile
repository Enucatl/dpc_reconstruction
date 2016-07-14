.PHONY: all install test
TF_INC := $(shell python -c 'import tensorflow as tf; print(tf.sysconfig.get_include())')

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

src/arg.so: src/arg.cc
	g++ -std=c++11 -shared $< -o $@ -fPIC -I ${TF_INC}

tests: 
	cd test; py.test

clean:
	rm -rf build dist
