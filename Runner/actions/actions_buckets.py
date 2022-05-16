#!/bin/env python

from argparse import ArgumentTypeError
from threading import Thread
import botocore
import requests
import random
import boto3
import queue
import time
import json
import csv
import re

queue = queue.Queue()

AWS_ACCESS_KEY_ID = ''
AWS_SECRET_ACCESS_KEY = ''

CSV_COLLECTABLE = 'results/Collectable.csv'
CSV_WRITABLE = 'results/Writable.csv'
CSV_ACL = 'results/ACL.csv'
CSV_PERMISSIONS = 'results/Permissions.csv'
CSV_COLLECTED_FILES = 'results/CollectedFiles.csv'

EXTENSION = re.compile("\.[A-Za-z0-9]{2,5}$")


class Settings(object):

    def __init__(self):
        self.WRITE_TEST_ENABLED = False
        self.WRITE_TEST_FILE = False
        self.OUTPUT_FILE = "output.txt"
        self.ANONYMOUS_MODE = False
        self.ACL_TEST_ENABLED = False
        self.COLLECT_TEST_ENABLED = False
        self.COLLECT_FILES = False
        self.SS_RESULTS = {}

    def set_write_test(self, write_file):
        self.WRITE_TEST_ENABLED = True
        self.WRITE_TEST_FILE = write_file

    def set_ACL_test(self):
        self.ACL_TEST_ENABLED = True

    def set_collect_test(self):
        self.COLLECT_TEST_ENABLED = True

    def set_collect_files(self):
        self.COLLECT_FILES = True

    def set_output_file(self, output_file):
        self.OUTPUT_FILE = output_file

    def set_anonymous_mode(self):
        self.ANONYMOUS_MODE = True
        print('''All tests will be executed in anonymous mode:
        If you want to send all requests using your AWS account please specify
        AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY variables in actions_buckets file
        ''')


def get_extension(s):
    return EXTENSION.findall(s)


def get_region(bucket_name):
    try:
        response = requests.get('http://' + bucket_name + '.s3.amazonaws.com/')
        region = response.headers.get('x-amz-bucket-region')
        time_response = response.elapsed.total_seconds()

        return [region, time_response]
    except Exception as e:
        print(f"Error: couldn't connect to '{bucket_name}' bucket. Details: {e}")


def get_session(bucket_name, region, sett):
    try:
        if sett.ANONYMOUS_MODE:
            sess = boto3.session.Session(region_name=region)
        else:
            sess = boto3.session.Session(
                region_name=region,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        conn = sess.resource('s3')
        bucket = conn.Bucket(bucket_name)
        return bucket

    except Exception as e:
        print(f"Error: couldn't create a session with '{bucket_name}' bucket. Details: {e}")


def get_bucket(bucket_name, sett):
    region, time_response = get_region(bucket_name)
    bucket = ""
    if region == 'None':
        print(f"Bucket '{bucket_name.encode('utf-8')}' does not exist.")
    else:
        bucket = get_session(bucket_name, region, sett)
    return bucket


def get_names(input_file):
    file = open(input_file, 'r')
    data = json.load(file)
    res = list(data.keys())
    return res


def getFiles(bucket_name, sett):
    try:
        bucket = get_bucket(bucket_name, sett)
        lis = list(bucket.objects.limit(count=50))
        print(f"Finding up to 50 files in bucket {bucket_name}")
        for s3_object in lis:
            name = s3_object.key
            files = {
                'BucketName': bucket_name,
                'ObjectName': name
            }
            ext = get_extension(name)
            if ext:
                files['Extension'] = ext[0][1:].lower()
            else:
                files["Extension"] = 'Unknown'

            append_csv(CSV_COLLECTED_FILES, files, list(files.keys()))

    except botocore.exceptions.ClientError as error:
        code = error.response['Error']['Code']
        error_code = f"Client Error when getting files with response: {code}"
        # print(error_code) # Uncomment if curious about the error code

    except Exception as e:
        print(f"Error: couldn't access the '{bucket_name}' bucket. Details: {e}\n")


def collect_buckets(bucket_name, sett):
    # Creates a connection with the bucket name and
    # Tries to extract a random object
    # Results are stored in a csv for further analysis

    region, time_response = get_region(bucket_name)

    if region == 'None':
        pass

    else:
        final = {
            "BucketName": bucket_name,
            "BucketRegion": region,
            "ResponseTime": time_response,
            "IsAccessible": False,
            "Code": ''
        }

        try:
            bucket = get_bucket(bucket_name, sett)

            lis = list(bucket.objects.limit(count=50))
            idx = random.randint(0, len(lis) - 1)
            obj = lis[idx]

            item = "http://s3."
            item += f"{region}.amazonaws.com/{bucket_name}/{obj.key}"

            res = f"Bucket '{bucket_name}' collectable: {item} !!!"
            final["IsAccessible"] = True
            final['Code'] = "Open"
            print(res)

            sett.SS_RESULTS[bucket_name]["SS_Collectable"] = False
            append_csv(CSV_COLLECTABLE,
                       final,
                       list(final.keys()))

        except botocore.exceptions.ClientError as error:
            code = error.response['Error']['Code']
            error_code = f"Client Error when finding objects with response: {code}"
            # print(error_code) # Uncomment if curious about the error code
            final["IsAccessible"] = False
            final['Code'] = code
            sett.SS_RESULTS[bucket_name]["SS_Collectable"] = True
            append_csv(CSV_COLLECTABLE,
                       final,
                       list(final.keys()))

        except Exception as e:
            final["IsAccessible"] = False
            final["Code"] = 'Connection Failed'
            sett.SS_RESULTS[bucket_name]["SS_Collectable"] = True
            print(f"Error: couldn't access the '{bucket_name}' bucket. Details: {e}\n")


def write_test(bucket_name, filename, sett):
    region, time_response = get_region(bucket_name)
    if region != 'None':
        final = {
            "BucketName": bucket_name,
            "BucketRegion": region,
            "IsWritable": False,
            "Code": ''
        }
        try:
            data = open(filename, 'rb')

            bucket = get_bucket(bucket_name, sett)
            bucket.put_object(Bucket=bucket_name,
                              Key=filename,
                              Body=data)
            print(f"Success: bucket '{bucket_name}' allows for uploading arbitrary files!!!")

            final["IsWritable"] = True
            final['Code'] = "Open"

            append_csv(CSV_WRITABLE,
                       final,
                       list(final.keys()))

        except botocore.exceptions.ClientError as error:
            code = error.response['Error']['Code']
            error_code = f"Client Error with response: {code}"
            print(error_code)
            final["IsWritable"] = False
            final['Code'] = code

            append_csv(CSV_WRITABLE,
                       final,
                       list(final.keys()))

        except Exception as e:
            final["IsWritable"] = False
            final["Code"] = 'Connection Failed'
            print(f"Error: couldn't upload file {filename} to '{bucket_name}' bucket. Details: {e}\n")


def append_output(file, results, method):
    with open(file, method) as output:
        output.write(results)


def append_csv(file, results, names):
    with open(file, mode='a') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=names, delimiter=';')
        writer.writerow(results)


