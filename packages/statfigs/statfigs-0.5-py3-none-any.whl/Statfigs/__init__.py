#Import libraries for the below code
import numpy as np
import pandas as pd #datafram functions
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind #ttest functions

#2 bars graph but only a t-test for between groups within 1 paramaters
def bar_upttest(df, para, grp, title, ymax):
    #Statistics: mean, sem, count (msc)
    msc = df.groupby([grp])[para].agg(['mean','sem','count']) #mean,sem,count calculation
    msc.reset_index(inplace=True) #converts any columns in index as columns
    pd.DataFrame(msc)

    #Statistics: t.test two tailed unpaired
    l1 = df[grp].unique() #retrieve subgroups name
    cat1 = df[df[para]==l1[0]] #subgroup 1 RAW values
    cat2 = df[df[para]== l1[1]] #subgroup 2 RAW values
    results = ttest_ind(cat1[para], cat2[para]) #ttest function
    pval = results[1] #retain for significance annotations for graph
    pd.read_excel(results)

    #Bar Graph: Numerical Information for graphs
    y1, yerr1 = msc['mean'].to_numpy(), msc['sem'].to_numpy()
    x1=np.arange(len(y1)) #Number of non-zero y-values for the number of x-positions
    
    #Bar Graph: Create
    fig, ax = plt.subplots(1,1); ax.bar(x1, y1) #create bar graph
    ax.errorbar(x1, y1, yerr=yerr1,fmt=' ', capsize=(3),zorder=0, ecolor='k')
    ax.spines['right'].set_visible(False); ax.spines['top'].set_visible(False) #Remove top & right graph lines
    ax.set_xticks(x1); ax.set_xticklabels(l1) #x-axis configs
    ax.set_title(title) #tital of graph
    ax.set_ylabel(para.replace('_','')); ax.set_ylim(top=ymax) #y-label but remove '_' and ymax

    #save prior to significance incase no significance
    fig.set_size_inches(4.3, 5)
    fig.savefig(para+'_'+grp+'_JR.png',dpi=200)

    #Significance lines on graph then save
    if pval <= 0.0001:
          text = '****'
    elif pval <= 0.001:
      text='***'
    elif pval <=0.01:
       text='**'
    elif pval <= 0.05:
        text='*'
    else:
        text=''
        return
    x = (x1[0]+x1[1])/2
    y = 1.1*max(y1[0],y1[1])
    props = {'connectionstyle':'bar','arrowstyle':'-','shrinkA':20,'shrinkB':20,'linewidth':2}
    ax.annotate(text,xy=(x,y+0.8),zorder=10,ha='center',fontsize=15)
    ax.annotate('',xy=(x1[0],y),xytext=(x1[1],y),arrowprops=props,ha='center',fontsize=15)
    fig.set_size_inches(4.3,5)
    fig.savefig(para+'_'+grp+'_JR.png',dpi=300)