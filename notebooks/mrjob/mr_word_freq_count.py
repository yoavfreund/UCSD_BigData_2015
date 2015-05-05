#!/usr/bin/python
# Copyright 2009-2010 Yelp
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The classic MapReduce job: count the frequency of words.
"""
from mrjob.job import MRJob
from mrjob.step import MRStep
import re
from sys import stderr

WORD_RE = re.compile(r"[\w']+")
Large=10000000  # maximal number of occurances of a single word.

logfile=open('logFile','w')
#logfile=stderr

class MRWordFreqCount(MRJob):

    def mapper1(self, _, line):
        for word in WORD_RE.findall(line):
            logfile.write('mapper '+word.lower()+'\n')
            yield (word.lower(), 1)

    def reducer1(self, word, counts):
        #yield (word, sum(counts))
        l_counts=[c for c in counts]  # extract list from iterator
        S=sum(l_counts)
        logfile.write('reducer '+word+' ['+','.join([str(c) for c in l_counts])+']='+str(S)+'\n')
        yield (word, S)
        
    def mapper2(self,word,count):
        logfile.write('mapper2 '+word+': '+str(count)+'\n')
        yield('%010d'%count,word) # add leading zeros so that lexical sorting is the same as numerical
        
    def reducer2(self,count,word):
        wlist=[w for w in word]
        logfile.write('reducer2 '+count+': '+wlist[0]+'\n')
        yield(count,wlist)
        
    def steps(self):
        return [
            MRStep(mapper=self.mapper1,
                   reducer=self.reducer1),
            MRStep(mapper=self.mapper2,
                   reducer=self.reducer2)
        ]



if __name__ == '__main__':
    MRWordFreqCount.run()