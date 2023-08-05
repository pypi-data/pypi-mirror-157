import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd

def plot_setting(title=None,x_text='',y_text='',
                 fig1=5,fig2=5,labelsize=10):
    plt.figure(figsize=(fig1, fig2))
    ax = plt.subplot(111)
    ax.tick_params(labelsize=labelsize)
    ax.set_ylabel(y_text, fontweight='bold', fontsize=labelsize)
    ax.set_xlabel(x_text, fontweight='bold', fontsize=labelsize)
    if title is not None:
        ax.set_title(title, fontweight='bold', fontsize=labelsize)
    return ax

def plot_savefig(title='output',type='png'):
    plt.savefig(title+'.'+type,bbox_inches='tight',dpi=400)


def plot_density(df:pd.DataFrame):
    sns.kdeplot(df.unstack())


def plot_bar(df:pd.DataFrame,x,height,width=0.6):
    #TODO: better style need to set
    plt.bar(x=x,height=height,data=df,width=width)


def plot_donut(df:pd.DataFrame,label,value,colors=None):
    if colors is None:
        colors=['#fbb4ae','#b3cde3','#ccebc5','#decbe4',\
        '#fed9a6','#ffffcc','#e5d8bd','#fddaec']
    patches = [mpatches.Patch(color=colors[i], \
        label="{:s}".format(df[label][i])) for i in range(len(colors))]
    plt.pie(df[value],radius=1,autopct='%.1f%%',\
        colors=colors,pctdistance=0.85)
    plt.pie([1],radius=0.7,colors='white')
    plt.legend(handles=patches,frameon=False,bbox_to_anchor=(0.5,0.1,1,1))

