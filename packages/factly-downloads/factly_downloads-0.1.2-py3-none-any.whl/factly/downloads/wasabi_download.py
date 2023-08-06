import json
import os
import sys
from pathlib import Path

import boto3


def get_obj_key(bucket):
    """Funtion to yield all possible file path present inside bucket

    Args:
        bucket (Bucket): s3 bucket

    Yields:
        [path]: [str]
    """
    for obj in bucket.objects.all():
        yield obj.key


def download(bucket, wasabi_file_path, local_folder_path):
    """Function will download file from remote wasabi to local folder

    Args:
        bucket : s3 bucket
        wasabi_file_path (str): path yielded from 'get_obj_key'
        local_folder_path (str): Local folder path , generally `data` inside project repo.
    """
    # filename to save the file in local
    # folder subdirectories inside data
    split_path = wasabi_file_path.split("/")
    filename = split_path[-1]
    sub_directories = "/".join(split_path[:-1])

    # join local data folder and sub_directories
    output_folder = Path(local_folder_path).joinpath(sub_directories)
    if not output_folder.is_dir():
        output_folder.mkdir(parents=True, exist_ok=True)

    bucket.download_file(
        Filename=str(output_folder) + "/" + filename, Key=wasabi_file_path
    )


def wasabi_download(bucket_name, local_folder_path, access_tokens=None, s3_host=None):
    """Function with Bucket name will download everything from bucket to local folder

    Args:
        bucket_name (str): name of s3 bucket
        local_folder_path (str): Local folder path , generally `data` inside project repo.
    """
    # Read Access Key and Secret Key
    if access_tokens is None:
        try:
            if os.environ["S3_ACCESS_KEY"] and os.environ["S3_SECRET_KEY"]:
                WASABI_ACCESS_KEY = os.environ["S3_ACCESS_KEY"]
                WASABI_SECRET_KEY = os.environ["S3_SECRET_KEY"]
        except KeyError:
            print("environment variables S3_ACCESS_KEY or S3_SECRET_KEY is not set.")
            sys.exit(1)
    else:
        with open(access_tokens, "r") as wasabi_keys:
            wasabi = json.load(wasabi_keys)
            WASABI_ACCESS_KEY = wasabi["key"]
            WASABI_SECRET_KEY = wasabi["secret"]
    if s3_host is None:
        try:
            if os.environ["S3_HOST"]:
                S3_HOST = os.environ["S3_HOST"]
        except KeyError:
            print("environment variables S3_HOST is not set.")
            sys.exit(1)
    else:
        S3_HOST = s3_host
    # Creating a Session on Wasabi
    # mentioning the endpoint to wasabi, this is insane
    session = boto3.Session(
        aws_access_key_id=WASABI_ACCESS_KEY,
        aws_secret_access_key=WASABI_SECRET_KEY,
    )
    s3 = session.resource("s3", endpoint_url=S3_HOST)
    # bucket instance
    project_bucket = s3.Bucket(bucket_name)

    for file_path in get_obj_key(project_bucket):
        download(project_bucket, file_path, local_folder_path)
