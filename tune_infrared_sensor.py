#!/usr/bin/env python3
import sys

from eva.run import run, create_infrared_tuner


if __name__ == '__main__':
    sys.exit(run(create_infrared_tuner))
