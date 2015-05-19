from mrjob.emr import EMRJobRunner
def find_waiting_flow(aws_access_key_id,aws_secret_access_key,ssh_key_pair_file=''):
    # print (aws_access_key_id,aws_secret_access_key)
    JobRunner = EMRJobRunner(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    emr_conn = JobRunner.make_emr_conn()
    job_flows=emr_conn.describe_jobflows()
    job_id='NONE'
    waiting_flows=[]
    for flow in job_flows:
        try:
            if flow.state=='WAITING':
                waiting_flows.append(flow)
                print flow.jobflowid,flow.state
                job_id=flow.jobflowid
                ip_address=flow.masterpublicdnsname
                if ssh_key_pair_file != '':
                    print 'ssh -i %s hadoop@%s'%(ssh_key_pair_file,ip_address)
                    job_id=flow.jobflowid
        except Exception:
            continue
    return job_id,waiting_flows

if __name__=='__main__':
    import os,sys, pickle
    dir=os.environ['EC2_VAULT']
    Creds=pickle.load(open(dir+'/Creds.pkl','rb'))
    if 'admin' in Creds.keys():
        creds_used=Creds['admin']
        key_id=creds_used['key_id']
        secret_key=creds_used['secret_key']
        ssh_key_name=creds_used['ssh_key_name']
        ssh_key_pair_file=creds_used['ssh_key_pair_file']
        print 'ssh_key_pair_file=',ssh_key_pair_file
        job_id=find_waiting_flow(key_id,secret_key,ssh_key_pair_file=ssh_key_pair_file)
