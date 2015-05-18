import os,sys,re
cmd='s3cmd ls s3://mas-dse-emr/log/j-YB3C47JV0NTK/ -r'

f=os.popen(cmd)

i=0
for line in f.readlines():

    R=re.split('\s+',line)
    print i,R
    i+=1
    if i>10:
        break

print i
