from mrjob.emr import EMRJobRunner
from operator import itemgetter
def find_waiting_flow(aws_access_key_id,aws_secret_access_key,ssh_key_pair_file=''):
    # print (aws_access_key_id,aws_secret_access_key)
    JobRunner = EMRJobRunner(aws_access_key_id=aws_access_key_id,aws_secret_access_key=aws_secret_access_key)
    emr_conn = JobRunner.make_emr_conn()
    job_flows=emr_conn.describe_jobflows()
    job_id='NONE'
    d = {'WAITING':0,'STARTING':1,'RUNNING':2}
    waiting_flows=[]
    index = 1
    for flow in job_flows:
        try:
            if flow.state in d.keys():
                job_id=flow.jobflowid
                ip_address=flow.masterpublicdnsname
                print index, job_id, ip_address, flow.state
                waiting_flows.append([d[flow.state],job_id,ip_address,flow.state])
                index += 1
                if ssh_key_pair_file != '':
                    print 'ssh -i %s hadoop@%s'%(ssh_key_pair_file,ip_address)
                    job_id=flow.jobflowid
        except Exception:
            continue
    sorted(waiting_flows, key=itemgetter(0))
    waiting_flows = [i[1:] for i in waiting_flows] #An index was added at the beginning for the sorting. Removing that index in this step
    waiting_flows_dict = [{'flow_id':i[0],'node':i[1],'flow_state':i[2]} for i in waiting_flows] #Converting a list of lists to a list of dicts
    return waiting_flows_dict

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
