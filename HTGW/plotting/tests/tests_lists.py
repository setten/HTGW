from __future__ import division, print_function, unicode_literals
from abipy.core.testing import AbipyTest
from HTGW.plotting.lists import ptable, colors


class ListTest(AbipyTest):
    """
    testing some data sets
    """

    def test_ptable(self):
        self.assertIsInstance(ptable, dict)

    def test_colors(self):
        self.assertIsInstance(colors, str)
