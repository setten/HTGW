from __future__ import print_function, division

__author__ = 'setten'

import os
import pandas as pd
import matplotlib.pyplot as plt


def hist(my_df):
    my_df.hist()
    plt.show()


def xy(my_df):
    my_df.plot(kind='scatter', x='a', y='b')
    plt.show()


def make_plot(my_df, plot_type):
    plots = {'hist': hist, 'xy': xy}
    if os.fork():
        pass
    else:
        plots[plot_type](my_df)


test = [{'a': 2, 'b': 3}, {'a': 2, 'b': 4}, {'a': 2, 'b': 5}, {'a': 2, 'b': 6}]

df = pd.DataFrame(test)

print(df.describe())

make_plot(df, 'hist')
make_plot(df, 'xy')
make_plot(df, 'hist')

print(df.describe())

