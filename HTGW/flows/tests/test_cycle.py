from __future__ import division, print_function, unicode_literals
import os
import shutil
import tempfile
import time
import sys
from abipy.core.testing import AbipyTest
from pymatgen.core.structure import Structure
from HTGW.scripts.abiGWsetup import main as gwsetup
from HTGW.scripts.abiGWoutput import main as gwoutput
from HTGW.flows.helpers import is_converged, read_grid_from_file, s_name
from HTGW.plotting.my_abiobjects import MySigResFile


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

        # the current version uses refence data from a run using the production version on zenobe
        # once all checks out the run should be done using the input generated using this version to replace the
        # reference

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
        print('      version with bandstructure and dos  ')
        gwsetup(update=False)
        self.assertTrue(os.path.isdir('SiC_SiC.cif.conv'))
        print(os.listdir(os.path.join(wdir, 'SiC_SiC.cif.conv', 'w0')))
        self.assertEqual(len(os.listdir(os.path.join(wdir, 'SiC_SiC.cif.conv', 'w0'))), 15)

        print(' ==== copy reference from second flow ===  ')
        time.sleep(1)  # the .conv directory should be older than the first one
        shutil.rmtree(os.path.join(wdir, 'SiC_SiC.cif.conv'))
        shutil.copytree(os.path.join(reference_dir, 'ref_res', 'SiC_SiC.cif.conv'),
                        os.path.join(wdir, 'SiC_SiC.cif.conv'))
        self.assertTrue(os.path.isdir(os.path.join(wdir, 'SiC_SiC.cif.conv')))
        self.assertEqual(len(os.listdir(os.path.join(wdir, 'SiC_SiC.cif.conv', 'w0'))), 13)

        print(' ==== process output ===  ')
        from cStringIO import StringIO
        backup = sys.stdout
        sys.stdout = StringIO()  # capture output
        gwoutput()
        out = sys.stdout.getvalue()  # release output
        sys.stdout.close()  # close the stream
        sys.stdout = backup  # restore original stdout

        print('=== *** ====\n'+out+'=== *** ====\n')
        gap = 0
        for l in out.split('\n'):
            if 'values' in l:
                gap = float(l.split(' ')[6])
        self.assertEqual(gap, 7.11495066416)

        print(os.listdir('.'))
        print('processed')
        self.assertTrue(os.path.isfile('SiC_SiC.cif.full_res'))
        full_res = read_grid_from_file(s_name(structure)+'.full_res')
        self.assertEqual(full_res, {u'all_done': True, u'remark': u'No converged SCf parameter found. Continue anyway.',
                                    u'grid': 0})
        self.assertTrue(os.path.isdir(os.path.join(wdir, 'SiC_SiC.cif.res')))
        self.assertEqual(len(os.listdir(os.path.join(wdir, 'SiC_SiC.cif.res'))), 5)
        print(os.listdir(os.path.join(wdir, 'SiC_SiC.cif.res')))
        with open(os.path.join(wdir, 'SiC_SiC.cif.res', 'out_SIGRES.nc'), 'r') as f:
            data = f.read()

        msrf = MySigResFile(data)
        self.assertEqual(msrf.homo, 6.6843830378711786)
        self.assertEqual(msrf.lumo, 8.0650328308487982)
        self.assertEqual(msrf.homo_gw, 6.2325949743130034)
        self.assertEqual(msrf.lumo_gw, 8.2504215095164763)
        self.assertEqual(msrf.fundamental_gap('ks'), msrf.lumo - msrf.homo)
        self.assertEqual(msrf.fundamental_gap('gw'), msrf.lumo_gw - msrf.homo_gw)
        self.assertAlmostEqual(msrf.fundamental_gap('gamma'), gap, places=3)

        # since we now have a mysigresfile object we test the functionality

        msrf.get_scissor()
        # return self.qplist_spin[0].build_scissors(domains=[[-200, mid], [mid, 200]], k=1, plot=False)

        msrf.get_scissor_residues()
        # return sc.residues

        msrf.plot_scissor(title='')

        msrf.plot_qpe(title='')

        # to be continued

        if temp_ABINIT_PS is not None:
            os.environ['ABINIT_PS_EXT'] = temp_ABINIT_PS_EXT
            os.environ['ABINIT_PS'] = temp_ABINIT_PS
