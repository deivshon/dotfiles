#!/bin/python3

import os
import sys

from setup.lib.venv import venv

if os.environ.get("VIRTUAL_ENV") is None:
    sys.exit(venv.run_with(__file__, sys.argv[1:]))

from setup import setup
setup.main()
