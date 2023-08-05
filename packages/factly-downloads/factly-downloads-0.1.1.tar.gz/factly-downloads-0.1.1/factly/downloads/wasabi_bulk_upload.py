import json
from glob import glob
from pathlib import Path
from typing import Union

import boto3
import click
from botocore.exceptions import ClientError, NoCredentialsError

WASABI_FILE_CONF = "../../libs/downloads/factly/downloads/wasabi_keys.cfg"
WASABI_END_POINT = "https://s3.eu-central-1.wasabisys.com"


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
def main(prefix, bucket, create_bucket, datasets, file_format, filename_pattern):
    cwd = Path.cwd()
    click.echo(f"Current working directory is : {cwd}")
    with open(WASABI_FILE_CONF, "r") as secrets:
        wasabi = json.load(secrets)
        wasabi_access_key = wasabi["key"]
        wasabi_secret_key = wasabi["secret"]

    bucket = cwd.name if bucket is None else bucket

    session = boto3.Session(
        aws_access_key_id=wasabi_access_key,
        aws_secret_access_key=wasabi_secret_key,
    )
    s3 = session.resource("s3", endpoint_url=WASABI_END_POINT)
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
