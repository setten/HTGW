#!/usr/bin/env python
"""
Script to store GW results for VASP and ABINIT in a database.
"""
from __future__ import unicode_literals, division, print_function, absolute_import
import os.path
import sys
from HTGW.flows.datastructures import get_spec

__author__ = "Michiel van Setten"
__copyright__ = " "
__version__ = "0.9"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "May 2014"


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    spec_in = get_spec('GW')
    spec_in.read_from_file('spec.in')
    counters = spec_in.loop_structures('s')
    return counters

if __name__ == "__main__":
    sys.exit(main())
