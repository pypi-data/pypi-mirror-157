.DEFAULT_GOAL := help
.PHONY: coverage deps format lint publish push test tox help

coverage:  ## Run tests with coverage
	python -m coverage erase
	python -m coverage run --include=calculator/* -m pytest -ra --doctest-modules --doctest-continue-on-failure
	python -m coverage report -m

deps:  ## Install dependencies
	python -m pip install --upgrade pip
	python -m pip install black coverage flake8 flit pyflakes mccabe mypy pylint hypothesis pytest tox tox-gh-actions

format: ## Format code
    python -m black calculator
    python -m black test

lint:  ## Lint and static-check
	python -m flake8 calculator
	python -m pyflakes calculator
	python -m mypy calculator
	python -m pylint calculator

publish:  ## Publish to PyPi
	python -m flit publish

push:  ## Push code with tags
	git push && git push --tags

test:  ## Run tests
	python -m pytest -ra --doctest-modules --doctest-continue-on-failure

tox:   ## Run tox
	python -m tox

help: ## Show help message
	@IFS=$$'\n' ; \
	help_lines=(`fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##/:/'`); \
	printf "%s\n\n" "Usage: make [task]"; \
	printf "%-20s %s\n" "task" "help" ; \
	printf "%-20s %s\n" "------" "----" ; \
	for help_line in $${help_lines[@]}; do \
		IFS=$$':' ; \
		help_split=($$help_line) ; \
		help_command=`echo $${help_split[0]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		help_info=`echo $${help_split[2]} | sed -e 's/^ *//' -e 's/ *$$//'` ; \
		printf '\033[36m'; \
		printf "%-20s %s" $$help_command ; \
		printf '\033[0m'; \
		printf "%s\n" $$help_info; \
	done