def get_ACLs(bucket_name, sett):
    region, time_response = get_region(bucket_name)
    if region != 'None':
        final = {
            "BucketName": bucket_name,
            "BucketRegion": region,
            "ResponseTime": time_response,
            "GotACL": False,
            "Code": '',
            "Owner": None
        }
        try:
            bucket = get_bucket(bucket_name, sett)
            acl = bucket.Acl()
            owner = acl.owner
            grants = acl.grants

            final["Owner"] = list(owner.values())

            for grantees in grants:
                perms = {
                    'BucketName': bucket_name,
                    'DisplayName': None,
                    'EmailAddress': None,
                    'ID': None,
                    'Type': None,
                    'URI': None,
                    'Permission': grantees['Permission']
                }

                grant = grantees['Grantee']

                if 'DisplayName' in grant:
                    perms["DisplayName"] = grant['DisplayName']
                if 'EmailAddress' in grant:
                    perms["EmailAddress"] = grant['EmailAddress']
                if 'ID' in grant:
                    perms["ID"] = grant['ID']
                if 'Type' in grant:
                    perms["Type"] = grant['Type']
                    print(f"Permission: {grantees['Permission']} found")
                if 'URI' in grant:
                    perms["URI"] = grant['URI']

                append_csv(CSV_PERMISSIONS, perms, list(perms.keys()))

            sett.SS_RESULTS[bucket_name]["SS_ACL_Collectable"] = False
            final['GotACL'] = True
            final['Code'] = 'Open'
            append_csv(CSV_ACL, final, list(final.keys()))

        except botocore.exceptions.ClientError as error:
            code = error.response['Error']['Code']
            error_code = f"Client Error when finding ACLs with response: {code}"
            # print(error_code) # Uncomment if curious about the error code
            final['Code'] = code
            sett.SS_RESULTS[bucket_name]["SS_ACL_Collectable"] = True
            append_csv(CSV_ACL, final, list(final.keys()))

        except Exception as e:
            final['Code'] = 'Connection Failed'
            append_csv(CSV_ACL, final, list(final.keys()))
            sett.SS_RESULTS[bucket_name]["SS_ACL_Collectable"] = True
            print(f"Error: couldn't get the acl {e}\n")


def bucket_worker(sett):
    while True:
        try:
            bucket = queue.get()
            if sett.ACL_TEST_ENABLED:
                get_ACLs(bucket, sett)

            if sett.WRITE_TEST_ENABLED:
                write_test(bucket, sett.WRITE_TEST_FILE, sett)

            if sett.COLLECT_TEST_ENABLED:
                collect_buckets(bucket, sett)
                getFiles(bucket, sett)

            with open(sett.OUTPUT_FILE, 'w') as outfile:
                json.dump(sett.SS_RESULTS, outfile)
        except Exception as e:
            print(f"Error: {e}\n")
        queue.task_done()


def initialize(
        bucket_list,
        modes,
        threads=4,
        output="output.json",
        write="upload.txt"

):
    settings = Settings()

    if output is not "output.json":
        settings.set_output_file(output)
    if "collect" in modes:
        # Search for Collectable Buckets
        settings.set_collect_test()

    if "ACLs" in modes:
        # Search for ACL collectable buckets
        settings.set_ACL_test()

    if "files" in modes:
        # Find at least 50 files per collectable bucket
        settings.set_collect_files()

    if "write" in modes:
        # Writes file to bucket
        settings.set_write_test(write)

    if not (AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY):
        settings.set_anonymous_mode()

    file = open(bucket_list, 'r')
    settings.SS_RESULTS = json.load(file)

    bucks = list(settings.SS_RESULTS.keys())

    for i in range(0, threads):
        t = Thread(target=bucket_worker, args=[settings])
        t.daemon = True
        t.start()

    for bucket in bucks:
        queue.put(bucket)
    print(f"Starting modes: {modes}")
    queue.join()
