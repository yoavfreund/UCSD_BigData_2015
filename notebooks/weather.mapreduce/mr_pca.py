#!/usr/bin/python
"""
compute the PCA for each region.
"""
import sys,os
from glob import glob
sys.path.append('./library')
from mrjob.job import MRJob,MRStep
import mrjob.protocol
import pandas as pd
import numpy as np
import Statistics2 as Stat
import pickle
#from ECatch import ECatch
from time import time
V_len=365

log=sys.stderr
log.write('**starting MRpca**\n\n')
log.flush()
Counter=0

class MRpca(MRJob):

    # When using PickleProtocol no extra work is needed, but the pickling is much slower
    # increasing from 0.06sec to 0.25 second. And the serialization is already the slowest part.
    # INTERNAL_PROTOCOL = mrjob.protocol.PickleProtocol

    INTERNAL_PROTOCOL = mrjob.protocol.JSONProtocol
    OUTPUT_PROTOCOL = mrjob.protocol.JSONProtocol
    
    global Counter
    #@ECatch
    def mapper_init(self):
        "read the station partitioning table"
        log.write('current working directory='+os.getcwd() + "\n")
        filenames=glob('*')
        log.write(str(filenames)+'\n')
        log.flush()
        os.system('ls -l')
        file=open('Partition_Tree.pkl','rb')
        Ptree=pickle.load(file)
        file.close()
        T=Ptree['Partitioned_Stations']
        self.Partition=T[['block','Node','weight']]
        self.Counter=0
        self.t_end=time()

    #def mapper(self,_,line):
    #    self.mapper_step(line)

    #@ECatch
    def mapper(self,_, line):
        self.t0=time()
        elements=line.split(',')
        if elements[1]=='TMAX': 
            station=elements[0]
            vec=np.zeros(V_len)
            nulls=0
            for i in range(3,len(elements)):
                if elements[i]=='':
                    vec[i-3]=np.nan
                    nulls+=1
                else:
                    vec[i-3]=int(elements[i])
            if nulls<=65:
                #log.write('mapping line: '+str(self.Counter)+'\n')
                self.Counter+=1
                S=Stat.VecStat(V_len)
                S.accum(vec)
                P_row=self.Partition.loc[station]
                key=P_row['block']
                self.t8=time()
                log.write('Mapper times='+str([self.t0-self.t_end,self.t8-self.t0])+'\n')
                self.t_end=self.t8
                yield(key,S.to_lists())

    def reducer_init(self):
        "initialize VecStat"
        self.VS=Stat.VecStat(V_len)
        self.Counter=0
        
    #@ECatch
    def reducer(self,key,val):
        log.write('start reduce on '+str(key)+'\n')
        try:
            while True:
                U_aslists = next(val)
                U=Stat.VecStat(V_len)
                U.from_lists(U_aslists)
                #U=next(val)
                log.write('reducing Iteration: '+str(self.Counter)+'\n')
                self.Counter+=1
                self.VS.add(U)
        except StopIteration:
            log.write('end reduce on '+str(key)+'\n')
            yield (key,self.VS.to_lists())
            #yield (key,self.VS)

    def steps(self):
        return[
            MRStep(mapper_init=self.mapper_init,
                   mapper=self.mapper,
                   reducer_init=self.reducer_init,
                   reducer=self.reducer,
                   combiner_init=self.reducer_init,
                   combiner=self.reducer)
              ]

if __name__ == '__main__':
    #print 'yey'
    MRpca.run()