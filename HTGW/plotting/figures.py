from __future__ import print_function, division

__author__ = 'setten'
__version__ = "0.1"
__maintainer__ = "Michiel van Setten"
__email__ = "mjvansetten@gmail.com"
__date__ = "Sept 2014"

from GWplotting.collection import Collection
from GWplotting.plots import ConvergenceParameterPlot, ConvergenceParameterPlot2, ScatterPlot
import copy

# mostly done in the KS set
l1 = ['mp-149', 'mp-2534', 'mp-8062', 'mp-2469', 'mp-1550', 'mp-830', 'mp-10695', 'mp-66']

figures = [{'name': 'figgaps', 'caption': "Plot of the G-G gaps of all systems and all properties.", 'ymax': 25},
           {'name': 'gw160-ecutepsvsksg', 'caption': "Plot of the ecuteps vs KS gap (GW160).", 'to_plot': ['ksfgap', 'ecuteps'], 't': 3, 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-gwvsksgap', 'caption': "Plot of the GW vs KS gaps (GW160).", 'to_plot': ['ksfgap', 'gwfgap'], 't': 3, 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-ecutepsvsnband', 'caption': "Plot of the ecuteps vs nband (GW160).", 'to_plot': ['ecuteps','nbands'], 't': 3, 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-figgaps', 'caption': "Plot of the G-G gaps of all GW160 systems.", 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-figfgaps'  , 'caption': "Plot of GW gaps of all GW160 systems.", 'to_plot': 'gwfgap', 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-fignb'  , 'caption': "Plot of the nbands of all GW160 systems.", 'to_plot': 'nbands', 'q': {'spec.source': 'mar_exp'}},
           {'name': 'gw160-figecut', 'caption': "Plot of the ecuteps of all GW160 systems.", 'to_plot': 'ecuteps', 'q': {'spec.source': 'mar_exp'}},
           {'name': 'figgaps_part', 'ymax': 9, 'caption': "Plot of the G-G gaps of the mostly done systems of the KS set", 'q': {'item': {"$in": l1}}},
           {'name': 'fignbgaps_part', 'ymax': 370, 'to_plot': 'nbands', 'caption': "Plot of the needed NBAND of the mostly done systems of the KS set", 'q': {'item': {"$in": l1}}},
           {'name': 'figecgaps_part', 'ymax': 550, 'to_plot': 'ecuteps', 'caption': "Plot of the needed ECUTEPS of the mostly done systems of the KS set", 'q': {'item': {"$in": l1}}},
           {'name': 'figfgaps_oncvpsp', 'caption': "Plot of the fundamental gaps of the mostly done systems of the KS set ONCVPSP only", 'q': {'item': {"$in": l1}}, 'to_plot': 'gwfgap', 'exclude': ['GGA_PBE_FHI-nc', 'GGA_PBE-JTH-paw']},
           {'name': 'figfgaps_part', 'ymax': 8, 'caption': "Plot of the fundamental gaps of the mostly done systems of the KS set.", 'q': {'item': {"$in": l1}}, 'to_plot': 'gwfgap', 'exclude': ['GGA_PBE-ONCVPSP-v1-nc']}]


def plot_help():
    print(ConvergenceParameterPlot2.__doc__)


def figure_help():
    for i, f in enumerate(figures):
        print("Figure %s:\n%s\n" % (i, f['caption']))


def plot(silent=False, to_plot='gwgap', t=2, q=None, ymax=None, exclude=None, name=None, save=False):
    my_col = Collection()
    add_sigres_data = False if to_plot in ['gwgap', 'nbands', 'ecuteps'] else True
    my_col.get_data_set(query=q, sigresdata=add_sigres_data)
    my_col.get_property_lists(query=q, exclude=exclude)
    #my_col.property_lists()
    if not silent:
        print(t)
    if t == 1:
        my_plot = ConvergenceParameterPlot(my_col, silent=silent, to_plot=to_plot)
    elif t == 2:
        my_plot = ConvergenceParameterPlot2(my_col, silent=silent, to_plot=to_plot, ymax=ymax, name=name)
    elif t == 3:
        my_plot = ScatterPlot(my_col, silent=silent, xlabel=to_plot[0], ylabel=to_plot[1])
    else:
        print('t = ', t, ' is not defined, only 1 or 2')
        return
    if save:
        my_plot.save()
    else:
        my_plot.show()


def figure(n, save=False, silent=True):
    options = {'q': None, 'ymax': None, 'to_plot': 'gwgap', 'exclude': None, 'name': None, 't': 2}
    options.update(figures[n])
    print(options['caption'])
    if save:
        plot(silent=silent, to_plot=options['to_plot'], q=options['q'], ymax=options['ymax'], exclude=options['exclude'], name=options['name'], t=options['t'], save=save)
    else:
        plot(silent=silent, to_plot=options['to_plot'], q=options['q'], ymax=options['ymax'], exclude=options['exclude'], name=options['name'], t=options['t'])


def game():
    m = []
    n = 0
    l = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i1 in l:
        l2 = copy.copy(l)
        l2.remove(i1)
        for i2 in l2:
            l3 = copy.copy(l2)
            l3.remove(i2)
            for i3 in l3:
                l4 = copy.copy(l3)
                l4.remove(i3)
                for i4 in l4:
                    l5 = copy.copy(l4)
                    l5.remove(i4)
                    for i5 in l5:
                        l6 = copy.copy(l5)
                        l6.remove(i5)
                        for i6 in l6:
                            x = i3 + i6 + 10*(i2 + i5) + 100*(i1+i4)
                            if x > 1000:
                                break
                            i7 = int(str(x)[-3])
                            i8 = int(str(x)[-2])
                            i9 = int(str(x)[-1])
                            if i7*i8*i9 == 0:
                                break
                            s = set([i1, i2, i3, i4, i5, i6, i7, i8, i9])
                            if len(s) == 9 and x < 1000:
                                print(' ')
                                print(i1, i2, i3)
                                print(i4, i5, i6, i1+i2+i3+i4+i5+i6)
                                print('-----')
                                print(i7, i8, i9, i7+i8+i9)
                                q = x / 9
                                m.append(x)
                                n += 1
    print(n)
    print(sorted(m))