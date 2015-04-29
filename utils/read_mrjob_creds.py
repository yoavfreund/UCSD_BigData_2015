#!/usr/bin/env python

import sys
import os
from os.path import expanduser
import pickle


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
        elif c == "ID":
            p_user_name = credentials['ID']
        elif c == "s3_bucket":
            p_s3_bucket = credentials["s3_bucket"]

    # These credentials are required to be set before proceeding
    try:
        p_credentials_path
        p_aws_access_key_id
        p_aws_secret_access_key
        p_user_name
        p_s3_bucket
    except NameError, e:
        sys.exit("Not all of the credentials were defined: %s" % e)

    return p_aws_access_key_id, p_aws_secret_access_key, p_s3_bucket, p_user_name