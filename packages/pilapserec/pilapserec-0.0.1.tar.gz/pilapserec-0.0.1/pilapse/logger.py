#!/usr/bin/env python3

from .arguments import arguments
from .interface import logger

logging = logger(verbose=arguments['--verbose'])