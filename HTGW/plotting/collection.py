from __future__ import print_function, division

__author__ = 'setten'
__version__ = "0.1"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "Sept 2014"

import os
import sys
import pymongo
import gridfs
import time as time
from plots import ConvTest
from my_abiobjects import MySigResFile, MyBandsFile
from pymatgen.matproj.rest import MPRester, MPRestError
from abipy.flowtk.netcdf import NetcdfReaderError
from pymatgen.util.convergence import determine_convergence
from HTGW.flows.datastructures import GWConvergenceData
from gridfs.errors import NoFile
from abipy.abilab import abiopen, ElectronBandsPlotter
from pymongo.errors import CursorNotFound


class Collection(object):
    """
    object to store a database collection
    """
    def __init__(self):
        self.systems = []
        self.ps = []
        self.functionals = []
        self.extra = []
        self.data_set = []
        self.col, self.gfs = self.get_collection()
        self.col_external = self.get_collection(db_name='band_gaps', collection=None)

#local_serv = pymongo.Connection("marilyn.pcpm.ucl.ac.be")
#local_db_gaps = local_serv.band_gaps
#pwd = os.environ['MAR_PAS']
#local_db_gaps.authenticate("setten", pwd)

    def get_collection(self, server="marilyn.pcpm.ucl.ac.be", db_name="GW_results", collection="general"):
        """
        Add the actual pymongo collection object as self.col

        :param server:
        name of the server

        :param db_name:
        name of the data_base

        :param collection:
        name of the collection

        :return:
        """
        local_serv = pymongo.Connection(server)
        try:
            user = os.environ['MAR_USER']
        except KeyError:
            user = raw_input('DataBase user name: ')
        try:
            pwd = os.environ['MAR_PAS']
        except KeyError:
            pwd = raw_input('DataBase pwd: ')
        db = local_serv[db_name]
        db.authenticate(user, pwd)
        if collection is None:
            return db
        else:
            return db[collection], gridfs.GridFS(db)


    @property
    def total_entries(self):
        """
        :return:
        the total number of enrties in the collection
        """
        return self.col.count()

    @property
    def all_systems(self, p=False):
        """
        :return:
        a list of all systems in the collection
        """
        l = []
        for i in self.col.find():
            if i['system'] not in l:
                l.append(i['system'])
                if p:
                    print(i['system'])
        return l

    @staticmethod
    def fix_extra(extra_vars):
        """
        method to return a clean tag based on extra abivars
        """
        if extra_vars is None:
            tag = 'default'
            return tag
        else:
            tag = ""

        if "gwcomp" in extra_vars.keys():
            if extra_vars['gwcomp'] == 1:
                tag += "ExtraPolar"
                if "gwencomp" in extra_vars.keys():
                    tag += "@"+str(extra_vars['gwencomp'])+"H"
                else:
                    tag += "@2H"

        if 'inclvkb' in extra_vars.keys():
                if len(tag) > 0:
                    tag += "."
                tag += "INCLVKB" + str(extra_vars['inclvkb'])

        if 'ecut' in extra_vars.keys():
            if len(tag) > 0:
                tag += "."
            tag += "@" + str(extra_vars['ecut']) + 'H'

        if 'npfft' in extra_vars.keys():
            if len(tag) > 0:
                tag += "."
            tag += "NPFFT" + str(extra_vars['npfft'])

        return tag

    def get_property_lists(self, query=None, exclude=None):
        """
        add the propperty lists the object as:

        self.systems : a list of systems that occur in the collection
        self.functionals : a list of occuring functionals
        self.ps : a list of occuring pseudos
        self.extra : a list of occuring extra parameres
        """
        if query is None:
            query = {}
        if exclude is None:
            exclude = []
        for item in self.col.find(query):
            sys = item['system'].split('_')[0]
            if sys not in self.systems and sys not in exclude:
                self.systems.append(sys)
            ps = item['ps'].split('/')[-2]
            if ps not in self.ps and ps not in exclude:
                self.ps.append(ps)
            f = item['spec']['functional']
            if f not in self.functionals and f not in exclude:
                self.functionals.append(item['spec']['functional'])
            ex = self.fix_extra(item['extra_vars'])
            if ex not in self.extra and ex not in self.extra:
                self.extra.append(ex)

    def property_lists(self):
        """
        print the property_lists
        :return:
        """
        print("Systems:\n %s\n" % self.systems)
        print("Functionals:\n %s\n" % self.functionals)
        print("Pseudos:\n %s\n" % self.ps)
        print("Extra vars:\n %s" % self.extra)

    def get_data_set(self, query=None, sigresdata=False, get_exp=False, update=False):
        """
        method to retrieve a data set from database
        """
        self.data_set = []
        #print('retreiving data:')
        #print(query)
        if sigresdata:
            print('may need to parse nc files, this may take some time')
        if query is None:
            query = {}
        for item in self.col.find(query):
            try:
                mpid = item['system'].split('_mp-')[1]
            except IndexError:
                mpid = 0
            try:
                entry = {'system': item['system'].split('_mp-')[0],
                         'id': "mp-%s" % mpid,
                         'ps': item['ps'].split('/')[-2],
                         'xc': item['spec']['functional'],
                         'kp_in': item['spec']['kp_in'],
                         'extra': self.fix_extra(item['extra_vars']),
                         'data': item['gw_results']}
                print("id: %s" % entry['id'])
                mp_id = entry['id'].split('mp-')[1]
                try:
                    for exp_result in self.col_external.exp.find({'MP_id': str(mp_id)}):
                        expgap = exp_result['band_gap']
                        icsd = exp_result['icsd_data']['icsd_id']
                    entry['expgap'] = expgap
                    for pbe_result in self.col_external.GGA_BS.find({'transformations.history.0.id': icsd}):
                        pbegap = pbe_result['analysis']['bandgap']
                    entry['pbegap'] = pbegap
                except:
                    print(str(mp_id))
                    expgap = None
                    icsd = None
                    pbegap = None
                if sigresdata:
                    try:
                        if update:
                            raise KeyError
                        if 'max_en' not in item['srf_data'].keys():
                            raise KeyError
                        entry['data'].update(item['srf_data'])
                        sys.stdout.write(".")
                        sys.stdout.flush()
                    except KeyError:
                        sys.stdout.write(":")
                        sys.stdout.flush()
                        try:
                            print('getting srfdata')
                            srf = MySigResFile(self.gfs.get(item['results_file']).read())
                            srf_data = {'gwfgap': srf.fundamental_gap('gw'),
                                        'ksfgap': srf.fundamental_gap('ks'),
                                        'gwggap': srf.fundamental_gap('gamma'),
                                        'gwhomo': srf.homo_gw,
                                        'kshomo': srf.homo,
                                        'gwlumo': srf.lumo_gw,
                                        'kslumo': srf.lumo,
                                        'max_en': srf.en_max_band,
                                        'scissor_residues': srf.scissor_residues}
                            entry['data'].update(srf_data)
                        except (IOError, OSError, NetcdfReaderError):
                            srf_data = {'gwfgap': 0,
                                        'ksfgap': 0,
                                        'gwhomo': 0,
                                        'kshomo': 0,
                                        'gwlumo': 0,
                                        'kslumo': 0,
                                        'max_en': 0,
                                        'scissor_residues': [0, 0]}
                            entry['data'].update(srf_data)
                        item['srf_data'] = srf_data
                        self.col.save(item)
                    if item['system'] not in []:
                        print('bands for', item['system'])
                        try:
                            #if 'gwbgap' not in item['bs_data'].keys():
                            if item['bs_data']['gwbgap'] is None:
                                raise KeyError
                            entry['data'].update(item['bs_data'])
                            sys.stdout.write(".")
                            sys.stdout.flush()
                            #raise KeyError
                        except KeyError:
                            try:
                                t0 = time.time()
                                if item['system'] in ['As2Os_mp-2455', 'AgI_mp-22894', 'PbO_mp-20878', 'Cu2O_mp-361']:
                                    raise KeyError
                                with self.gfs.get(item['ksbands_file']) as f:
                                    ksb = MyBandsFile(f.read())
                                t = time.time() - t0
                                print('reading bands : %s' % t)
                                t0 = time.time()
                                with self.gfs.get(item['results_file']) as g:
                                    srf = MySigResFile(g.read())
                                t = time.time() - t0
                                print('reading srf : %s' % t)
                                t0 = time.time()
                                scissor = srf.get_scissor()
                                gwbhomo = ksb.homo + scissor.apply(ksb.homo)
                                gwblumo = ksb.lumo + scissor.apply(ksb.lumo)
                                bs_data = {'ksbgap': ksb.lumo - ksb.homo,
                                           'ksbhomo': ksb.homo,
                                           'gwbhomo': gwbhomo,
                                           'ksblumo': ksb.lumo,
                                           'gwblumo': gwblumo,
                                           'gwbgap':  gwblumo - gwbhomo}
                                entry['data'].update(bs_data)
                                t = time.time() - t0
                                print('making updating : %s' % t)
                                print('got ksbandsdata')
                            except (NoFile, KeyError, ValueError, KeyboardInterrupt): # (KeyError, NoFile, NetcdfReaderError, ValueError):
                                print('failed getting ksbandsdata')
                                bs_data = {'ksbgap': None,
                                           'ksbhomo': None,
                                           'gwbhomo': None,
                                           'gwblumo': None,
                                           'ksblumo': None,
                                           'gwbgap': None}
                            #else:
                            #    print('in else', item['system'])
                            #    bs_data = {'ksbgap': 0,
                            #                'ksbhomo': 0,
                            #                'gwbhomo': 0,
                            #                'gwblumo': 0,
                            #                'ksblumo': 0,
                            #                'gwbgap': 0}
                            #    entry['data'].update(bs_data)
                            item['bs_data'] = bs_data
                            self.col.save(item)

                self.data_set.append(entry)
            except CursorNotFound:
                print('cursonotfound')
        print('\n')

    def review(self, query=None):
        """
        print for each ellement in the collection the basic information and keep or remove it

        :param query: query for which the operation is performed
        """
        if query is None:
            query = {}
        for item in self.col.find(query).sort('system'):
            print('System: ', item['system'])
            print('Ps    : ', item['ps'])
            print('extra : ', item['extra_vars'])
            try:
                print('data  : ', item['results_file'], item['data_file'])
            except:
                pass
            keep = raw_input('Keep this item: (y, n) ')
            if keep == 'n':
                print('removing', item['_id'])
                self.col.remove(item['_id'])

    def conv_plots(self, query=None, silent=False, title=None):
        """
        plot the convergence plots for all entries in query
        """
        if query is None:
            query = {}
        for item in self.col.find(query):
            #gw_conv_data = GWConvergenceData(spec={'code': 'ABINIT'}, structure=None)
            if not silent:
                print('System    : ', item['system'])
                print('Ps        : ', item['ps'])
                print('extra     : ', item['extra_vars'])
                print('gwresults : ', item['gw_results'])
            try:
                if not silent:
                    print('data  : ', item['data_file'])
                if True:  # isinstance(item['data_file'], ObjectId):
                    f = self.gfs.get(item['data_file'])
                    data = f.read()
                    xx = []
                    yy = []
                    x = []
                    y = []
                    z = []
                    for line in data.splitlines():
                        if len(line) > 1 and 'data' not in line:
                            x.append(float(line.split()[0]))
                            y.append(float(line.split()[1]))
                            z.append(float(line.split()[2]))
                            # collect the gap vs ecuteps curve for calculating the interpolated ecuteps
                            if abs(float(line.split()[0]) - item['gw_results']['nbands']) < 20:
                                xx.append(float(line.split()[1]))
                                yy.append(float(line.split()[2]))
                    #print(xx)
                    #print(yy)
                    tol = 0.05
                    convres = determine_convergence(xs=xx, ys=yy, name='test', tol=-tol)
                    n = convres[3]
                    if n > 0:
                        dx = abs(xx[n] - xx[n-1])
                        dy = abs(yy[n] - yy[n-1])
                        print(n, dx, dy)
                        if convres[2] < convres[4]:
                            m = convres[4] - tol
                            f = (m - yy[n-1]) / dy
                        else:
                            m = convres[4] + tol
                            f = (yy[n-1] - m) / dy
                        print('extrapol: %s, border: %s, factor %s ' % (convres[4],  m, f))
                        ecuteps_interpol = xx[n-1] + f * dx
                    else:
                        ecuteps_interpol = convres[1]
                    ecuteps_interpol = ecuteps_interpol if ecuteps_interpol < 500000 else None
                    item['gw_results']['ecuteps_interpol'] = ecuteps_interpol
                    print('interpolated ecuteps: %s' % ecuteps_interpol)
                    #print(item)
                    self.col.save(item)
                    if title is None:
                        t = item['system']
                    else:
                        t = title
                    try:
                        p = ConvTest(title=t, x=x, y=y, z=z)
                        p.show()
                    except ValueError:
                        print('bad data')
                        dummy = raw_input('next')

            except (KeyError, NoFile):
                print('no convergence plot in DataBase')
                #dummy = raw_input('next')

        return p.return_fig_ax()

    def sigres_plots(self, query=None, sort='system'):
        """
        Plot the scissor operators for all the systems in the DB
        :param query:
        :param sort:
        :return:
        """
        if query is None:
            query = {}
        for item in self.col.find(query).sort(sort):
            print('System    : ', item['system'].split('_')[0])
            print('Ps        : ', item['ps'])
            print('extra     : ', item['extra_vars'])
            print('gwresults : ', item['gw_results'])
            try:
                print('data  : ', item['results_file'])
                data = self.gfs.get(item['results_file']).read()
                if len(data) > 1000:
                    srf = MySigResFile(data)
                    title = "QPState corrections of " + str(item['system']) + "\nusing "\
                            + str(item['ps'].split('/')[-2])
                    if item['extra_vars'] is not None:
                        title += ' and ' + str(self.fix_extra(item['extra_vars']))
                    fig = srf.plot_scissor(title=title)
                    srf.print_gap_info()
                    sc = srf.get_scissor()
                    try:
                        if not item['tgwgap']:
                            bands_data = self.gfs.get(item['ksbands_file'])
                            ks_bands = MyBandsFile(bands_data)
                            item['tkshomo'] = ks_bands.homo
                            item['tkslumo'] = ks_bands.lumo
                            item['tksgap'] = ks_bands.lumo - ks_bands.homo
                            item['tgwhomo'] = ks_bands.homo + sc.apply(ks_bands.homo)
                            item['tgwlumo'] = ks_bands.lumo + sc.apply(ks_bands.lumo)
                            item['tgwgap'] = item['tgwlumo'] - item['tgwhomo']
                            self.col.save(item)
                    except KeyError:
                        pass
            except IOError:
                print('No Sigres file in DataBase')
                dummy = raw_input('next')

        try:
            return fig
        except UnboundLocalError:
            return None

    def band_plots(self, query=None, sort='system'):
        """
        Plot the scissored bands for all the systems in the DB
        :param query:
        :param sort:
        :return:
        """
        if query is None:
            query = {}
        for item in self.col.find(query).sort(sort):
            exclude = ['ZnO_mp-2133', 'K3Sb_mp-14017', 'NiP2_mp-486', 'OsS2_mp-20905', 'PbO_mp-1336', 'Rb3Sb_mp-16319',
                       'As2Os_mp-2455']
            if item['system'] in exclude:
                continue
            if False:
                print('System    : ', item['system'].split('_mp-')[0])
                print('Ps        : ', item['ps'])
                print('extra     : ', item['extra_vars'])
                print('gwresults : ', item['gw_results'])
            try:
                #print('data  : ', item['results_file'])
                data = self.gfs.get(item['results_file']).read()
                if len(data) > 1000:
                    srf = MySigResFile(data)
                    title = "QPState corrections of " + str(item['system']) + "\nusing " + str(item['ps'].split('/')[-2])
                    if item['extra_vars'] is not None:
                        title += ' and ' + str(self.fix_extra(item['extra_vars']))
                    srf.plot_scissor(title=title)
                    srf.print_gap_info()
                    sc = srf.get_scissor()

                    with self.gfs.get(item['ksbands_file']) as f:
                        ksb = MyBandsFile(f.read()).ebands
                    qpb = ksb.apply_scissors(sc)

                    # Plot the LDA and the QPState band structure with matplotlib.
                    plotter = ElectronBandsPlotter()

                    plotter.add_ebands("KS", ksb)

                    plotter.add_ebands("KS+scissors(e)", qpb)

                    # Define the mapping reduced_coordinates -> name of the k-point.
                    #klabels = {
                    #    (0.5,  0.0,  0.0): "L",
                    #    (0.0,  0.0,  0.0): "$\Gamma$",
                    #    (0.0,  0.5,  0.5): "X",
                    #}

                    fig = plotter.plot(align='cbm', ylim=(-5, 10), title="%s Bandstructure" % item['system'].split('_mp-')[0])

                    try:
                        if not item['tgwgap']:
                            bands_data = self.gfs.get(item['ksbands_file'])
                            ks_bands = MyBandsFile(bands_data)
                            item['tkshomo'] = ks_bands.homo
                            item['tkslumo'] = ks_bands.lumo
                            item['tksgap'] = ks_bands.lumo - ks_bands.homo
                            item['tgwhomo'] = ks_bands.homo + sc.apply(ks_bands.homo)
                            item['tgwlumo'] = ks_bands.lumo + sc.apply(ks_bands.lumo)
                            item['tgwgap'] = item['tgwlumo'] - item['tgwhomo']
                            self.col.save(item)
                    except KeyError:
                        pass
            except (KeyError, IOError, NoFile):
                print('No Sigres file in DataBase')
                #dummy = raw_input('next')

        try:
            return fig
        except UnboundLocalError:
            return None

    def fundamental_gaps(self, query=None, sort='system'):
        """
        print the gap info for all the systems in the database
        :param query:
        :param sort: default sort per system
        :return:
        """
        mp_key = os.environ['MP_KEY']
        if query is None:
            query = {}
        for item in self.col.find(query).sort(sort):
            print('')
            print('System    : ', item['system'].split('_')[0])
            print('Ps        : ', item['ps'])
            print('extra     : ', item['extra_vars'])
            print('gwresults : ', item['gw_results'])
            print('item      : ', item['item'])
            if 'mp-' in item['item']:
                try:
                    with MPRester(mp_key) as mp_database:
                        #print 'structure from mp database', item['item']
                        gap = {}
                        bandstructure = mp_database.get_bandstructure_by_material_id(item['item'])
                        gap['vbm_l'] = bandstructure.kpoints[bandstructure.get_vbm()['kpoint_index'][0]].label
                        gap['cbm_l'] = bandstructure.kpoints[bandstructure.get_cbm()['kpoint_index'][0]].label
                        gap['vbm_e'] = bandstructure.get_vbm()['energy']
                        gap['cbm_e'] = bandstructure.get_cbm()['energy']
                        gap['cbm'] = tuple(bandstructure.kpoints[bandstructure.get_cbm()['kpoint_index'][0]].frac_coords)
                        gap['vbm'] = tuple(bandstructure.kpoints[bandstructure.get_vbm()['kpoint_index'][0]].frac_coords)
                except (MPRestError, IndexError, KeyError) as err:
                    print(err.message)
                    gap = None
            else:
                gap = None
            if gap:
                print(gap['cbm_l'], gap['vbm_l'])
                print(gap['cbm'], gap['vbm'])
            try:
                data = self.gfs.get(item['results_file']).read()
                if len(data) > 1000:
                    srf = MySigResFile(data)
                    srf.print_gap_info()
            except IOError:
                print('No Sigres file in DataBase')
                dummy = raw_input('next')
