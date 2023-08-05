import json

import boto3
from botocore.exceptions import NoCredentialsError


def wasabi_upload(bucket_name, wasabi_path, local_file_path):
    """
    function to upload files from local to wasabi
    """
    wasabi_keys = open("../../libs/downloads/factly/downloads/wasabi_keys.cfg")
    wasabi = json.load(wasabi_keys)
    WASABI_ACCESS_KEY = wasabi["key"]
    WASABI_SECRET_KEY = wasabi["secret"]

    # Creating a Session on Wasabi
    # mentioning the endpoint to wasabi, this is insane

    session = boto3.Session(
        aws_access_key_id=WASABI_ACCESS_KEY,
        aws_secret_access_key=WASABI_SECRET_KEY,
    )
    s3 = session.resource(
        "s3", endpoint_url="https://s3.eu-central-1.wasabisys.com"
    )
    """
    This next command will create a new bucket for the dataset that we are wroking on
    """
    # for bucket in s3.buckets.all():
    #     if bucket.name == bucket_name:
    #         print(bucket_name + " bucket already exists")
    #         wasabi_bucket = bucket_name
    #         pass
    #     else:
    wasabi_bucket = s3.create_bucket(Bucket=bucket_name)

    def upload_to_wasabi(file_name, bucket, data):
        """
        Function to upload a dataset on to the wasabi cloud
        """
        try:
            s3.Bucket(bucket).put_object(Key=file_name, Body=data)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    data = open(local_file_path, "rb")
    wasabi_bucket = bucket_name
    # invoking the upload function to wasabi or amazon s3.
    upload_to_wasabi(wasabi_path, wasabi_bucket, data)
    print("file uploaded to wasabi on this path: ", wasabi_path)
