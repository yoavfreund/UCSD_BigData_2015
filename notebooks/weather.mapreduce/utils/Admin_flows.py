from mrjob.emr import EMRJobRunner
def find_all_flows(aws_access_key_id,aws_secret_access_key):
    JobRunner = EMRJobRunner(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    print 'got job runner'
    emr_conn = JobRunner.make_emr_conn()
    print 'made EMR connection'
    return emr_conn.describe_jobflows()

import os,sys, pickle
dir=os.environ['EC2_VAULT']
Creds=pickle.load(open(dir+'/Creds.pkl','rb'))
job_flows=find_all_flows(Creds['admin']['key_id'],\
                         Creds['admin']['secret_key'])
for flow in job_flows:
    if flow.state in ['RUNNING','WAITING','STARTING']:
        print flow,flow.name,flow.jobflowid,flow.state

