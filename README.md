# Polyxia assistant

### Architecure

![Architecture](./assets/Architecture.png)

### Requirements

- Python 3.9
- python3.9-distutils
- python3.9-dev

## Installation

Create a `.env` file based on `.env.template` and fill the values.
Then to install the assistant you have to run:

```bash
make install
```

## Usage

To run the assistant simply run in your terminal:

```bash
make run
```

# Usage with Jetson nano

Because Nvidia does not maintain jetson nano, you have to flash it with a custom image to use newer version of python and pytorch.
Flash your jetson nano with: https://github.com/Qengineering/Jetson-Nano-Ubuntu-20-image

> Note: By default the partition size is 32 GB with this image, feel free to resize it if you need.

The jetson nano does not come standard with equipment such as a microphone and speakers. To communicate with the assistant you will need a headset that can be
connected via USB. Then simply plug the headset into one of the jetson's USB ports.

Then run:

```bash
make install
make run
```
