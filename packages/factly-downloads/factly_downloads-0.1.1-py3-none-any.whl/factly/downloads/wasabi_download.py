import json
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


def wasabi_download(bucket_name, local_folder_path):
    """Function with Bucket name will download everything from bucket to local folder

    Args:
        bucket_name (str): name of s3 bucket
        local_folder_path (str): Local folder path , generally `data` inside project repo.
    """
    # Read Access Key and Secret Key
    wasabi_keys = open("../../libs/downloads/factly/downloads/wasabi_keys.cfg")
    wasabi = json.load(wasabi_keys)
    WASABI_ACCESS_KEY = wasabi["key"]
    WASABI_SECRET_KEY = wasabi["secret"]

    # Creaate session
    session = boto3.Session(
        aws_access_key_id=WASABI_ACCESS_KEY,
        aws_secret_access_key=WASABI_SECRET_KEY,
    )
    # Add end point to session
    s3 = session.resource(
        "s3", endpoint_url="https://s3.eu-central-1.wasabisys.com"
    )
    # bucket instance
    project_bucket = s3.Bucket(bucket_name)

    for file_path in get_obj_key(project_bucket):
        download(project_bucket, file_path, local_folder_path)
