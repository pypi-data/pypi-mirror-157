import json
import os
import sys
from glob import glob
from pathlib import Path
from typing import Union

import boto3
import click
from botocore.exceptions import ClientError, NoCredentialsError

# WASABI_FILE_CONF = "../../libs/downloads/factly/downloads/wasabi_keys.cfg"
# WASABI_END_POINT = "https://s3.eu-central-1.wasabisys.com"


def upload_to_wasabi(s3_resource, file_name, bucket, data):
    """
    Function to upload a dataset on to the wasabi cloud
    """
    try:
        s3_resource.Bucket(bucket).put_object(Key=file_name, Body=data)
        return True
    except FileNotFoundError:
        click.echo("The file was not found")
        return False
    except NoCredentialsError:
        click.echo("Credentials not available")
        return False


def get_csv_path(
    prefix: str,
    dataset_dir,
    datasets: Union[str, None] = "processed",
    file_format: Union[str, None] = "csv",
    filename_pattern: str = "output*",
) -> iter:
    """Function provide Path to datasets stored in "processed" folder.

    Args:
        prefix (str): prefix name for which the dataset belongs, if all dataset are required pass "None"
        dataset_dir (PosixPath, optional): Path to processed folder. Defaults to DATASET_FOLDER.

    Raises:
        ValueError: Raised when "prefix" passed is not present or wrong.

    Yields:
        Iterator[iter]: Iterate path of datasets in strings
    """
    # If no specific prefix is provided then do operation for all prefix
    if not prefix:
        # * will match to any prefix
        prefix = "**"
    if not datasets:
        datasets = "*"
    if not file_format:
        file_format = "*"
    if not filename_pattern:
        filename_pattern = "*"

    # csv path are required to their respective processed csv's
    click.echo("File Pattern : ")
    click.echo(
        str(dataset_dir) + f"/data/{datasets}/{prefix}/{filename_pattern}.{file_format}"
    )
    csv_path = sorted(
        glob(
            str(dataset_dir)
            + f"/data/{datasets}/{prefix}/{filename_pattern}.{file_format}",
            recursive=True,
        )
    )

    # Cross-checking if no specific name is provided
    # Raise value error to notify user that given prefix contains no files
    if not csv_path:
        # ValueError to give idea that Value entered for prefix is not proper
        raise ValueError(
            f"No Dataset path present for CATEGORY : '{prefix}'.\nEither no csv present under '{prefix}' or improper CATEGORY name provided"
        )

    # Number of files could be more
    # we dont require sequence from above list
    yield from csv_path


@click.command()
@click.option(
    "--prefix",
    "-p",
    help="Provide Specific file prefix name , if Required.",
)
@click.option(
    "--bucket",
    "-b",
    help="Provide S3 bucket name , if Required.",
    default=None,
)
@click.option(
    "--create_bucket",
    "-c",
    help="Create S3 bucket , if Required.",
    type=bool,
    default=False,
)
@click.option(
    "--datasets",
    "-d",
    help="Dataset Category , processed, raw, interim or external.",
    default=None,
)
@click.option(
    "--file_format", "-f", help="File format for files to upload", default=None
)
@click.option(
    "--filename_pattern",
    "-fp",
    help="File name format for files to upload",
    default=None,
)
@click.option(
    "--access_tokens",
    "-keys",
    help="File name for access tokens",
    default=None,
)
@click.option(
    "--s3_host",
    "-host",
    help="S3 Endpoint url",
    default=None,
)
def main(
    prefix,
    bucket,
    create_bucket,
    datasets,
    file_format,
    filename_pattern,
    access_tokens,
    s3_host,
):
    cwd = Path.cwd()
    click.echo(f"Current working directory is : {cwd}")
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
    bucket = cwd.name if bucket is None else bucket

    session = boto3.Session(
        aws_access_key_id=WASABI_ACCESS_KEY,
        aws_secret_access_key=WASABI_SECRET_KEY,
    )
    s3 = session.resource("s3", endpoint_url=S3_HOST)
    try:
        s3.meta.client.head_bucket(Bucket=bucket)
    except ClientError:
        if not create_bucket:
            raise ValueError(f"Bucket : '{bucket}' does not exist")
        s3.create_bucket(Bucket=bucket)
    finally:
        click.echo(f"Bucket name is : {bucket}")

    for each_file_path in get_csv_path(
        prefix,
        dataset_dir=cwd,
        datasets=datasets,
        file_format=file_format,
        filename_pattern=filename_pattern,
    ):
        data = open(each_file_path, "rb")
        object_name = str(each_file_path).split("/data/")[-1]
        response = upload_to_wasabi(s3, object_name, bucket, data)
        if response:
            click.secho(f"File : '{object_name}' uploaded successfully", fg="green")
            continue
        click.secho(f"File : '{object_name}' failed to upload", fg="red")
