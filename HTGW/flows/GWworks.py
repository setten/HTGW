# coding: utf-8
from __future__ import print_function, division, unicode_literals, absolute_import

"""
Workflows for GW calculations:
 VaspGWFWWorkFlow fireworks wf for vasp
 SingleAbinitGWWorkFlow workflow for abinit
Under construction:
 general GW workflow that should manage all the code independent logic

"""

import os.path
import copy
import json
from abipy.flowtk.flows import Flow
from abipy.flowtk.tasks import TaskManager
from HTGW.flows.helpers import now, s_name, expand, read_grid_from_file, is_converged
from HTGW.flows.helpers import read_extra_abivars
from HTGW.flows.GWtasks import *
from abipy.abio.factories import g0w0_convergence_inputs

# to move to flowtk?
from abipy.flowtk.works import G0W0Work
from abipy.flowtk.pseudos import PseudoTable


__author__ = "Michiel van Setten"
__copyright__ = " "
__version__ = "0.9"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "May 2014"


MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


class GWWork(object):
    """
    UNDER CONSTRUCTION/extend
    Base class for GW workflows. the code specific implementations should extend this one.
    the base class should contain the convergence calculations structure
    """

    @property
    def grid(self):
        return self._grid

    @property
    def all_done(self):
        return self._all_done

    @property
    def workdir(self):
        return self._workdir

    def set_status(self, structure):
        self._grid = 0
        self._all_done = False
        self._workdir = None
        self._converged = is_converged(False, structure)
        try:
            self._grid = read_grid_from_file(s_name(structure)+".full_res")['grid']
            self._all_done = read_grid_from_file(s_name(structure)+".full_res")['all_done']
            self._workdir = os.path.join(s_name(structure), 'work_'+str(self.grid))
        except (IOError, OSError):
            pass


class VaspGWFWWorkFlow:
    """
    Object containing a VASP FireWorks GW workflow for a single structure
    """

    def __init__(self):
        self.work_list = []
        self.connections = {}
        self.fw_id = 1
        self.prep_id = 1
        self.wf = []

    def add_work(self, parameters):
        from fireworks.core.firework import FireWork
        tasks = []
        job = parameters['job']
        print('adding job ' + job + ' to the workslist as ', self.fw_id)
        if job == 'prep':
            launch_spec = {'task_type': 'Preparation job', '_category': 'cluster', '_queueadapter': 'qadapterdict'}
            task = VaspGWInputTask(parameters)
            tasks.append(task)
            task = VaspGWExecuteTask(parameters)
            tasks.append(task)
            task = VaspGWToDiagTask(parameters)
            tasks.append(task)
            task = VaspGWExecuteTask(parameters)
            tasks.append(task)
            fw = FireWork(tasks, spec=launch_spec, name=job, created_on=now(), fw_id=self.fw_id)
            self.connections[self.fw_id] = []
            self.prep_id = self.fw_id
            self.fw_id += 1
            print(self.connections)
        elif job in ['G0W0', 'GW0', 'scGW0']:
            launch_spec = {'task_type': 'GW job', '_category': 'cluster', '_queueadapter': 'qadapterdict'}
            task = VaspGWInputTask(parameters)
            tasks.append(task)
            task = VaspGWGetPrepResTask(parameters)
            tasks.append(task)
            task = VaspGWExecuteTask(parameters)
            tasks.append(task)
            if parameters['spec']['converge']:
                task = VaspGWWriteConDatTask(parameters)
                tasks.append(task)
                task = VaspGWTestConTask(parameters)
                tasks.append(task)
            fw = FireWork(tasks, spec=launch_spec, name=job, created_on=now(), fw_id=self.fw_id)
            self.connections[self.fw_id] = []
            self.connections[self.prep_id].append(self.fw_id)
            self.fw_id += 1
        else:
            fw = []
            print('unspecified job, this should have been captured before !!')
            exit()

        self.work_list.append(fw)

    def create(self):
        from fireworks.core.firework import Workflow
        self.wf = Workflow(self.work_list, self.connections, name='VaspGWFWWorkFlow', created_on=now())
        print('creating workflow')

    def add_to_db(self):
        from fireworks.core.launchpad import LaunchPad
        launchpad_file = os.path.join(os.environ['FW_CONFIG_DIR'], 'my_launchpad.yaml')
        lp = LaunchPad.from_file(launchpad_file)
        lp.add_wf(self.wf)


