from calendar import c
import numpy as np
import random
from random import randint

#local import
from .functions import outer_product

class Individual():


    def __init__(self,nom='1',ploidy=2,
                 freq={'A':(0.4,0.6),'B':(0.6,0.4)},
                 d=0,R=0.5,mu=(0.1,0.1),
                 sex_system='XY',gen=0,
                 parents=0):
        '''
        Creates an individual based on population characteristics.
        
        Parameters:
            size (int): population size
            ploidy (int): number of homologous chromosomes. Defaults to 2.
            d (float): Linkage desequilibrium. Defaults to 0.
            R (float): recombination frequency. Defaults to 0.5.
            mu (tuple): mutation rate. Defaults to (0.1,0.1).
            sex_system (str): Sex system. Defaults to 'XY'.
            gen (int): current generation. Defaults to 0.
            parents (tuple,int): individual parents. Defaults to 0 (no parents).
            
        '''
        
        #population attributes
        self.spPloidy = ploidy
        self.d = d
        self.R = R
        self.mu = mu
        self.alFreq = freq
        
        #individual attributes
        self.ide = 'g'+str(gen)+".ID-"+str(nom)
        self.age = 0
        self.parents = parents
        self.sex_system = sex_system
        
        self.__createIndividual()
        

        
    def __createIndividual(self):
        '''
        Initialize variables that are not passed to the initializer
        '''
        self.chromosome = dict()
        self.isMutated = 0
        # si tiene padres, es decir, no esta iniciada de 0...
        if self.parents:
            # self.mating()
            self.mating()
            self.isMutated = self.mutation()
        else:
            self.sex_chromosome = self.generate_sexual_genotype()
            self.chromosome = self.chooseGametes()
            self.gameticFreq()
            
        self.sex = self.getSex()
        self.genotype = self.getGenotype()

            
    def generate_sexual_genotype(self):
        '''Generates a sexual genotype, composed of two corresponding values
        to each of the chromosomes, stores them in the variable sex_chromosome
        
        returns:
            str: sex chromosome for the individual'''
        # sex_chromosome= 'XX'or'XY' / 'ZW' or 'ZZ' / 'XO' or 'XX'
        if randint(0,1)==0:
            return self.sex_system[0]+self.sex_system[0]
        else:
            return self.sex_system
        
    def getSex(self):
        '''Returns sex for given sexual chromosome. 
        
        Returns:
            str: sex (Male/Female)
            '''
            
        if self.sex_chromosome[0] == self.sex_chromosome[1]:
            sexo = 'Female' if self.sex_system != 'ZW' else 'Male'
        else:
            sexo = 'Male'  if self.sex_system != 'ZW' else 'Female'
        return sexo
        
    def getGenotype(self):
        '''Obtain the genotype of the individual
        Returns:
            dict(str:str): genotype of the individual'''
        
        c = [list(self.chromosome[x]) for x in self.chromosome]
        array = np.array(c)
        genotype = [''.join(array[:,i]) for i in range(array.shape[1])]
        
        gen_sorted = [''.join(sorted(g)) for g in genotype]
        
        return gen_sorted

    # Calcula la frecuencia gametica a partir de las frecuencias alelicas y D
    # esto quiza deberia estar en population !!!revisar
    def gameticFreq(self):

        f = self.alFreq
        d = self.d
        fGametes = dict()
        
        #producto externo (outer product)
        freqValues = list(f.values())
        inp = freqValues[0]
        finalDict = dict()
        if len(freqValues)>1:
            fGametes = outer_product(f)
        else:
            word = str(list(f.keys())[0])
            keys = [word,word.lower()]
            
            values = list(freqValues[0])  
                 
            fGametes = dict(zip(keys,values))

        return fGametes

    # Elige un gameto segun su probabilidad (frecuencia)
    def chooseGametes(self):
        """Choose a gamete from gameticFreq keys
        by its given probability in gameticFreq values

        Returns:
           dict(str:str): two chromosomes and its genotype
        """
        chrom = dict()
        fGametes = self.gameticFreq()
        
        gameto =list(fGametes.keys())
        pesos = list(fGametes.values())
        
        for i in range(1,self.spPloidy+1):
            
            chrom['c'+str(i)]= ''.join(random.choices(gameto,
                                            weights=pesos,k=1))

        # self.chromosome = chrom
        return chrom

    
    # metodo dunder
    def __str__(self):
        ind_info = {'Individual id:': self.ide,
                    'sex': self.sex, 
                    'genotype': ' '.join(self.genotype)}
        if self.parents != 0:
            ind_info['suffered mutation']= False if not self.isMutated else self.isMutated
            
        return ('\n'.join(f'{key}: {value}' for key,value in ind_info.items()))
    
    def printParents(self,):
        '''
        Print individual parents
        '''
        
        print(f'''su padre es {self.parents[0].ide}, 
        con genotipo {self.parents[0].chromosome}\n su madre es {self.parents[1].ide}
        con genotipo {self.parents[1].chromosome}''')

    # calculates
    def mating(self):
        ''' Calculates the mating of the individual: parent recombination,
        sexual chromosomes and gametes.'''
        # print(self.chromosome,len(self.chromosome))
        if self.spPloidy > 1:
            r = self.R
            for x in range(len(self.parents)):
                # autosomas
                c1P = self.parents[x].chromosome['c1']
                c2P = self.parents[x].chromosome['c2']
                # metodo de recombinacion
                c1,c2 = Individual.recombination(c1P,c2P,r)              
                self.chromosome['c'+str(x+1)] = random.choice([c1,c2])   
            # cromosomas sexuales sex_chromosome: str XX/XY or ZW/ZZ or XX/X0
            sP = self.parents[0].sex_chromosome
            sM = self.parents[1].sex_chromosome
            self.sex_chromosome = ''.join(sorted([random.choice(sP),random.choice(sM)]))
        else:  
            self.chromosome = {'c'+str(k+1):v for k in range(2) for v in random.choice(self.parents[k].chromosome.values())}

    def recombination(c1,c2,r):
        '''Recombination of two chromosomes by r value.
        If r=0, the chromosomes are not recombined.'''
            # factor de interferencia
            # para que sea menos probable la recombinacion de dos loci seguidos
        int = 0
        c1 = list(c1)
        c2 = list(c2)
        c1R,c2R = c1.copy(),c2.copy()
        for i in range(0,len(c1)):
            if random.random()<=r-int:
                # ocurre la recombinacion (solo recombinan los loci A B )
                c1R = c1
                c2R = c2
                c1R[i] = c2[i]
                c2R[i] = c1[i]
                int = r/2
                
            else:
                int = 0      
        return ''.join(c1R),''.join(c2R)
            
    
    def mutation(self):
        '''
        It causes the change from the major to the minor allele with a mut frequency.
        '''
        muType = 'unidirectional'
        muLoci = list()
        if sum(self.mu) != 0:      
            for k,v in self.chromosome.items():
                for i in range(len(v)):
                    #comprueba si es el alelo mayor
                    if v[i].isupper():
                        #si muta, cambia el alelo del cromosoma por el alelo menor
                        if random.random() < self.mu[i]:
                            self.chromosome[k] = self.chromosome[k].replace(v[i],v[i].lower())
                            muLoci.append(v[i])
        
        return muLoci
                    

            

