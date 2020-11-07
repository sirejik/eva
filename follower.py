#!/usr/bin/env python3
import sys

from eva.run import run, follow_sensor


if __name__ == '__main__':
    sys.exit(run(follow_sensor))
