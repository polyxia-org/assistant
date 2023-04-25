.PHONY: install-precise-engine install-poetry modify-torch-line install-dependency

ARCH := $(shell uname -m)

install-precise-engine:
	if ! [ -d precise-engine ]; then \
		if [ $(ARCH) = "aarch64" ]; then \
			wget https://github.com/MycroftAI/precise-data/raw/dist/aarch64/precise-engine_0.3.0_aarch64.tar.gz; \
			tar xvf precise-engine_0.3.0_aarch64.tar.gz; \
			rm precise-engine_0.3.0_aarch64.tar.gz; \
		else \
			wget https://github.com/MycroftAI/precise-data/raw/dist/$(ARCH)/precise-engine.tar.gz; \
			tar xvf precise-engine.tar.gz; \
			rm precise-engine.tar.gz; \
		fi \
	fi
	
install-poetry:
	if ! `command -v poetry`; then \
		sudo apt -y install curl; \
		(curl -sSL https://install.python-poetry.org | python3 -); \
	fi

modify-torch-line:
	if [ $(ARCH) = "aarch64" ]; then \
		sed -i 's/^torch =.*/torch = {file = "packages\/torch-1.13.0a0+git7c98e70-cp38-cp38-linux_aarch64.whl"}/' pyproject.toml; \
		export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring; \
		poetry lock; \
	fi

install-dependency:
	sudo apt-get install -y portaudio19-dev libgirepository1.0-dev ; \
	export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring; \
	poetry install; \

modify-alsa-config:
	if [ $(ARCH) = "aarch64" ]; then \
		sudo cp -f asound.conf /etc/asound.conf; \
	fi

install: install-precise-engine install-poetry modify-torch-line install-dependency modify-alsa-config

run:
	poetry run python assistant/app.py
