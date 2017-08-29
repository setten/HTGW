from __future__ import division
from __future__ import print_function, division
import matplotlib.pyplot as plt
from operator import add
from matplotlib import cm
import numpy as np


__author__ = 'setten'
__version__ = "0.1"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "Sept 2014"


colors = ['r', 'g', 'b', 'y', 'm', 'c', 'k', 'k', 'k', 'k', 'k', 'k', 'k', 'k']

labels = {'nbands': "Number of bands",
          'gwgap': "GW gap @ Gamma (eV)",
          'ecuteps': "ecuteps (eV)",
          'gwfgap': "Fundamental GW gap (eV)",
          'ksfgap': "Fundamental KS gap (eV)",
          'gwhomo': "GW HOMO (eV)",
          'kshomo': "KS HOMO (eV)",
          'gwlumo': "GW LUMO (eV)",
          'kslumo': "KS LUMO (eV)",
          'scissor_residues0': "scissor residues (eV)",
          'scissor_residues1': "scissor residues (eV)"}


class MyPlotStyle(object):
    """
    base clase for plots setting visual settings
    """
    @staticmethod
    def set_style(self):
        """
        """


class ConvergenceParameterPlot(MyPlotStyle):
    """
    plot the convergence parameters for all systems x pseudos grouped per system
    to_plot determines what is to be plotted: gwgap, nbands, ecuteps
    """
    def __init__(self, col, to_plot='gwgap', **kwargs):
        plt.xticks(rotation=70)

        silent = kwargs.get('silent', False)

        self.plot = plt
        self.to_plot = to_plot
        self.data_set = col.data_set
        self.xpos = range(0, len(self.data_set))

        self.names = []
        self.data = []

        my_list = []
        for system in col.systems:
            for ps in col.ps:
                for item in self.data_set:
                    if system == item['system'] and ps == item['ps']:
                        my_list.append(item)

        for item in my_list:
            if not silent:
                print(item)
            self.names.append(item['system']+"."+item['ps'].split('-')[-1])
            self.data.append(item['data'][self.to_plot])

        self.plot.bar(self.xpos, self.data)
        self.plot.ylabel(self.to_plot)
        self.plot.xticks(self.xpos, self.names)

    def show(self):
        self.plot.show()
        self.plot.savefig('test', format='eps')


class ConvergenceParameterPlot2(MyPlotStyle):
    """
    plot the convergence parameters for all systems x pseudos grouped per system

    to_plot="gwgap"
    to_plot determines what is to be plotted:
    gwgap, nbands, ecuteps are retreived directly from the entry
    gwfgap, ksfgap, gwhomo, kshomo, gwlumo, kslumo, scissor_residues need to be retrieved from the sigres files.
    this only is done once and at that time stored in the entry.

    q=None
    q is an additional query passed to the method retrieving the data from the database
    todo: store some usefull queries in a atributes of plot

    ymax=None
    ymax can be used to adjust the y-max of the plot to make sure the legend is not covering data
    """
    def __init__(self, col, to_plot='gwgap', **kwargs):
        plt.xticks(rotation=70)

        ymax = kwargs.get('ymax', None)
        name = kwargs.get('name', None)
        silent = kwargs.get('silent', False)

        self.plot = plt
        self.name = name
        if name is not None:
            self.plot.suptitle = name
        self.to_plot = to_plot
        self.data_set = col.data_set
        self.xpos = range(0, len(self.data_set))

        self.names = []
        self.data = {}

        self.ylabels = labels

        self.plot.ylabel(self.ylabels[self.to_plot])
        self.plot.legend()

        n = 0

        my_list = {}
        for ps in col.ps:
            for extra in col.extra:
                x = str(ps) + '.' + str(extra)
                my_list[x] = []
                for system in col.systems:
                    success = False
                    for item in self.data_set:
                        if system == item['system'] and ps == item['ps'] and extra == item['extra']:
                            my_list[x].append(item)
                            success = True
                    if not success:
                        # no entry found matching, add 0 to facilitate plotting
                        if 'scissor' in self.to_plot:
                            my_list[x].append({'system': system, 'ps': ps, 'extra': extra, 'data': {'scissor_residues': [0, 0]}})
                        else:
                            my_list[x].append({'system': system, 'ps': ps, 'extra': extra, 'data': {self.to_plot: 0}})
                if self.test_data(my_list[x]):
                    n += 1  # count the number of non empty data sets to determine the with

        width = 1.0 / (n + 1)

        for item in my_list[str(col.ps[0])+'.'+str(col.extra[0])]:
            self.names.append(item['system'])
        xpos = range(0, len(self.names))
        xpos = map(add, xpos, len(xpos)*[0.45])
        self.plot.xticks(xpos, self.names)

        shift = 0
        c = 0
        l1 = []
        l2 = []
        for ps in col.ps:
            for extra in col.extra:
                x = str(ps) + '.' + str(extra)
                data = []
                for item in my_list[x]:
                    if self.to_plot == 'scissor_residues0':
                        data.append(item['data']['scissor_residues'][0])
                    elif self.to_plot == 'scissor_residues1':
                        data.append(item['data']['scissor_residues'][1])
                    else:
                        data.append(item['data'][self.to_plot])
                xpos = range(0, len(data))
                xpos = map(add, xpos, len(xpos)*[shift])
                if self.test_data(data):  # only add this set of bars if that is actually data in them
                    if not silent:
                        print(c)
                    l1.append(self.plot.bar(xpos, data, width, color=colors[c])[0])
                    l2.append(x)
                    shift += width
                    c += 1

        self.plot.xlim(-width, len(self.names) + width)

        if ymax is not None:
            self.plot.ylim(0, ymax)

        self.plot.legend(l1, l2, bbox_to_anchor=(1.1, 1.3))

    def test_data(self, data):
        check_sum = 0
        for item in data:
            if isinstance(item, dict):
                try:
                    if self.to_plot == 'scissor_residues0':
                        v = item['data']['scissor_residues'][0]
                    elif self.to_plot == 'scissor_residues1':
                        v = item['data']['scissor_residues'][1]
                    else:
                        v = item['data'][self.to_plot]
                except KeyError:
                    v = 0
                check_sum += abs(v)
            else:
                check_sum += abs(item)
        if check_sum > 0:
            return True
        else:
            return False

    def show(self):
        self.plot.subplots_adjust(top=0.77)
        self.plot.show()

    def save(self, ext='png'):
        self.plot.subplots_adjust(top=0.77)
        self.plot.savefig(self.name, ext)


