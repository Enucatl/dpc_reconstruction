.PHONY: all install test
TF_INC := $(shell python -c 'import tensorflow as tf; print(tf.sysconfig.get_include())')
NSYNC_INC := ${TF_INC}/external/nsync/public/
TF_LIB=$(shell python -c 'import tensorflow as tf; print(tf.sysconfig.get_lib())')
TF_PYTHON=${TF_LIB}/python

all: install .git/hooks/post-commit .git/hooks/pre-commit src/arg.so

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
	g++ -std=c++11 -shared ${TF_PYTHON}/_pywrap_tensorflow_internal.so $< -o $@ -fPIC -I ${TF_INC} -I ${NSYNC_INC} -L${TF_LIB} -ltensorflow_framework -D_GLIBCXX_USE_CXX11_ABI=0 

tests: 
	cd test; py.test

clean:
	rm -rf build dist src/arg.so
