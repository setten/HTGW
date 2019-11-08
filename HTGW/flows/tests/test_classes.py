from __future__ import division, print_function, unicode_literals

import unittest
# try:
#     raise ImportError("No module named sets_deprecated")
# except ImportError:
#     raise unittest.SkipTest("Skipping all tests in test_classes due to sets_deprecated")

import shutil
import os
import tempfile
import json
import abipy.data as abidata
import copy

from abipy.core.testing import AbipyTest
from pymatgen.core.structure import Structure
# from pymatgen.io.vasp.GWvaspinputsets import GWDFTDiagVaspInputSet, GWG0W0VaspInputSet, GWscDFTPrepVaspInputSet
from HTGW.flows.GWvaspinputsets import GWDFTDiagVaspInputSet, GWG0W0VaspInputSet, GWscDFTPrepVaspInputSet
from HTGW.flows.GWvaspinputsets import SingleVaspGWWork
from HTGW.flows.datastructures import GWSpecs, GWConvergenceData, get_spec
from HTGW.flows.codeinterfaces import AbinitInterface, VaspInterface, get_code_interface
from HTGW.flows.tests.test_helpers import structure
from abipy.abilab import Structure as AbiStructure
from HTGW.flows.GWworks import GWWork, SingleAbinitGWWork, VaspGWFWWorkFlow
from abipy.flowtk import Flow, ScfTask, NscfTask, SigmaTask
from abipy.flowtk.tasks import ScrTask  # this does not import via flowtk
from pymatgen import SETTINGS

POTCAR_DIR = SETTINGS.get("VASP_PSP_DIR")

# TODO: These tests produce several files. The execution of the test should be done in a temp directory.

__author__ = 'setten'


class GWSpecTest(AbipyTest):
    def test_GWspect(self):
        """
        Testing the class GWSpecs()
        """
        spec = GWSpecs()
        self.assertEqual(len(spec.as_dict()), 10)
        self.assertIsInstance(spec, GWSpecs)
        self.assertEqual(spec.get_code(), 'ABINIT')
        self.assertIsInstance(spec.code_interface, AbinitInterface)
        spec.data['code'] = 'VASP'
        spec.update_code_interface()
        self.assertEqual(spec.get_code(), 'VASP')
        self.assertIsInstance(spec.code_interface, VaspInterface)

    def test_GWspect_test(self):
        """
        Testing warnings and errors of gwspecs
        """
        spec = GWSpecs()
        spec.test()
        self.assertEqual(len(spec.warnings), 0)
        self.assertEqual(len(spec.errors), 0)

    def test_GWget_spec(self):
        """
        Testing the factory function get_specs()
        """
        spec = get_spec('GW')
        self.assertIsInstance(spec, GWSpecs)


