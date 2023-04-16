# Polyxia assistant

### Architecure
![Architecture](./assets/Architecture.png)


### Requirements
```bash
# If poetry is not installed
curl -sSL https://install.python-poetry.org | python3 -
```

## Installation 
```bash
git clone  ...
cd assistant
poetry install
```

Move .env.template to .env and fill the values

# Usage
```bash
poetry run python assistant/app.py
```



# Usage with Jetson nano
Because Nvidia does not maintain jetson nano, we are obliged to flash it with a custom image to use newer version of python and pytorch.
Flash your jetson nano with: https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image
> Note: By default the partition size is 32 GB with this image, feel free to resize it if you need.

Download custom build pytorch and put it at the root of this folder: https://drive.google.com/file/d/1e9FDGt2zGS5C5Pms7wzHYRb0HuupngK1/view


Then run 
```bash
make install
make run
```

You can then run the assistant app with `poetry run python assistant/app.py`