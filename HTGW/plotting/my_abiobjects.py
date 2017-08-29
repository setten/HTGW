from __future__ import print_function, division
from abipy.electrons.gw import SigresFile
from abipy.electrons.gsr import GsrFile
import sys
import os

__author__ = 'setten'
__version__ = "0.1"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "Sept 2014"


# Disable
def block_print():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enable_print():
    sys.stdout = sys.__stdout__


class MyBandsFile(object):
    """
    container for a GSR file with some additional stuff
    """
    def __init__(self, data, silent=False):
        if silent:
            block_print()
        name = 'tmp_GSR.nc'
        f = open(name, 'w')
        f.write(data)
        f.close()
        with GsrFile(filepath=name) as gsr_file:
            self.ebands = gsr_file.ebands
        self.lumo = self.ebands.lumos[0].eig
        self.lumo_kp = self.ebands.lumos[0].kpoint
        self.lumo_i = self.ebands.kindex(self.lumo_kp)
        self.lumo_b = self.ebands.lumos[0].band
        self.lumo_s = self.ebands.lumos[0].spin
        self.homo = self.ebands.homos[0].eig
        self.homo_kp = self.ebands.homos[0].kpoint
        self.homo_i = self.ebands.kindex(self.homo_kp)
        self.homo_b = self.ebands.homos[0].band
        self.homo_s = self.ebands.homos[0].spin
        self.en_max_band = self.ebands.enemax()
        if silent:
            enable_print()


class MySigResFile(object):
    """
    container for a sigres file with some additional stuff ..
    """
    def __init__(self, data, silent=False):
        if silent:
            block_print()
        name = 'tmp_SIGRES.nc'
        f = open(name, 'w')
        f.write(data)
        f.close()
        sigma_file = SigresFile(filepath=name)
        self.ebands = sigma_file.ebands
        self.qplist_spin = sigma_file.qplist_spin
        self.lumo = self.ebands.lumos[0].eig
        self.lumo_kp = self.ebands.lumos[0].kpoint
        self.lumo_i = self.ebands.kindex(self.lumo_kp)
        self.lumo_b = self.ebands.lumos[0].band
        self.lumo_s = self.ebands.lumos[0].spin
        self.homo = self.ebands.homos[0].eig
        self.homo_kp = self.ebands.homos[0].kpoint
        self.homo_i = self.ebands.kindex(self.homo_kp)
        self.homo_b = self.ebands.homos[0].band
        self.homo_s = self.ebands.homos[0].spin
        self.en_max_band = self.ebands.enemax()
        # self.qplist_spin = sigma_file.qplist_spin
        qpe = self.qplist_spin[0].get_field('qpe')
        self.lumo_gw = self.qplist_spin[0].get_value((self.lumo_s, self.lumo_kp, self.lumo_b), 'qpe').real
        self.homo_gw = self.qplist_spin[0].get_value((self.homo_s, self.homo_kp, self.homo_b), 'qpe').real
        self.lumo_gamma_gw = self.qplist_spin[0].get_value((0, 0, self.lumo_b), 'qpe').real
        self.homo_gamma_gw = self.qplist_spin[0].get_value((0, 0, self.homo_b), 'qpe').real
        e0 = self.qplist_spin[0].get_field('e0')
        self.lower = min(min(qpe).real, min(e0)) - 1
        self.upper = max(max(qpe).real, max(e0)) + 1
        self.scissor_residues = self.get_scissor_residues()
        if silent:
            enable_print()
        sigma_file.close()

    def get_scissor(self):
        mid = (self.homo + self.lumo) / 2
        return self.qplist_spin[0].build_scissors(domains=[[-200, mid], [mid, 200]], k=1,
                                                  plot=False)

    def get_scissor_residues(self):
        sc = self.get_scissor()
        return sc.residues

    def plot_scissor(self, title=''):
        mid = (self.homo + self.lumo) / 2
        self.qplist_spin[0].build_scissors(domains=[[self.lower, mid], [mid, self.upper]], k=1, plot=True,
                                           title=title)

    def plot_qpe(self, title=''):
        self.qplist_spin[0].plot_qps_vs_e0(title=title, with_fields="qpe", fermi=self.lumo)

    def print_gap_info(self):
        print('KS LUMO at %s eV at kpoint %s' % (str(self.lumo), str(self.lumo_kp)))
        print('KS HOMO at %s eV at kpoint %s' % (str(self.homo), str(self.homo_kp)))
        print('KS GAP     %s eV' % str(self.lumo - self.homo))
        print('GW LUMO at %s eV at kpoint %s' % (str(self.lumo_gw), str(self.lumo_kp)))
        print('GW HOMO at %s eV at kpoint %s' % (str(self.homo_gw), str(self.homo_kp)))
        print('GW GAP     %s eV' % str(self.lumo_gw - self.homo_gw))
        for i, x in enumerate(self.scissor_residues):
            print('Scissor residue of domain %s: %s' % (i, x))

    def fundamental_gap(self, mode):
        if mode == 'gw':
            return self.lumo_gw - self.homo_gw
        elif mode == 'ks':
            return self.lumo - self.homo
        elif mode == 'gamma':
            return self.lumo_gamma_gw - self.homo_gamma_gw
        else:
            return None