class GWConvergenceDataTest(AbipyTest):

    def test_GWConvergenceData(self):
        """
        Testing the class GWConvergenceData
        """
        spec = GWSpecs()
        self.assertIsInstance(structure, Structure)
        structure.item = 'mp-149'
        conv_data = GWConvergenceData(spec=spec, structure=structure)
        self.assertIsInstance(conv_data, GWConvergenceData)
        self.assertEqual(conv_data.name, 'Si_mp-149')
        self.assertEqual(conv_data.conv_res, {u'control': {}, u'derivatives': {}, u'values': {}})
        test_file = tempfile.mktemp()
        full_res = {u"grid": 0, u"all_done": True}
        f_name = conv_data.name+'.full_res'
        with open(f_name, 'w') as f:
            json.dump(obj=full_res, fp=f)
        conv_data.read_full_res_from_file()
        os.remove(f_name)
        self.assertEqual(conv_data.full_res, {'all_done': True, 'grid': 0})
        conv_res = {'control': {'ecuteps': True, 'nbands': True, 'ecut': True},
                    'values': {'ecuteps': 101.98825, 'nbands': 30.0, 'ecut': 12.0, 'gap': 3.13196},
                    'derivatives': {'ecuteps': 0.00023077744572658418, 'nbands': -0.0013567555555555532, 'ecut': 0.16666666666665808}}
        with open(test_file, 'w') as f:
            json.dump(obj=conv_res, fp=f)
        conv_data.read_conv_res_from_file(test_file)
        self.assertEqual(conv_data.conv_res['values']['nbands'], 30)
        self.assertEqual(conv_data.conv_res['derivatives']['ecuteps'], 0.00023077744572658418)
        conv_res = copy.deepcopy(conv_data.conv_res)
        self.assertEqual(conv_data.data, {})
        data_names = ['nbands', 'ecuteps',  'gwgap']
        data_list = [[30.00000, 101.98825, 3.13196], [30.00000, 203.97650, 3.14811], [30.00000, 326.36240, 3.14876],
                     [30.00000, 428.35065, 3.14880], [30.00000, 530.33890, 3.14881], [60.00000, 101.98825, 3.10808],
                     [60.00000, 203.97650, 3.13435], [60.00000, 326.36240, 3.13522], [60.00000, 428.35065, 3.13531],
                     [60.00000, 530.33890, 3.13532], [120.00000, 101.98825, 3.12039], [120.00000, 203.97650, 3.15994],
                     [120.00000, 326.36240, 3.16167], [120.00000, 428.35065, 3.16182], [120.00000, 530.33890, 3.16183],
                     [180.00000, 101.98825, 3.12198], [180.00000, 203.97650, 3.16845], [180.00000, 326.36240, 3.17183],
                     [180.00000, 428.35065, 3.17203], [180.00000, 530.33890, 3.17205]]
        for i, d in enumerate(data_list):
            conv_data.data[i] = dict(zip(data_names, d))
        data_names = ['ecut', 'full_width']
        data_list = [[10, 99], [12, 101], [13, 101], [14, 101]]
        ii = len(conv_data.data) + 1
        for i, d in enumerate(data_list):
            conv_data.data[i+ii] = dict(zip(data_names, d))

        # self.assertEqual(conv_data.data[0]['gwgap'], 3.13196)
        # conv_data.conv_res = {u'control': {}, u'derivatives': {}, u'values': {}}
        conv_data.find_conv_pars(tol=-0.1, silent=True)
        conv_data.find_conv_pars_scf('ecut', 'full_width', tol=-0.1, silent=True)
        conv_data.print_conv_res()
        print('********* here')
        print(conv_data.conv_res)
        self.assertEqual(conv_data.conv_res['control'], conv_res['control'])
        self.assertEqual(conv_data.conv_res['derivatives'], conv_res['derivatives'])
        # self.assertEqual(conv_data.conv_res['values'], conv_res['values'])
        for k in conv_data.conv_res['values']:
            self.assert_almost_equal(conv_data.conv_res["values"][k], conv_res['values'][k], decimal=4)

        # Remove artifact
        os.remove(conv_data.name +'.conv_res')


class GWTestCodeInterfaces(AbipyTest):
    def test_VaspInterface(self):
        """
        Testing the VASP code interface
        """
        interface = get_code_interface('VASP')
        self.assertIsInstance(interface, VaspInterface)
        self.assertEqual(len(interface.conv_pars), 3)
        self.assertEqual(len(interface.supported_methods), 4)
        self.assertFalse(interface.hartree_parameters)
        self.assertIsNone(interface.read_ps_dir())
        #self.assertEqual(interface.get_conv_res_test(spec_data=spec.data, structure=structure), {})

    def test_AbinitInterface(self):
        """
        Testing the ABINIT code interface
        """
        interface = get_code_interface('ABINIT')
        self.assertIsInstance(interface, AbinitInterface)
        self.assertEqual(len(interface.conv_pars), 3)
        self.assertEqual(len(interface.supported_methods), 2)
        self.assertFalse(interface.all_done)
        self.assertEqual(interface.grid, 0)
        self.assertTrue(interface.hartree_parameters)
        self.assertFalse(interface.converged)
        self.assertEqual(len(interface.other_vars), 1166)
        self.assertEqual(interface.gw_data_file, 'out_SIGRES.nc')
        w_path = os.path.join('HTGW', 'test_files', 'SiC_test_case', 'ref_res', 'SiC_SiC.cif', 'w0', 't0', 'outdata')
        os.listdir(w_path)
        print(interface.read_convergence_data(w_path))
        self.assertEqual(len(interface.read_convergence_data(w_path)), 4)
        self.assertTrue(interface.read_convergence_data(w_path)['full_width'] > 0.0)
        self.assertIsNone(interface.workdir)
        conv_res = {'values': {'nbands': 10, 'ecut': 10, 'ecuteps': 10}}
        self.assertEqual(interface.conv_res_string(conv_res), "{'nscf_nbands': 10, 'ecut': 10, 'ecuteps': 10}")
        self.assertEqual(interface.test_methods({'jobs': ['prep', 'G0W0']}), [])
        self.assertEqual(interface.test_methods({'jobs': ['scGW']}), ['scGW is not supported'])


class GWVaspInputSetTests(AbipyTest):

    def setUp(self):
        """
        Testing GWVaspInputSetTests setUp
        """
        self.structure = structure
        self.spec = GWSpecs()
        self.spec.data['code'] = 'VASP'
        self.spec.update_code_interface()

    def test_GWscDFTPrepVaspInputSet(self):
        """
        Testing GWVaspInputSetTests GWscDFTPrepVaspInputSet
        """
        print(type(self.structure))
        inpset = GWscDFTPrepVaspInputSet(structure=self.structure, spec=self.spec)
        self.assertIsInstance(inpset, GWscDFTPrepVaspInputSet)
        self.assertEqual(inpset.convs, {})

