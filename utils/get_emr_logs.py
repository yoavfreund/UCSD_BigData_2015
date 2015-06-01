#!/usr/bin/env python

import os
import sys
import pickle
from os.path import expanduser
import dateutil.parser
from dateutil import tz
from boto.emr.connection import EmrConnection
from boto.s3.connection import S3Connection


def read_credentials():
    # If the EC2_VAULT environ var is set then use it, otherwise default to ~/Vault/
    try:
        os.environ['EC2_VAULT']
    except KeyError:
        vault = expanduser("~") + '/Vault'
    else:
        vault = os.environ['EC2_VAULT']

    # Exit if no vault directory is found
    if not os.path.isdir(vault):
        sys.exit("Vault directory not found.")

    # Read credentials from vault/Creds.pkl
    try:
        p_credentials_path = vault + '/Creds.pkl'
        p_credentials_file = open(p_credentials_path)
        p = pickle.load(p_credentials_file)
        credentials = p['mrjob']
    except Exception, e:
        print e
        sys.exit("Could not read %s/Creds.pkl" % vault)

    for c in credentials:
        if c == "key_id":
            p_aws_access_key_id = credentials['key_id']
        elif c == "secret_key":
            p_aws_secret_access_key = credentials['secret_key']

    # These credentials are required to be set before proceeding
    try:
        p_aws_access_key_id
        p_aws_secret_access_key
    except NameError, e:
        sys.exit("Not all of the credentials were defined: %s" % e)

    return p_aws_access_key_id, p_aws_secret_access_key


if __name__ == "__main__":
    aws_access_key_id, aws_secret_access_key = read_credentials()

    emr_conn = EmrConnection(aws_access_key_id, aws_secret_access_key)

    # List EMR Clusters
    clusters = emr_conn.list_clusters(cluster_states=["RUNNING", "WAITING"])

    for index, cluster in enumerate(clusters.clusters):
        print "[%s] %s" % (index, cluster.id)

    selected_cluster = input("Select a Cluster: ")

    cluster_id = clusters.clusters[int(selected_cluster)].id
    print cluster_id

    # List EMR Steps
    steps = emr_conn.list_steps(clusters.clusters[int(selected_cluster)].id)
    step_cnt = 0
    for index, step in enumerate(steps.steps):
        time = dateutil.parser.parse(step.status.timeline.creationdatetime).astimezone(tz.tzlocal())
        print "[%s] NAME: %s - STATE: %s - START TIME: %s" % (index, step.name, step.status.state,
                                                              time.strftime("%Y-%m-%d %H:%M"))
        step_cnt += 1

    selected_step = input("Select a Step: ")

    step_id = steps.steps[int(selected_step)].id
    print step_id

    # Connect to S3
    s3_conn = S3Connection(aws_access_key_id, aws_secret_access_key)

    steps_path = "log/%s/steps/%s" % (cluster_id, step_id)
    task_path = "log/%s/task-attempts" % cluster_id
    task_index = step_cnt - int(selected_step)
    print task_index

    bucket_name_list = ["mas-dse-emr", "cse255-emr"]

    for bucket_name in bucket_name_list:
        try:
            bucket = s3_conn.get_bucket(bucket_name)
            break
        except Exception, e:
            continue

    # Download step logs
    for key in bucket.list(steps_path):

        if not os.path.isdir(os.path.dirname(key.name)):
            os.makedirs(os.path.dirname(key.name))

        try:
            res = key.get_contents_to_filename(key.name)
            print key.name
        except Exception, e:
            print "Failure: %s : %s" % (key.name, e)

    # Download task logs (if any)
    for key in bucket.list(task_path):

        if "_%s_" % str(task_index).zfill(4) in key.name:

            if not os.path.isdir(os.path.dirname(key.name)):
                os.makedirs(os.path.dirname(key.name))

            try:
                res = key.get_contents_to_filename(key.name)
                print key.name
            except Exception, e:
                print "Failure: %s : %s" % (key.name, e)
