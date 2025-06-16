# Makefile for Bitbucket CLI

.PHONY: help install clean build upload

help:
	@echo "Available commands:"
	@echo "  install     Install the package"
	@echo "  clean       Clean build artifacts"
	@echo "  build       Build package"
	@echo "  upload      Upload to PyPI"

install:
	pip install -e .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

upload: build
	pip install twine
	twine upload dist/*