#    @unittest.skipIf(POTCAR_DIR is None, "POTCAR dir is None")
    def test_GWDFTDiagVaspInputSet(self):
        """
        Testing GWVaspInputSetTests GWDFTDiagVaspInputSet
        """
        self.maxDiff = None
        inpset = GWDFTDiagVaspInputSet(structure=self.structure, spec=self.spec)
        self.assertIsInstance(inpset, GWDFTDiagVaspInputSet)
        self.assertEqual(inpset.convs,
                         {u'NBANDS': {u'test_range': (10, 20, 30, 40, 50, 60, 70), u'control': u'gap',
                                      u'method': u'set_nbands'}})

        self.assertDictEqual(inpset.incar, {u'ALGO': u'Exact', u'EDIFF': 1e-10, u'IBRION': -1, u'ICHARG': 1,
                                            u'ISMEAR': -5, u'ISPIN': 1, u'LOPTICS': True, u'LORBIT': 11,
                                            u'LREAL': u'Auto', u'LWAVE': True, u'MAGMOM': [0.6, 0.6],
                                            u'NBANDS': 240, u'NELM': 1, u'NPAR': 40,
                                            u'PREC': u'Medium', u'SIGMA': 0.01})

#    @unittest.skipIf(POTCAR_DIR is None, "POTCAR dir is None")
    def test_GWG0W0VaspInputSet(self):
        """
        Testing GWVaspInputSetTests GWG0W0VaspInputSet
        """
        inpset = GWG0W0VaspInputSet(structure=self.structure, spec=self.spec)
        self.assertIsInstance(inpset, GWG0W0VaspInputSet)
        self.assertEqual(inpset.convs, {u'ENCUTGW': {u'test_range': (200, 400, 600, 800), u'control': u'gap', u'method': u'incar_settings'}})

    def test_SingleVaspGWWork(self):
        """
        Testing GWVaspInputSetTests SingleVaspGWWork
        """
        work = SingleVaspGWWork(structure=self.structure, spec=self.spec, job='prep')
        self.assertIsInstance(work, SingleVaspGWWork)


