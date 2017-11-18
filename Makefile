BROWSER ?= xdg-open
PYTHON_PACKAGE = midiscenemanager
TESTS_PACKAGE = tests

.PHONY: po mo clean clean-test clean-pyc clean-build docs help
.DEFAULT_GOAL := help

help:
	@echo "Available make targets:"
	@echo
	@echo "dist           builds source and wheel package"
	@echo "install        install the package to the active Python environment"
	@echo "docs           generate Sphinx HTML documentation, including API docs"
	@echo "apk            build an android apk with buildozer"
	@echo "deploy         deploy the app to your android device"
	@echo "po             create i18n message file"
	@echo "mo             create i18n locales files"
	@echo "test           run tests on every Python version with tox"
	@echo "flake8         run style checks and static analysis with flake8"
	@echo "pylint         run style checks and static analysis with pylint"
	@echo "docstrings     check docstring presence and style conventions with pydocstyle"
	@echo "coverage       check code coverage with the default Python version"
	@echo "metrics        print code metrics with radon"
	@echo "clean          remove all build, test, coverage and Python artifacts"
	@echo "clean-build    remove distutils build artifacts"
	@echo "clean-pyc      remove Python file artifacts"
	@echo "clean-test     remove testing and QA reposting artifacts"

test:
	python setup.py test

flake8: ## run style checks and static analysis with flake8
	flake8 $(PYTHON_PACKAGE) $(TESTS_PACKAGE)

docstrings: ## check docstring presence and style conventions with pydocstyle
	pydocstyle $(PYTHON_PACKAGE)

pylint: ## run style checks and static analysis with pylint
	@-mkdir -p reports/
	@-pylint -f html $(PYTHON_PACKAGE) $(TESTS_PACKAGE) > reports/pylint.html
	@$(BROWSER) reports/pylint.html
	pylint $(PYTHON_PACKAGE) $(TESTS_PACKAGE)

coverage: ## check code coverage quickly with the default Python
	@-mkdir -p reports/htmlcov
	coverage run --source $(PYTHON_PACKAGE) `which py.test`
	coverage report -m
	@coverage html -d reports/htmlcov
	@$(BROWSER) reports/htmlcov/index.html

metrics: ## print code metrics with radon
	radon raw -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)
	radon cc -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)
	radon mi -s $(PYTHON_PACKAGE) $(TEST_PACKAGE)

po:
	xgettext -Lpython --keyword=tr:1 --output=messages.pot midiscenemanager/*.kv
	msgmerge --update --no-fuzzy-matching --backup=off po/en.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/de.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/es.po messages.pot
	msgmerge --update --no-fuzzy-matching --backup=off po/fr.po messages.pot

mo:
	mkdir -p data/locales/en/LC_MESSAGES
	mkdir -p data/locales/de/LC_MESSAGES
	mkdir -p data/locales/es/LC_MESSAGES
	mkdir -p data/locales/fr/LC_MESSAGES
	msgfmt -c -o data/locales/en/LC_MESSAGES/midiscenemanager.mo po/en.po
	msgfmt -c -o data/locales/de/LC_MESSAGES/midiscenemanager.mo po/de.po
	msgfmt -c -o data/locales/es/LC_MESSAGES/midiscenemanager.mo po/es.po
	msgfmt -c -o data/locales/fr/LC_MESSAGES/midiscenemanager.mo po/fr.po

docs:
	mkdir -p docs/_static
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	$(BROWSER) docs/build/html/index.html

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

apk:
	buildozer -v android debug

deploy:
	buildozer android deploy logcat

## remove all docs, build, test, coverage and Python artifacts
clean: clean-build clean-docs clean-pyc clean-test

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-docs:
	$(MAKE) -C docs clean

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr reports/
