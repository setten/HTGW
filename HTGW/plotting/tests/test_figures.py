from __future__ import division, print_function, unicode_literals
from abipy.core.testing import AbipyTest
from HTGW.plotting.figures import figures, plot_help, figure_help


class ListTest(AbipyTest):
    """
    testing the Collection class for interation with the database
    """

    def test_figure_list(self):
        """
        test the presence of the figure list
        """
        self.assertIsInstance(figures, list)

    def test_plot_help(self):
        """
        test the plot help function
        """
        plot_help()

    def test_figure_help(self):
        """
        test the figure help function
        """
        figure_help()

