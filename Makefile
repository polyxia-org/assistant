.PHONY: install-poetry modify-torch-line install-dependency

install-poetry:
    command -v poetry >/dev/null 2>&1 || (curl -sSL https://install.python-poetry.org | python3 -)

modify-torch-line:
	if [ `uname -m` = "aarch64" ]; then \
		sed -i 's/^torch =.*/torch = {file = "torch-1.13.0a0+git7c98e70-cp38-cp38-linux_aarch64.whl"}/' pyproject.toml
	fi

install-dependency:
	poetry install

install: install-poetry modify-torch-line install-dependency
