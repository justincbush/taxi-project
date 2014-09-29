# figures.py

# Makes figures using matplotlib and pandas for display on website. In particular
# boxplots for showing distributions of trip times.

import matplotlib
matplotlib.use("Agg")           # prevents python rocketship
import matplotlib.pyplot as plt

def multi_boxplot(quantiles_list,quantile_labels):

    fig, ax = plt.subplots(figsize=(.5*len(quantiles_list)+1,6))

    ax.boxplot(quantiles_list, widths=.5)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    ax.yaxis.set_label_text('Trip time in minutes', size=8)
    ax.yaxis.set_tick_params(labelsize=8)

    max_value = max([max(elt) for elt in quantiles_list])
    upper_bound = int(max(max_value*4/3,max_value+2))

    plt.yticks(range(0,upper_bound,max(upper_bound/7,1)))
    plt.tight_layout()
    ax.xaxis.set_ticklabels(quantile_labels)
    ax.xaxis.set_tick_params(labelsize=8)
    
    return fig