#!/usr/bin/env python
""" This is a script for collecting the credentials, 
choosing one of them, and creating a pickle file to hold them """

import sys
import os
from glob import glob
import AWS_keypair_management
import pickle
from os.path import expanduser
import boto.s3
import time
import curses_menu
import logging
import argparse
import shutil


def collect_credentials():
    # Log the csv files found in the vault directory
    for csv in glob(vault+'/*.csv'):
        logging.info("Found csv file: %s" % csv)

    csv_credentials = AWS_keypair_management.AWS_keypair_management()
    (credentials, bad_files) = csv_credentials.Get_Working_Credentials(vault)

    # If there is more than one AWS key pair then display them using a menu, otherwise just select the one
    if len(credentials) > 1:
        # Log the valid AWS credentials that are found
        logging.info("Multiple AWS credentials found:")
        for credential in credentials:
            logging.info("AWS credential found: %s : %s" %
                         (credential, credentials[credential]['Creds'][0]['Access_Key_Id']))

        title = "Which AWS credentials do you want to use? Below is the list of user names."
        top_instructions = "Use the arrow keys make your selection and press return to continue"
        bottom_instructions = ""
        user_input = curses_menu.curses_menu(credentials, title=title, top_instructions=top_instructions,
                                             bottom_instructions=bottom_instructions)
        user_id = credentials.keys()[int(user_input)]
        logging.info("AWS credential selected: %s : %s" % (user_id, credentials[user_id]['Creds'][0]['Access_Key_Id']))
    elif len(credentials) == 1:
        user_id = credentials.keys()[0]
        logging.info("One AWS credential found and selected: %s : %s" % (user_id, credentials.keys()[0]))
    else:
        logging.info("No AWS credentials found")
        sys.exit("No AWS credentials found.")

    entry = credentials[user_id]

    key_id = entry['Creds'][0]['Access_Key_Id']
    secret_key = entry['Creds'][0]['Secret_Access_Key']

    try:
        s3 = boto.connect_s3(aws_access_key_id=key_id,
                             aws_secret_access_key=secret_key)
    except Exception, e:
        logging.info("There was an error connecting to AWS: %s" % e)
        sys.exit("There was an error connecting to AWS: %s" % e)

    # Make sure all of the variables exist before trying to write them to vault/Creds.pkl
    if (not user_id is None) and (not key_id is None) and (not secret_key is None):
        print 'ID: %s, key_id: %s' % (user_id, key_id)
    else:
        logging.info("Undefined variable: user_id: %s, key_id: %s" % (user_id, key_id))
        sys.exit("Undefined variable")

    logging.info("Asking for s3 bucket")
    s3_bucket = ""
    bucket_exists = False

    while not s3_bucket.startswith("s3://") or not s3_bucket.endswith("/") or not bucket_exists:
        s3_bucket = raw_input("What is your S3 bucket in \"s3://bucket-name/\" format: ")
        logging.info("s3 bucket raw input: %s" % s3_bucket)

        bucket_name = s3_bucket.replace('s3://', '').replace('/', '')

        try:
            s3.get_bucket(bucket_name)
            bucket_exists = True
            logging.info("%s exists!" % s3_bucket)
        except Exception, e:
            bucket_exists = False
            print "%s does not exist on AWS S3. Please make sure you are entering the correct bucket name." % s3_bucket
            logging.info("%s does not exist!" % s3_bucket)

    logging.info("s3 bucket: %s" % s3_bucket)

    new_credentials = {}
    # If a Creds.pkl file already exists, make a copy, read the non 'launcher' credentials
    if os.path.isfile(vault + "/Creds.pkl"):
        logging.info("Found existing %s/Creds.pkl" % vault)
        # Make a copy of vault/Creds.pkl before making any changes
        old_credentials = vault + "/Creds_%s.pkl" % str(int(time.time()))
        try:
            shutil.copyfile(vault + "/Creds.pkl", old_credentials)
            logging.info("Copied %s/Creds.pkl to %s" % (vault, old_credentials))
        except (IOError, EOFError):
            logging.info("Error copying %s/Creds.pkl to %s" % (vault, old_credentials))
            sys.exit("Error copying %s/Creds.pkl to %s" % (vault, old_credentials))

        # Read the contents of vault/Creds.pkl
        try:
            pickle_file = open(vault + '/Creds.pkl', 'rb')
            saved_credentials = pickle.load(pickle_file)
            pickle_file.close()
            logging.info("Reading %s/Creds.pkl" % vault)
            print "Updating %s/Creds.pkl" % vault
        except (IOError, EOFError):
            saved_credentials = {}
            logging.info("Error reading %s/Creds.pkl" % vault)
            print "Error reading %s/Creds.pkl" % vault

        # Add all the top level keys that are not launcher
        for c in saved_credentials:
            logging.info("Found top level key in Creds.pkl: %s" % c)
            if not c == "launcher":
                logging.info("Saving %s to Creds.pkl unchanged" % c)
                new_credentials.update({c: saved_credentials[c]})
    else:
        logging.info("Creating a new %s/Creds.pkl" % vault)
        print "Creating a new %s/Creds.pkl" % vault

    # Add the new launcher credentials
    logging.info("Adding ID: %s, key_id: %s s3_bucket: %s to Creds.pkl" % (user_id, key_id, s3_bucket))
    new_credentials.update({'mrjob': {'ID': user_id,
                                      'key_id': key_id,
                                      'secret_key': secret_key,
                                      's3_bucket': s3_bucket}})

    # Write the new vault/Creds.pkl
    pickle_file = open(vault + '/Creds.pkl', 'wb')
    pickle.dump(new_credentials, pickle_file)
    pickle_file.close()
    logging.info("Saved %s/Creds.pkl" % vault)
    s3.close()

    # Create ~/.mrjob.conf with AWS credentials
    s3_scratch_uri = "%stmp" % s3_bucket
    s3_log_uri = "%slogs" % s3_bucket

    logging.info("Creating ~/.mrjob.conf")
    template = open('mrjob.conf.template').read()

    filled_template = template % (key_id, secret_key, s3_scratch_uri, s3_log_uri)
    logging.info("~/.mrjob.conf template filled")

    home = os.environ['HOME']
    mrjob_outfile = "%s/.mrjob.conf" % home

    try:
        open(mrjob_outfile, 'wb').write(filled_template)
        logging.info("Wrote: %s" % mrjob_outfile)
        print "Wrote: %s" % mrjob_outfile
    except (IOError, EOFError):
        logging.info("Error writing to %s" % mrjob_outfile)
        sys.exit("Error writing to %s" % mrjob_outfile)


