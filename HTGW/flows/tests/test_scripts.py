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


class GWSetupTest(AbipyTest):
    def test_setup_single(self):
        """
        Testing the main functions called in the abiGWsetup script for a single shot calculation
        """

        spec_in = get_spec('GW')
        self.assertIsInstance(spec_in, GWSpecs)

        self.assert_equal(spec_in.test(), 0)
        self.assert_equal(len(spec_in.to_dict()), 10)
        self.assert_equal(spec_in.get_code(), 'ABINIT')

        spec_in.data['source'] = 'cif'

        self.assert_equal(spec_in.hash_str(), "code:ABINIT;source:cifjobs:['prep', 'G0W0'];mode:ceci;functional:PBE;kp_grid_dens:500prec:m;tol:0.0001;test:False;converge:False")

        wdir = tempfile.mkdtemp()
        print('wdir', wdir)

        os.chdir(wdir)

        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        shutil.copyfile(abidata.pseudo("14si.pspnc").path, os.path.join(wdir, 'Si.pspnc'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'shell_manager.yml'), os.path.join(wdir, 'manager.yml'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'simple_scheduler.yml'), os.path.join(wdir, 'scheduler.yml'))

        try:
            temp_ABINIT_PS_EXT = os.environ['ABINIT_PS_EXT']
            temp_ABINIT_PS = os.environ['ABINIT_PS']
        except KeyError:
            temp_ABINIT_PS_EXT = None
            temp_ABINIT_PS = None

        os.environ['ABINIT_PS_EXT'] = '.pspnc'
        os.environ['ABINIT_PS'] = wdir

        spec_in.data['source'] = 'cif'
        print('dirpath', abidata.dirpath)

        spec_in.write_to_file('spec.in')
        self.assertTrue(os.path.isfile(os.path.join(wdir, 'spec.in')))

        spec_in.loop_structures('i')

        if temp_ABINIT_PS is not None:
            os.environ['ABINIT_PS_EXT'] = temp_ABINIT_PS_EXT
            os.environ['ABINIT_PS'] = temp_ABINIT_PS

        ls = os.listdir('.')
        print(ls)
        self.assertEqual(ls, [u'job_collection', u'manager.yml', u'scheduler.yml', u'si.cif', u'Si.pspnc',
                              u'Si_si.cif', u'spec.in'])

        ls2 = os.listdir('Si_si.cif/')
        print(ls2)
        self.assertEqual(ls2, [u'.nodeid', u'__AbinitFlow__.pickle', u'indata', u'outdata', u'tmpdata', u'w0'])

        ls3 = os.listdir('Si_si.cif/w0/')
        print(ls3)
        self.assertEqual(ls3, [u'indata', u'outdata', u't0', u't1', u't2', u't3', u'tmpdata'])

        with open('Si_si.cif/w0/t0/run.abi') as f:
            abi = f.readlines()
        for x in [' ecut 44\n', ' tolvrs 1e-08\n', ' kptopt 1\n', ' ngkpt 6 6 6\n', ' nshiftk 1\n', ' nband 26\n']:
            self.assertIn(x, abi)

        with open('Si_si.cif/w0/t1/run.abi') as f:
            abi = f.readlines()
        for x in [' ecut 44\n', ' tolwfr 1e-17\n', ' kptopt 1\n', ' iscf -2\n']:
            self.assertIn(x, abi)

        with open('Si_si.cif/w0/t2/run.abi') as f:
            abi = f.readlines()
        for x in [' kptopt 1\n', ' shiftk 0 0 0\n', ' ngkpt 6 6 6\n', ' nshiftk 1\n', ' iscf -2\n', ' nband 60\n',
                  ' nsppol 1\n', ' ecut 44\n', ' toldfe 1e-08\n',' gwmem 10\n', ' inclvkb 2\n', '\n', ' symsigma 1\n',
                  ' ecuteps 8\n']:
            self.assertIn(x, abi)

        with open('Si_si.cif/w0/t3/run.abi') as f:
            abi = f.readlines()
        for x in [' kptopt 1\n', ' shiftk 0 0 0\n', ' ngkpt 6 6 6\n', ' nshiftk 1\n', ' iscf -2\n', ' nband 60\n',
                  ' nsppol 1\n', ' ecut 44\n', ' toldfe 1e-08\n', ' gwmem 10\n', ' inclvkb 2\n', '\n', ' symsigma 1\n',
                  ' ecutsigx 44\n', ' ecuteps 8\n', ' gw_qprange 2\n', ' ppmodel 1\n', ' gwcalctyp 00\n']:
            self.assertIn(x, abi)

    def test_setup_convergence(self):
        """
        Testing the main functions called in the abiGWsetup script for a convergence calculation
        """

        spec_in = get_spec('GW')
        self.assertIsInstance(spec_in, GWSpecs)

        self.assert_equal(spec_in.test(), 0)
        self.assert_equal(len(spec_in.to_dict()), 10)
        self.assert_equal(spec_in.get_code(), 'ABINIT')

        spec_in.data['source'] = 'cif'
        print(spec_in)
        spec_in.data['converge'] = 'True'

        self.assert_equal(spec_in.hash_str(),
                          "code:ABINIT;source:cifjobs:['prep', 'G0W0'];mode:ceci;functional:PBE;kp_grid_dens:500prec:m;tol:0.0001;test:False;converge:True")

        wdir = tempfile.mkdtemp()
        print('wdir', wdir)

        os.chdir(wdir)

        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        shutil.copyfile(abidata.pseudo("14si.pspnc").path, os.path.join(wdir, 'Si.pspnc'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'shell_manager.yml'), os.path.join(wdir, 'manager.yml'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'simple_scheduler.yml'),
                        os.path.join(wdir, 'scheduler.yml'))

        try:
            temp_ABINIT_PS_EXT = os.environ['ABINIT_PS_EXT']
            temp_ABINIT_PS = os.environ['ABINIT_PS']
        except KeyError:
            temp_ABINIT_PS_EXT = None
            temp_ABINIT_PS = None

        os.environ['ABINIT_PS_EXT'] = '.pspnc'
        os.environ['ABINIT_PS'] = wdir

        spec_in.data['source'] = 'cif'
        print('dirpath', abidata.dirpath)

        spec_in.write_to_file('spec.in')
        self.assertTrue(os.path.isfile(os.path.join(wdir, 'spec.in')))

        spec_in.loop_structures('i')

        if temp_ABINIT_PS is not None:
            os.environ['ABINIT_PS_EXT'] = temp_ABINIT_PS_EXT
            os.environ['ABINIT_PS'] = temp_ABINIT_PS

        ls = os.listdir('.')
        print(ls)
        self.assertEqual(ls, [u'job_collection', u'manager.yml', u'scheduler.yml', u'si.cif', u'Si.pspnc',
                              u'Si_si.cif', u'spec.in'])

        ls2 = os.listdir('Si_si.cif/')
        print(ls2)
        self.assertEqual(ls2, [u'.nodeid', u'__AbinitFlow__.pickle', u'indata', u'outdata', u'tmpdata', u'w0'])

        ls3 = os.listdir('Si_si.cif/w0/')
        print(ls3)
        # this test will break if the grid of nband and ecut eps values for convergence tests is changed
        self.assertEqual(len(ls3), 48)

        with open('Si_si.cif/w0/t0/run.abi') as f:
            abi = f.readlines()
        for x in [' ecut 50\n', ' tolvrs 1e-08\n', ' kptopt 1\n', ' ngkpt 2 2 2\n', ' nshiftk 1\n', ' nband 26\n']:
            self.assertIn(x, abi)

        with open('Si_si.cif/w0/t3/run.abi') as f:
            abi = f.readlines()
        for x in [' ecut 44\n', ' tolvrs 1e-08\n', ' kptopt 1\n', ' ngkpt 2 2 2\n', ' nshiftk 1\n', ' nband 26\n']:
            self.assertIn(x, abi)

        with open('Si_si.cif/w0/t4/run.abi') as f:
            abi = f.readlines()
        for x in [' ecut 44\n', ' tolwfr 1e-17\n', ' kptopt 1\n', ' iscf -2\n']:
            self.assertIn(x, abi)

        # reading this directory will break if the grid of nband and ecut eps values for convergence tests is changed
        with open('Si_si.cif/w0/t43/run.abi') as f:
            abi = f.readlines()
        for line in abi:
            print(line.strip())
        for x in [' kptopt 1\n', ' shiftk    0.0    0.0    0.0\n', ' ngkpt 2 2 2\n', ' nshiftk 1\n', ' iscf -2\n', ' nband 120\n',
                  ' nsppol 1\n', ' ecut 44\n', ' toldfe 1e-08\n', ' gwmem 10\n', ' inclvkb 2\n', '\n', ' symsigma 1\n',
                  ' ecuteps 12\n']:
            self.assertIn(x, abi)

        # reading this directory will break if the grid of nband and ecut eps values for convergence tests is changed
        with open('Si_si.cif/w0/t44/run.abi') as f:
            abi = f.readlines()
        for x in [' kptopt 1\n', ' shiftk    0.0    0.0    0.0\n', ' ngkpt 2 2 2\n', ' nshiftk 1\n', ' iscf -2\n', ' nband 120\n',
                  ' nsppol 1\n', ' ecut 44\n', ' toldfe 1e-08\n', ' gwmem 10\n', ' inclvkb 2\n', '\n', ' symsigma 1\n',
                  ' ecuteps 12\n', ' gw_qprange 2\n', ' ppmodel 1\n', ' gwcalctyp 00\n']:
            self.assertIn(x, abi)


