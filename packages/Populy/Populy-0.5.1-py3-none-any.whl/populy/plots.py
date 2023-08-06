
import matplotlib.pyplot as plt
import pandas as pd

#local imports

from .population import Population
from .superpop import Superpop


class Plots:
    
    def __init__(self):
        pass
    
    def __populationInfo(pop):
        try:
            labels = ['gen.'+str(x) for x in range(0,pop.gen+1,pop.steps)]
        except e as e:
            print(e)
            
        caption=f"""Caracteristicas iniciales: frecuencia gametica={pop.freq}, R={pop.R}
        frecuencia de mutación={pop.mu}"""
        
        return labels, caption
        
    def alleles(pop):
        '''
        Metodo estatico que recibe un dataframe y lo representa
        graficamente
        '''
        labels,caption = Plots.__populationInfo(pop)
        alleles = pop.getDataFrame('alelos')      
        plt.style.use('ggplot')
        plt.figure(figsize=(6,4),constrained_layout=True)
        plt.title("Change in allelic frequencies")
        plt.xlabel("Generations")
        plt.ylabel("p")
        plt.ylim([0,1])
        plt.plot(alleles)  
        plt.legend(alleles.columns)
        plt.xticks(rotation=45)
        plt.show()
    
        
    def gametes(pop):
        labels,caption = Plots.__populationInfo(pop)
        gametes = pop.getDataFrame('gametos')
        
        plt.style.use('ggplot')
        plt.figure(figsize=(6,4),constrained_layout=True)
        plt.title("Change in gametic frequencies")
        plt.xlabel("Generations")
        plt.ylabel("p")
        plt.ylim([0,1])
        plt.plot(gametes)
        plt.legend(gametes.columns)
        plt.xticks(rotation=45)
        plt.show()
        
    def sex(pop):
        labels,caption = Plots.__populationInfo(pop)
        sex = pop.getDataFrame('sex')
        
        plt.style.use('ggplot')
        plt.figure(figsize=(6,4),constrained_layout=True)
        plt.title("Change in sex frequencies")
        plt.xlabel("Generations")
        plt.ylabel("Frequency")
        plt.ylim([0,1])
        plt.plot(sex)
        plt.legend(sex.columns)
        plt.xticks(rotation=45)
        plt.show()
        
    def mutations(pop):
        labels, caption = Plots.__populationInfo(pop)
        mut = pop.getDataFrame('mutantes')
        
        plt.style.use('ggplot')
        plt.figure(figsize=(6,4),constrained_layout=True)
        plt.title("Number of total mutations per generation")
        plt.xlabel("Generations")
        plt.ylabel("Mutants")
        plt.plot(mut)
        plt.legend(mut.columns)
        plt.xticks(rotation=45)
        plt.show()