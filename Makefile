.PHONY: install-precise-engine install-poetry modify-torch-line install-dependency

IS_JETSON := $(shell if [ -f /etc/nv_tegra_release ]; then echo true; else echo false; fi)

install-precise-engine:
	if ! [ -d precise-engine ]; then \
		if [ $(IS_JETSON) = true ] || [ $(shell uname -o) = Darwin ]; then \
			wget https://github.com/MycroftAI/precise-data/raw/dist/aarch64/precise-engine_0.3.0_aarch64.tar.gz; \
			tar xvf precise-engine_0.3.0_aarch64.tar.gz -C packages/; \
			rm precise-engine_0.3.0_aarch64.tar.gz; \
		else \
			wget https://github.com/MycroftAI/mycroft-precise/releases/download/v0.3.0/precise-engine_0.3.0_x86_64.tar.gz; \
			tar xvf precise-engine_0.3.0_x86_64.tar.gz -C packages/; \
			rm precise-engine_0.3.0_x86_64.tar.gz; \
		fi \
	fi
	
install-poetry:
	if ! `command -v poetry`; then \
		sudo apt -y install curl; \
		(curl -sSL https://install.python-poetry.org | python3 -); \
		export PATH="$HOME/.local/bin:$PATH"; \
	fi

modify-torch-line:
	if [ $(IS_JETSON) = true ]; then \
		sed -i 's/^torch =.*/torch = {file = "packages\/torch-1.13.0a0+git7c98e70-cp38-cp38-linux_aarch64.whl"}/' pyproject.toml; \
		export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring; \
		poetry lock; \
	fi

install-dependency:
	sudo apt-get install -y portaudio19-dev libgirepository1.0-dev ; \
	export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring; \
	poetry env use python3; \
	poetry lock; \
	poetry install	

modify-alsa-config:
	if [ $(IS_JETSON) = true ]; then \
		sudo cp -f asound.conf /etc/asound.conf; \
	fi

install: install-precise-engine install-poetry modify-torch-line install-dependency modify-alsa-config

run:
	poetry run python assistant/app.py
