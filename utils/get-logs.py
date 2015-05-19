import os,sys,re

# Look for all of the job-flows
log_dir='s3://mas-dse-emr/log/'
cmd='s3cmd ls '+log_dir

flows=[]
Split_flowname=re.compile(log_dir+'([^/]+)/')
f=os.popen(cmd)
for line in f.readlines():
    Match=Split_flowname.search(line);
    print line,
    if Match:
        flows.append(Match.group(1))
    else:
        print 'No Match'
f.close()

print flows

for flow in flows:
    cmd='s3cmd ls s3://mas-dse-emr/log/'+flow+'/steps/ -r'

    f=os.popen(cmd)

    splitter=re.compile('(\d{4}-\d{2}-\d+)\s+(\d+:\d+)\s+(\d+)\s+(\S+)')
    i=0
    for line in f.readlines():
        Match=splitter.search(line)
        if Match:
            (date,time,size,filename)=Match.groups()
            
        else:
            print 20*'-',i,'No Match',line
        i+=1
        #if i>0:
        #    break

    f.close()
