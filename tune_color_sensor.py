#!/usr/bin/env python3
import sys

from eva.run import run, tune_reflected_intensity


if __name__ == '__main__':
    sys.exit(run(tune_reflected_intensity))