class GWOutputTest(AbipyTest):
    def test_output_empty(self):
        """
        Testing loop_structures output parsing mode o empty case
        """
        wdir = tempfile.mkdtemp()
        print('wdir', wdir)
        os.chdir(wdir)
        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        spec_in = get_spec('GW')
        self.assertIsInstance(spec_in, GWSpecs)
        spec_in.data['source'] = 'cif'
        spec_in.data['converge'] = True
        return_value = spec_in.loop_structures('o')
        self.assertEqual(return_value[0], 0)
        self.assertEqual(return_value[1], 1)
        self.assertEqual(return_value[2], {u'Si_si.cif': u'calculation stage could not be determined for convergence calculation'})


class GWPrintTest(AbipyTest):
    def test_print_empty(self):
        """
        Testing loop_structures print mode w empty case
        """
        wdir = tempfile.mkdtemp()
        print('wdir', wdir)
        os.chdir(wdir)
        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        spec_in = get_spec('GW')
        self.assertIsInstance(spec_in, GWSpecs)
        spec_in.data['source'] = 'cif'
        spec_in.data['converge'] = True
        return_value = spec_in.loop_structures('w')
        self.assertEqual(return_value[0], 0)
        self.assertEqual(return_value[1], 1)
        self.assertEqual(return_value[2], {u'Si_si.cif': 'no convergence data found'})


class GWStoreTest(AbipyTest):
    def test_store_empty(self):
        """
        Testing loop_structures store mode s empty case
        """
        wdir = tempfile.mkdtemp()
        print('wdir', wdir)
        os.chdir(wdir)
        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        spec_in = get_spec('GW')
        self.assertIsInstance(spec_in, GWSpecs)
        spec_in.data['source'] = 'cif'
        return_value = spec_in.loop_structures('s')
        self.assertEqual(return_value[0], 0)
        self.assertEqual(return_value[1], 1)
        self.assertEqual(return_value[2], {u'Si_si.cif': 'no data found to insert in db'})
