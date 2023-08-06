
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
import pandas as pd


class Plot:
    
    def __init__(self):
        pass
        
    def alleles(df,ax=None,show=True,**set_kwargs):
        title = "Change in allelic frequencies"
        ylabel= 'p'
        
        if show==True:
            plt.figure(figsize=(8,4),constrained_layout=True)
            plt.style.use('ggplot')
            
        axes = Plot.axesConfig(df,ax,set_kwargs,
                                title=title,
                                ylabel=ylabel)
        #enseña la figura, que incluye los axis (subplots)
        if show==True:
            plt.show()
        else:
            return plt.gca()
        
    def sex(df,ax=None,show=True, **set_kwargs):
        title = "Change in sex frequencies"
        ylabel = 'freq'
        
        if show==True:
            plt.figure(figsize=(8,4),constrained_layout=True)
            plt.style.use('ggplot')
        axes = Plot.axesConfig(df,ax,
                                title=title,
                                ylabel=ylabel)
        #enseña la figura, que incluye los axis (subplots)
        if show==True:
            plt.show()
        else:
            return plt.gca()
        
    def gametes(df,ax=None,show=True,**set_kwargs):
        title = "Change in gametic frecuencies"
        ylabel = 'f'
        
        if show==True:
            plt.figure(figsize=(8,4),constrained_layout=True)
            plt.style.use('ggplot')
            
        axes = Plot.axesConfig(df,ax,
                                title=title,
                                ylabel=ylabel)
        #enseña la figura, que incluye los axis (subplots)
        if show==True:
            plt.show()
        else:
            return plt.gca()
        
    def mutations(df,ax=None,show=True,**kwargs):
        title ='Number of mutations per loci'
        ylabel = 'mut'
        maxMutLim = int(max(df.sum(axis=1)))
        ylim = [0,maxMutLim+1]
        
        if show==True:
            plt.figure(figsize=(8,4),constrained_layout=True)
            plt.style.use('ggplot')
            
        axes = Plot.axesConfig(df,ax,
                               type='bar',
                               ylim=ylim,
                            title=title,
                            ylabel=ylabel)
        if show==True:
            plt.show()
        else:
            return plt.gca()
        
        
    def axesConfig(df,ax=None,type='plot',**set_kwargs):
        # new_steps = int(len(df.index)/5) if len(df.index)>8 else 1
        # xticks = range(0,len(df.index),new_steps)
        xMajor_ticks = df.index[-1]//5
        xMinor_ticks = df.index[-1]//20
        if ax is None:
            ax = plt.gca()
        if 'legend' not in set_kwargs.keys():
            legend = df.columns
            
        if type=='bar':
            for x,i in enumerate(df.columns):
                bottom = 0
                if x>0:
                    bottom = df.iloc[:,x-1]
                    ax.bar(height=df[i],x=df.index,bottom=bottom)
                else:
                    ax.bar(height=df[i],x=df.index)
        else:
            ax.plot(df)    
            # x ticks
            ax.xaxis.set_minor_locator(MultipleLocator(xMinor_ticks))
        ax.xaxis.set_major_locator(MultipleLocator(xMajor_ticks))
        ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
        # x limit
        ax.set_xlim(0,df.index[-1])
        ax.set_ylim(0,1.05)
        # ax legend,title...
        ax.legend(legend)
        ax.set_xlabel(df.index.name)
        
        ax.set(**set_kwargs)
        
        return(ax)
                   
        
    def multipleData(data=list(),row=2,col=2,**kwargs):

        if (row*col)/2 > len(data):
            col = col/2
        fig,axes= plt.subplots(nrows=row,ncols=col,
                             figsize=(10,6),
                             constrained_layout=True)
        i=0
        with plt.style.context("ggplot"):
            for ax in axes.reshape(-1):
                cus_plot = Plot.axesConfig(data[i],ax)
                i += 1 
        plt.show()
        
