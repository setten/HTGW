from __future__ import division, print_function, unicode_literals

from abipy.core.testing import AbipyTest
from pymatgen import SETTINGS
from HTGW.flows.GWtasks import VaspGWTask, VaspGWExecuteTask, VaspGWInputTask, SingleVaspGWWork
from HTGW.flows.datastructures import GWSpecs
from HTGW.flows.tests.test_helpers import structure
from HTGW.flows.GWworks import VaspGWFWWorkFlow
from HTGW.flows.helpers import add_gg_gap, s_name
import os

POTCAR_DIR = SETTINGS.get("VASP_PSP_DIR")

# TODO: These tests produce several files. The execution of the test should be done in a temp directory.

__author__ = 'setten'


class GWVaspTest(AbipyTest):
    def test_VaspGWTasks(self):
        """
        testing the vasp GW task
        """
        spec = GWSpecs()
        struct = add_gg_gap(structure)
        structure_dict = struct.as_dict()
        band_structure_dict = {'vbm_l': structure.vbm_l, 'cbm_l': structure.cbm_l, 'vbm_a': structure.vbm[0],
                               'vbm_b': structure.vbm[1], 'vbm_c': structure.vbm[2], 'cbm_a': structure.cbm[0],
                               'cbm_b': structure.cbm[1], 'cbm_c': structure.cbm[2]}

        parameters = {'structure': structure_dict, 'band_structure': band_structure_dict, 'job': 'prep',
                      'spec': spec, 'option': None}
        task = VaspGWTask(parameters=parameters)
        self.assertEqual(task.get_launch_dir(), 'Si')
        self.assertEqual(task.get_prep_dir(), 'Si')
        self.assertIsNone(task.option)
        self.assertEqual(task.job,'prep')
        task = VaspGWInputTask(parameters=parameters)
        fwa = task.run_task({})
        task = VaspGWExecuteTask(parameters=parameters)
        # fwa = task.run_task({})

    def test_fw_vasp(self):
        fireworksflow = VaspGWFWWorkFlow()
        spec = GWSpecs()

        #task = VaspGWTask()

    def test_VaspSingle(self):
        spec = GWSpecs()
        spec.data['code'] = 'VASP'
        work = SingleVaspGWWork(structure=structure, spec=spec, job='prep')
        work.create_input()
        print(os.listdir('.'))
        for f in ['INCAR', 'POTCAR', 'POSCAR', 'KPOINTS', 'INCAR.DIAG']:
            self.assertIn(f, os.listdir(path=s_name(structure)))
        work.create_job_script(add_to_collection=False)
        self.assertIn('job', os.listdir(path=s_name(structure)))
        work.create_job_script(mode='slurm', add_to_collection=False)
        self.assertIn('job', os.listdir(path=s_name(structure)))