def clear_vault():
    backup_directory = vault + "/" + "Vault_" + str(int(time.time()))

    os.makedirs(backup_directory)
    logging.info("Clearing Vault to %s" % backup_directory)

    # Move all of the non .csv files into the backup_directory
    for clear_vault_file in glob(vault+'/*'):
        if os.path.isfile(clear_vault_file):
            if os.path.splitext(clear_vault_file)[1] == ".csv":
                logging.info("Leaving Vault file: %s" % clear_vault_file)
            else:
                logging.info("Moving Vault file: %s" % clear_vault_file)
                os.rename(clear_vault_file, backup_directory + "/" + os.path.basename(str(clear_vault_file)))

    logging.info("Clearing Complete")


if __name__ == "__main__":
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

    # Create a logs directory in the vault directory if one does not exist
    if not os.path.exists(vault + "/logs"):
        os.makedirs(vault + "/logs")

    # Save a log to vault/logs/setup.log
    logging.basicConfig(filename=vault + "/logs/setup.log", format='%(asctime)s %(message)s', level=logging.INFO)

    logging.info("mrjob_setup.py started")
    logging.info("Vault: %s" % vault)

    # Log all of the files in the Vault directory
    for vault_file in glob(vault+'/*'):
        logging.info("Found Vault file: %s" % vault_file)

    # Commandline Parameters
    parser = argparse.ArgumentParser(description="This is a script for collecting the AWS credentials and creating " +
                                                 "a pickle file to hold them ")
    parser.add_argument('-c', dest='clear', action='store_true', default=False,
                        help='Clear the Vault directory before running')

    args = vars(parser.parse_args())

    if args['clear']:
        clear_vault()

    collect_credentials()

    logging.info("mrjob_setup.py finished")