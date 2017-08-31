from __future__ import division, print_function, unicode_literals
import os
import shutil
import tempfile
import abipy.data as abidata
from abipy.core.testing import AbipyTest
from pymatgen.core.structure import Structure
from HTGW.flows.datastructures import GWSpecs, get_spec  # , GWConvergenceData
from HTGW.scripts.abiGWsetup import main as gwsetup
from HTGW.scripts.abiGWoutput import main as gwoutput
from HTGW.flows.helpers import is_converged


__author__ = 'setten'

__reference_dir__ = os.path.join(os.getcwd(), 'HTGW', 'test_files')
if not os.path.isdir(__reference_dir__):
    print('failing to read from %s' % __reference_dir__)
    print(os.listdir(__reference_dir__))
    raise RuntimeError('to run nose or py test needs to be started in the HTGW root')


class ConvergenceFullCycleTest(AbipyTest):
    def SiC_conv_test(self):
        """
        Testing a full convergence calculation cycle on SiC using precomupted data.
        """
        wdir = tempfile.mkdtemp()
        os.chdir(wdir)

        try:
            temp_ABINIT_PS_EXT = os.environ['ABINIT_PS_EXT']
            temp_ABINIT_PS = os.environ['ABINIT_PS']
        except KeyError:
            temp_ABINIT_PS_EXT = None
            temp_ABINIT_PS = None

        os.environ['ABINIT_PS_EXT'] = '.psp8'
        os.environ['ABINIT_PS'] = wdir

        reference_dir = os.path.join(__reference_dir__, 'SiC_test_case')
        if not os.path.isdir(reference_dir):
            print('failing to read from %s' % reference_dir)
            print(os.listdir(reference_dir))
            raise RuntimeError('to run ConvergenceFullCycleTest nose or py test needs to be started in the '
                               'HTGW root')

        # copy input
        print(wdir)
        self.assertTrue(os.path.isdir(reference_dir))
        src_files = os.listdir(reference_dir)
        for file_name in src_files:
            full_file_name = os.path.join(reference_dir, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, wdir)
        self.assertEqual(len(os.listdir(wdir)), 6)

        print(os.listdir(wdir))
        structure = Structure.from_file('SiC.cif')
        structure.item = 'SiC.cif'

        print(' ==== generate flow ===  ')
        gwsetup(update=False)
        self.assertTrue(os.path.isdir(os.path.join(wdir, 'SiC_SiC.cif')))
        print(os.listdir(os.path.join(wdir)))
        print(os.listdir(os.path.join(wdir, 'SiC_SiC.cif')))
        self.assertTrue(os.path.isfile(os.path.join(wdir, 'SiC_SiC.cif', '__AbinitFlow__.pickle')))
        self.assertEqual(len(os.listdir(os.path.join(wdir, 'SiC_SiC.cif', 'w0'))), 48)

        print(' ==== copy reference results from first calculation ===  ')
        shutil.rmtree(os.path.join(wdir, 'SiC_SiC.cif'))
        shutil.copytree(os.path.join(reference_dir, 'ref_res', 'SiC_SiC.cif'), os.path.join(wdir, 'SiC_SiC.cif'))
        self.assertTrue(os.path.isdir(os.path.join(wdir, 'SiC_SiC.cif')))
        self.assertEqual(len(os.listdir(os.path.join(wdir, 'SiC_SiC.cif', 'w0'))), 68)

        print(' ==== process output ===  ')
        gwoutput()
        print(os.listdir('.'))
        self.assertTrue(os.path.isfile('plot-fits'))
        self.assertTrue(os.path.isfile('plots'))
        self.assertEqual(is_converged(hartree_parameters=True, structure=structure, return_values=True),
                         {u'ecut': 44.0, u'ecuteps': 4.0, u'gap': 6.816130591466406, u'nbands': 60})
        self.assertTrue(os.path.isfile('SiC_SiC.cif.full_res'))

        print(' ==== generate next flow ===  ')
        gwsetup(update=False)
        self.assertTrue(os.path.isdir('SiC_SiC.cif.conv'))

        # to be continued

        print(' ==== copy reference from second flow ===  ')

        if temp_ABINIT_PS is not None:
            os.environ['ABINIT_PS_EXT'] = temp_ABINIT_PS_EXT
            os.environ['ABINIT_PS'] = temp_ABINIT_PS