class ScatterPlot(MyPlotStyle):
    """
    plot the convergence parameters for all systems x pseudos grouped per system
    to_plot determines what is to be plotted: gwgap, nbands, ecuteps
    """
    def __init__(self, col, xlabel='ksfgap', ylabel='ecuteps', **kwargs):

        plt.xticks(rotation=70)

        self.plot = plt
        self.data_set = col.data_set
        self.xpos = range(0, len(self.data_set))

        silent = kwargs.get('silent', False)

        x = []
        y = []

        self.names = []
        self.data = []

        for item in self.data_set:
            if not silent:
                print(item)
            x.append(item['data'][xlabel])
            y.append(item['data'][ylabel])

        self.plot.scatter(x, y)
        self.plot.ylabel(labels[ylabel])
        self.plot.xlabel(labels[xlabel])

    def show(self):
        self.plot.show()
        self.plot.savefig('test', format='eps')

    def return_fig_ax(self):
        return (self.fig, self.ax)


class ConvTest(object):
    def __init__(self, title='title',
                 x=7*[-50, 0, 50], y=3*[-75]+3*[-50]+3*[-25]+3*[0]+3*[25]+3*[50]+3*[75], z=[np.random.random(3*7)]):
        """
        takes x,y,z as lists and produces 3d plot
        """
        lx = len(sorted(set(x)))
        ly = len(sorted(set(y)))
        self.plot = plt
        self.fig = self.plot.figure()

        self.x = np.array(x).reshape((lx, ly))
        self.y = np.array(y).reshape((lx, ly))
        self.z = np.array(z).reshape((lx, ly))
        ax = self.fig.gca(projection='3d')
        c = 1  # int((np.max(self.x) - np.min(self.x)) / (lx - 1))
        r = 1  # int((np.max(self.y) - np.min(self.y)) / (ly - 1))
        ax.plot_surface(self.x, self.y, self.z, rstride=r, cstride=c, alpha=0.7, cmap=cm.coolwarm, linewidth=0, antialiased=False)
        ax.contourf(self.x, self.y, self.z, zdir='z', offset=1.2*np.min(self.z) - 0.2*np.max(self.z), cmap=cm.coolwarm)
        ax.contourf(self.x, self.y, self.z, zdir='x', offset=1.2*np.min(self.x) - 0.2*np.max(self.x), cmap=cm.coolwarm)
        ax.contourf(self.x, self.y, self.z, zdir='y', offset=1.2*np.max(self.y) - 0.2*np.min(self.y), cmap=cm.coolwarm)

        self.plot.title(title)
        ax.set_xlabel('Nb')
        ax.set_xlim(1.2*np.min(self.x) - 0.2*np.max(self.x), 1.2*np.max(self.x) - 0.2*np.min(self.x))
        ax.set_ylabel('Ec (eV)')
        ax.set_ylim(1.2*np.min(self.y) - 0.2*np.max(self.y), 1.2*np.max(self.y) - 0.2*np.min(self.y))
        ax.set_zlabel('G-G gap (eV)')
        ax.set_zlim(1.2*np.min(self.z) - 0.2*np.max(self.z), 1.2*np.max(self.z) - 0.2*np.min(self.z))

        self.ax = ax

    def show(self):
        self.plot.show()

    def return_fig_ax(self):
        return (self.fig, self.ax)