class GWworksTests(AbipyTest):

    def test_GWWork(self):
        """
        Testing the abstract class GWFWWork
        """
        struc = AbiStructure.from_file(abidata.cif_file("si.cif"))
        struc.item = 'test'
        self.assertIsInstance(struc, AbiStructure)
        work = GWWork()
        work.set_status(struc)
        self.assertEqual(work.workdir, 'Si_test/work_0')
        self.assertEqual(work.grid, 0)
        self.assertFalse(work.all_done)

    def test_VaspGWFWWorkFlow(self):
        """
        Testing the concrete VaspGWFWWorkFlow class
        """
        struc = AbiStructure.from_file(abidata.cif_file("si.cif"))
        struc.item = 'test'
        self.assertIsInstance(struc, AbiStructure)
        work = VaspGWFWWorkFlow()

        self.assertEqual(len(work.work_list), 0)
        self.assertEqual(len(work.connections), 0)
        self.assertEqual(work.fw_id, 1)
        self.assertEqual(work.prep_id, 1)
        self.assertEqual(len(work.wf), 0)

        if False:
            for job in ['prep', 'G0W0', 'GW0', 'scGW0']:
                parameters = dict()
                parameters['spec'] = dict()
                parameters['spec']['converge'] = True
                parameters['job'] = job
                work.add_work(parameters=parameters)

        # self.assertTrue(done, 'there are tests missing')

    def test_SingleAbinitGWWork(self):
        """
        Testing the concrete SingleAbinitGWWork class
        """
        struc = AbiStructure.from_file(abidata.cif_file("si.cif"))
        struc.item = 'test'

        wdir = tempfile.mkdtemp()
        shutil.copyfile(abidata.cif_file("si.cif"), os.path.join(wdir, 'si.cif'))
        shutil.copyfile(abidata.pseudo("14si.pspnc").path, os.path.join(wdir, 'Si.pspnc'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'shell_nompi_manager.yml'),
                        os.path.join(wdir, 'manager.yml'))
        shutil.copyfile(os.path.join(abidata.dirpath, 'managers', 'simple_scheduler.yml'), os.path.join(wdir, 'scheduler.yml'))

        temp_ABINIT_PS_EXT = os.environ.get('ABINIT_PS_EXT', None)
        temp_ABINIT_PS = os.environ.get('ABINIT_PS', None)

        os.environ['ABINIT_PS_EXT'] = '.pspnc'
        os.environ['ABINIT_PS'] = wdir
        self.assertIsInstance(struc, AbiStructure)
        spec = get_spec('GW')
        spec.data['kp_grid_dens'] = 100
        spec.data['kp_in'] = -100
        with open(os.path.join(wdir, 'extra_abivars'), 'w') as f:
            f.write('{"ecut": 8, "ecutsigx": 8}')

        work = SingleAbinitGWWork(struc, spec)
        self.assertEqual(len(work.CONVS), 3)

        conv_strings = ['method', 'control', 'level']
        for test in work.CONVS:
            self.assertIsInstance(work.CONVS[test]['test_range'], tuple)
            for item in conv_strings:
                self.assertIsInstance(work.CONVS[test][item], str)
        self.assertEqual(work.work_dir, 'Si_test')
        self.assertEqual(len(work.pseudo_table), 1)
        self.assertEqual(work.bands_fac, 1)

        self.assertEqual(work.get_electrons(struc), 8)
        self.assertEqual(work.get_bands(struc), 6)
        self.assertGreater(work.get_bands(struc), work.get_electrons(struc) / 2, 'More electrons than bands, very bad.')

        flow = work.create()
        print(work.work_dir)
        print(flow.workdir)
        print(flow[0].workdir)
        self.assertIsInstance(flow, Flow)
        self.assertEqual(len(flow), 1)      # one work
        self.assertEqual(len(flow[0]), 4)   # with 4 tasks
        # self.assertEqual(flow.workdir, 'Si')

        self.assertEqual(flow.build_and_pickle_dump(), 0)
        # some more tests
        flow.rmtree()

        spec = get_spec('GW')
        spec.data['converge'] = True
        struc.item = 'converge'
        work = SingleAbinitGWWork(struc, spec)
        flow = work.create()
        self.assertEqual(len(flow[0]), 45)
        self.assertEqual(flow[0][0].__class__, ScfTask)
        self.assertEqual(flow[0][1].__class__, ScfTask)
        self.assertEqual(flow[0][2].__class__, ScfTask)
        self.assertEqual(flow[0][3].__class__, ScfTask)
        self.assertEqual(flow[0][4].__class__, NscfTask)
        self.assertEqual(flow[0][5].__class__, ScrTask)
        self.assertEqual(flow[0][6].__class__, SigmaTask)

        ecuts = [dict(task.input.as_dict()['abi_args'])['ecut'] for task in flow[0]]
        print('ecuts:', ecuts)
        # it is essential that the first four are diffent, this is for the convergence study of ecut, and that
        # after that is stays the same
        self.assertEqual(ecuts, [50, 48, 46, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44,
                                 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44, 44,
                                 44])

        nbands = [dict(task.input.as_dict()['abi_args'])['nband'] for task in flow[0]]
        print('nbands:', nbands)
        # the firs 4 should be 'low' these are self consistent
        # the fifth should be the maximum of what follows
        # the 6th and on should always be pairs that are the same, they are combinations of scr and sigma tasks
        self.assertEqual(nbands, [26, 26, 26, 26, 120, 30, 30, 60, 60, 90, 90, 120, 120, 30, 30, 60, 60, 90, 90, 120,
                                  120, 30, 30, 60, 60, 90, 90, 120, 120, 30, 30, 60, 60, 90, 90, 120, 120, 30, 30, 60,
                                  60, 90, 90, 120, 120])

        ecuteps = [dict(task.input.as_dict()['abi_args']).get('ecuteps', None) for task in flow[0]]
        print('ecuteps:', ecuteps)
        self.assertEqual(ecuteps, [None, None, None, None, None, 4, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 6, 6, 6, 6, 6, 8, 8,
                                   8, 8, 8, 8, 8, 8, 10, 10, 10, 10, 10, 10, 10, 10, 12, 12, 12, 12, 12, 12, 12, 12])

        inplens = [len(task.input.as_dict()['abi_args']) for task in flow[0]]
        print(inplens)
        self.assertEqual(inplens, [18, 18, 18, 18, 19, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31,
                                   29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29, 31, 29,
                                   31, 29, 31])

        ngkpts = [dict(task.input.as_dict()['abi_args'])['ngkpt'] for task in flow[0]]

        for ngkpt in ngkpts:
            self.assertEqual(ngkpt, [2, 2, 2])

        npffts = [dict(task.input.as_dict()['abi_args'])['npfft'] for task in flow[0]]

        self.assertTrue(all(x == 3 for x in npffts))

        self.assertEqual(flow.build_and_pickle_dump(), 0)

        # some more tests
        flow.rmtree()

        if temp_ABINIT_PS is not None:
            os.environ['ABINIT_PS_EXT'] = temp_ABINIT_PS_EXT
            os.environ['ABINIT_PS'] = temp_ABINIT_PS
