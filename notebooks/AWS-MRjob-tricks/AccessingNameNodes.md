### Accessing namenodes and files from hdfs ###

The ALL.csv file is unzipped in the hdfs folder that you are pussposed to directly use. 
the following the the code below that you can use to access the same

```python
#code to find the namenode 
`from mrjob.emr import EMRJobRunner
def find_all_flows(aws_access_key_id,aws_secret_access_key):
JobRunner = EMRJobRunner(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
print 'got job runner'
emr_conn = JobRunner.make_emr_conn()
print 'made EMR connection'
return emr_conn.describe_jobflows()

from find_waiting_flow import *
flow_id = find_waiting_flow(key_id,secret_key)
node = ''
job_flows=find_all_flows(key_id,secret_key)
for job in job_flows:
if job.jobflowid == flow_id:
node = job.masterpublicdnsname
print flow_id
print node

input_file = 'hdfs://'+node+':9000/mas-dse-public/ALL.csv'
``` 
!python mr_word_freq_count.py -r emr $input_file --emr-job-flow-id=$flow_id --output-dir=$output_dir  > counts_emr.txt
 
Just take care of indentations.
