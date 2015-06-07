"""
A module for computing simple statistics - mean, variance, covariance
s1: First order Statistics for a matrix random variable (a numpy array)
s2: Second order Statistics for a vector random variable.
"""
from numpy import *
import numpy as np
from random import random
import sys,copy,traceback

class s:
    """ compute the mean of matrices (have to be of same size) """
    def __init__(self,mat):
        self.reset(mat)
        
    def reset(self,mat):
        self.n=zeros(shape(mat))
        self.sum=zeros(shape(mat))
        
    def accum(self,value):
        """ Add a value to the statistics """

        if type(value)!= ndarray:
            raise Exception('in s.accum: type of value='+str(type(U))+', it should be numpy.ndarray')
 
        if shape(value) != shape(self.sum):
            raise Exception('in s.accum: shape of value:'+str(shape(value))+\
                            ' is not equal to shape of sum:'+str(shape(self.sum)))
        self.sum+=nan_to_num(value)
        self.n+=(1-isnan(value))

    def compute(self):
        """ Returns the counts and the means for each entry """
        self.mean = self.sum / self.n
        self.mean = nan_to_num(self.mean)
        self.count=nan_to_num(self.n)
        return (self.count,self.mean)

    def add(self,other):
        """ add two statistics """
        self.n += other.n
        self.sum += other.sum
        
    def to_lists(self):
        return {'n':self.n.tolist(),\
                'sum':self.sum.tolist()}

    def from_lists(self,D):
        self.n=array(D['n'])
        self.sum=array(D['sum'])

class VecStat:
    """ Compute first and second order statistics of vectors of a fixed size n """
    def __init__(self,n):
        self.n=n
        self.reset()
        # Create a vector of length n and a matrix of size nXn
 
    def reset(self):
        n=self.n
        self.V=s(zeros(n))
        self.Cov=s(zeros([n,n]))
        
    def accum(self,U):
        """ accumulate statistics:
        U: an numpy array holding one vector
        """
        #check the length of U
        if len(U) != self.n :
            error='in Statistics.secOrdStat.accum: length of V='+str(self.n)+' not equal to length of U='+str(U.n)+'/n'
            sys.stderr.write(error)
            raise StandardError, error
        #check if U has the correct type
        if type(U) != ndarray:
            error='in Statistics.secOrdStat.accum: type of U='+str(type(U))+', it should be numpy.ndarray'
            sys.stderr.write(error)
            raise StandardError, error
        else:
            #do the work
            self.V.accum(U)
            self.Cov.accum(outer(U,U))
            
    def compute(self,k=5):
        """
        Compute the statistics. k (default 5) is the number of eigenvalues that are kept
        """

        # Compute mean vector
        (countV,meanV)=self.V.compute()

        # Compute covariance matrix
        (countC,meanC)=self.Cov.compute()
        cov=meanC-outer(meanV,meanV)
        std=[cov[i,i] for i in range(shape(self.Cov.sum)[0])]
        try:
            (eigvalues,eigvectors)=linalg.eig(cov)
            order=argsort(-abs(eigvalues))	# indexes of eigenvalues from largest to smallest
            eigvalues=eigvalues[order]		# order eigenvalues
            eigvectors=eigvectors[order]	# order eigenvectors
            eigvectors=eigvectors[0:k]		# keep only top k eigen-vectors
            for v in eigvectors:
                v=v[order]     # order the elements in each eigenvector

        except Exception,e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,limit=2, file=sys.stderr)
            
            eigvalues=None
            eigvectors=None
        return {'count':self.V.n,'mean':meanV,'std':std,'eigvalues':eigvalues,'eigvectors':eigvectors}
        
    def add(self, other):
        """ add the statistics of s into self """
        self.V.add(other.V)
        self.Cov.add(other.Cov)
        
    def to_lists(self):
        return {'V':self.V.to_lists(),
                'Cov':self.Cov.to_lists()}

    def from_lists(self,D):
        self.V.from_lists(D['V'])
        self.Cov.from_lists(D['Cov'])
        self.n=len(self.V.sum)


if __name__ == "__main__":
    ## Test code ##
    vec1=array([0,nan,1,0,nan])
    vec2=array([1,2,1,1,nan])
    print 'vec1=\n',vec1,'\n vec2=\n',vec2

    S1=s(vec1)
    S1.accum(vec1)
    S1.accum(vec2)
    count,mean=S1.compute()
    print 'First order statistics'
    print 'count=\n',count,'\nmean=\n',mean

    S2=VecStat(len(vec1))
    S2.accum(vec1)
    S2.accum(vec2)
    EigenDecomp=S2.compute()
    print 'second order statistics'
    print EigenDecomp
    