class SingleAbinitGWWork:
    """
    GW flow for Abinit
    """
    RESPONSE_MODELS = ["cd", "godby", "hybersten", "linden", "farid"]
    TESTS = {'ecuteps': {'test_range': (10, 14), 'method': 'direct', 'control': "gap", 'level': "sigma"},
             'nscf_nbands': {'test_range': (30, 40), 'method': 'set_bands', 'control': "gap", 'level': "nscf"},
             'response_model': {'test_range': RESPONSE_MODELS, 'method': 'direct', 'control': 'gap',
                                'level': 'screening'}}
    # scf level test are run independently, the last value will be used in the nscf and sigma tests
    # 'test': {'test_range': (1, 2, 3), 'method': 'direct', 'control': "e_ks_max", 'level': "scf"},
    CONVS = {'ecut': {'test_range': (50, 48, 46, 44), 'method': 'direct', 'control': "e_ks_max", 'level': "scf"},
             'ecuteps': {'test_range': (4, 6, 8, 10, 12), 'method': 'direct', 'control': "gap", 'level': "sigma"},
             'nscf_nbands': {'test_range': (5, 10, 15, 20), 'method': 'set_bands', 'control': "gap", 'level': "nscf"}}

    def __init__(self, structure, spec, option=None):
        self.structure = structure
        self.spec = spec
        if option is not None:
            option.pop('gap', None)
            option['nscf_nbands'] = option['nbands']
            option.pop('nbands', None)
        self.option = option
        print('option:', option)
        self.bands_fac = 1
        self.tests = self.__class__.get_defaults_tests()
        self.convs = self.__class__.get_defaults_convs()
        self.response_models = self.__class__.get_response_models()
        if self.option is None:
            self.all_converged = False
        elif len(self.option) == len(self.convs):
            self.all_converged = True
        else:
            self.all_converged = False
        path_add = '.conv' if self.all_converged else ''
        self.work_dir = s_name(self.structure)+path_add
        try:
            abi_pseudo = os.environ['ABINIT_PS_EXT']
            abi_pseudo_dir = os.environ['ABINIT_PS']
        except KeyError:
            abi_pseudo = None
            abi_pseudo_dir = None
        pseudos = []
        for element in self.structure.composition.element_composition:
            pseudo = os.path.join(abi_pseudo_dir, str(element) + abi_pseudo)
            pseudos.append(pseudo)
        self.pseudo_table = PseudoTable(pseudos)

    @classmethod
    def get_defaults_tests(cls):
        return copy.deepcopy(cls.TESTS)

    @classmethod
    def get_defaults_convs(cls):
        return copy.deepcopy(cls.CONVS)

    @classmethod
    def get_response_models(cls):
        return copy.deepcopy(cls.RESPONSE_MODELS)

    def get_electrons(self, structure):
        """
        Method for retrieving the number of valence electrons
        """
        electrons = 0

        for element in structure.species:
            pseudo = self.pseudo_table.pseudo_with_symbol(element.symbol)
            electrons += pseudo.Z_val
        return electrons

    def get_bands(self, structure):
        """
        Method for retrieving the standard number of bands
        """
        bands = self.get_electrons(structure) / 2 + len(structure)
        return int(bands)

    def get_work_dir(self):
            name = s_name(self.structure)
            if not self.all_converged:
                return str(name)+'_'+str(self.option['test'])+'_'+str(self.option['value'])
            else:
                return str(name)

    def create(self):
        """
        create single abinit G0W0 flow
        """
        # manager = 'slurm' if 'ceci' in self.spec['mode'] else 'shell'
        # an AbiStructure object has an overwritten version of get_sorted_structure that sorts according to Z
        # this could also be pulled into the constructor of Abistructure
        # abi_structure = self.structure.get_sorted_structure()
        from abipy import abilab
        item = copy.copy(self.structure.item)
        self.structure.__class__ = abilab.Structure
        self.structure = self.structure.get_sorted_structure_z()
        self.structure.item = item
        abi_structure = self.structure
        manager = TaskManager.from_user_config()
        # Initialize the flow.
        flow = Flow(self.work_dir, manager, pickle_protocol=0)
        # kpoint grid defined over density 40 > ~ 3 3 3
        if self.spec['converge'] and not self.all_converged:
            # (2x2x2) gamma centered mesh for the convergence test on nbands and ecuteps
            # if kp_in is present in the specs a kp_in X kp_in x kp_in mesh is used for the convergence study
            print('== here ===')
            print(self.spec.__class__)
            json.dumps(self.spec.data, indent=2)
            if 'kp_in' in self.spec.data.keys():
                if self.spec['kp_in'] > 9:
                    print('WARNING:\nkp_in should be < 13 to generate an n x n x n mesh\nfor larger values a grid with '
                          'density kp_in will be generated')
                kppa = self.spec['kp_in']
            else:
                kppa = 2
        else:
            # use the specified density for the final calculation with the converged nbands and ecuteps of other
            # stand alone calculations
            kppa = self.spec['kp_grid_dens']
        gamma = True

        # 'standard' parameters for stand alone calculation
        scf_nband = self.get_bands(self.structure) + 20
        # additional bands to accommodate for nbdbuf and a bit extra
        nscf_nband = [10 * self.get_bands(self.structure)]

        nksmall = None
        ecuteps = [8]

        extra_abivars = dict()

        # read user defined extra abivars from file  'extra_abivars' should be dictionary
        extra_abivars.update(read_extra_abivars())
        # self.bands_fac = 0.5 if 'gwcomp' in extra_abivars.keys() else 1
        # self.convs['nscf_nbands']['test_range'] =
        # tuple([self.bands_fac*x for x in self.convs['nscf_nbands']['test_range']])

        ecut = extra_abivars.pop('ecut', 44)
        ecutsigx = extra_abivars.pop('ecutsigx', 44)

        # if npfft is too large or if npfft changes between the nscf calcualtion and the screening / sigma calulations
        # strange things can happen
        if 'npfft' not in extra_abivars:
            extra_abivars['npfft'] = 3

        if ecutsigx > ecut:
            raise RuntimeError('ecutsigx can not be larger than ecut')
        if ecutsigx < max(ecuteps):
            raise RuntimeError('ecutsigx < ecuteps this is not realistic')

        response_models = ['godby']
        if 'ppmodel' in extra_abivars.keys():
            response_models = [extra_abivars.pop('ppmodel')]

        if self.option is not None:
            for k in self.option.keys():
                if k == 'ecut':
                    ecut = self.option[k]
                if k in ['ecuteps', 'nscf_nbands']:
                    pass
                else:
                    extra_abivars.update({k: self.option[k]})

        try:
            grid = read_grid_from_file(s_name(self.structure)+".full_res")['grid']
            all_done = read_grid_from_file(s_name(self.structure)+".full_res")['all_done']
            workdir = os.path.join(s_name(self.structure), 'w'+str(grid))
        except (IOError, OSError):
            grid = 0
            all_done = False
            workdir = None

        if not all_done:
            if (self.spec['test'] or self.spec['converge']) and not self.all_converged:
                if self.spec['test']:
                    print('| setting test calculation')
                    tests = SingleAbinitGWWork(self.structure, self.spec).tests
                    response_models = []
                else:
                    if grid == 0:
                        print('| setting convergence calculations for grid 0')
                        # tests = SingleAbinitGWWorkFlow(self.structure, self.spec).convs
                        tests = self.convs
                    else:
                        print('| extending grid')
                        # tests = expand(SingleAbinitGWWorkFlow(self.structure, self.spec).convs, grid)
                        tests = expand(self.convs, grid)
                ecuteps = []
                nscf_nband = []
                for test in tests:
                    if tests[test]['level'] == 'scf':
                        if self.option is None:
                            extra_abivars.update({test + '_s': tests[test]['test_range']})
                        elif test in self.option:
                            extra_abivars.update({test: self.option[test]})
                        else:
                            extra_abivars.update({test + '_s': tests[test]['test_range']})
                    else:
                        for value in tests[test]['test_range']:
                            if test == 'nscf_nbands':
                                nscf_nband.append(value * self.get_bands(self.structure))
                                # scr_nband takes nscf_nbands if not specified
                                # sigma_nband takes scr_nbands if not specified
                            if test == 'ecuteps':
                                ecuteps.append(value)
                            if test == 'response_model':
                                response_models.append(value)
            elif self.all_converged:
                print('| setting up for testing the converged values at the high kp grid ')
                # add a bandstructure and dos calculation
                if os.path.isfile('bands'):
                    nksmall = -30
                    # negative value > only bandstructure
                else:
                    nksmall = 30
                # in this case a convergence study has already been performed.
                # The resulting parameters are passed as option
                ecuteps = [self.option['ecuteps'], self.option['ecuteps'] + self.convs['ecuteps']['test_range'][1] -
                           self.convs['ecuteps']['test_range'][0]]
                nscf_nband = [self.option['nscf_nbands'], self.option['nscf_nbands'] + self.convs['nscf_nbands'][
                    'test_range'][1] - self.convs['nscf_nbands']['test_range'][0]]
                # for option in self.option:
                #    if option not in ['ecuteps', 'nscf_nband']:
                #        extra_abivars.update({option + '_s': self.option[option]})
        else:
            print('| all is done for this material')
            return

        logger.info('ecuteps : %s ' % str(ecuteps))
        logger.info('extra   : %s ' % str(extra_abivars))
        logger.info('nscf_nb : %s ' % str(nscf_nband))
        inputs = g0w0_convergence_inputs(abi_structure, self.pseudo_table, kppa, nscf_nband, ecuteps, ecutsigx,
                                         scf_nband, ecut, accuracy="normal", spin_mode="unpolarized", smearing=None,
                                         response_models=response_models, charge=0.0, gw_qprange=2,
                                         gamma=gamma, nksmall=nksmall, extra_abivars=extra_abivars)

        work = G0W0Work(scf_inputs=inputs[0], nscf_inputs=inputs[1], scr_inputs=inputs[2], sigma_inputs=inputs[3])

        # work = g0w0_extended_work(abi_structure, self.pseudo_table, kppa, nscf_nband, ecuteps, ecutsigx, scf_nband,
        # accuracy="normal", spin_mode="unpolarized", smearing=None, response_models=response_models,
        # charge=0.0, sigma_nband=None, scr_nband=None, gamma=gamma, nksmall=nksmall, **extra_abivars)

        print(workdir)
        flow.register_work(work, workdir=workdir)
        return flow.allocate()

    def create_job_file(self, serial=True):
        """
        Create the jobfile for starting all schedulers manually
        serial = True creates a list that can be submitted as job that runs all schedulers a a batch job
        (the job header needs to be added)
        serial = False creates a list that can be used to start all schedulers on the frontend in the background
        """
        job_file = open("job_collection", mode='a')
        if serial:
            job_file.write(str('abirun.py ' + self.work_dir + ' scheduler > ' + self.work_dir + '.log\n'))
            job_file.write(str('rm ' + self.work_dir + '/w*/t*/outdata/out_SCR\n'))
        else:
            job_file.write(str('nohup abirun.py ' + self.work_dir + ' scheduler > ' + self.work_dir + '.log & \n'))
            job_file.write(str('sleep 2\n'))
        job_file.close()
