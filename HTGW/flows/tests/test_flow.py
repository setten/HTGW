from __future__ import division, print_function, unicode_literals
import os

from abipy.core.testing import AbipyTest
from abipy.flowtk import Work, TaskManager, Flow, AbinitTask
__author__ = 'setten'

test_dir = os.path.join(os.path.dirname(__file__), "..", "..", 'test_files')


class FlowTest(AbipyTest):
    def test_flow(self):
        """
        Testing flow creation and task registering
        """
        flow = Flow(workdir=test_dir, manager=TaskManager.from_file(os.path.join(test_dir, "manager.yml")))
        inp = {}
        flow.register_task(input=inp)
        flow.allocate()
        self.assertTrue(flow.allocated)
        self.assertIsInstance(flow[0], Work)
        self.assertIsInstance(flow[0][0], AbinitTask)
        self.assertEqual(flow.check_status(), None)
