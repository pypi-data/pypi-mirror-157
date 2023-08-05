"""
This script is to  downloading the scraped files to local or/and google drive or/and wasabi or Amazon S3.
"""
import json
import mimetypes
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError
from google.oauth2 import credentials as cred
from googleapiclient import discovery
from googleapiclient.http import MediaFileUpload


# Main function
def download_files(
    self, response, storage_mode, parent_folder, path_value, file_name
):
    """
    This function takes in the above parameters and downloads the files
    on to the local and/or wasabi and/or google drive
    depending on the parameter provided in storage_mode.
    Note: If storage mode is gdrive, files will be downloaded
    both locally and uploaded to gdrive.
    """
    if "local" in storage_mode:
        path = Path(parent_folder + "/" + path_value)
        path.mkdir(parents=True, exist_ok=True)
        with open(file_name, "wb") as f:
            f.write(response.body)

    if "wasabi" in storage_mode:
        wasabi_keys = open(
            "../../libs/downloads/factly/downloads/wasabi_keys.cfg"
        )
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
        wasabi_bucket = s3.create_bucket(Bucket=self.name)

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

        path = str(path_value + "/" + file_name)
        data = response.body
        # invoking the upload function to wasabi or amazon s3.
        upload_to_wasabi(path, wasabi_bucket, data)
        print("file uploaded to wasabi on this path: ", path)

    if "gdrive" in storage_mode:

        def upload_to_gdrive(filename, parent_id, file_path, mimetype):
            """
            Function to upload the data to google drive,
            this will require the folder ID for which the user has
            access to and has access to and respective user's storage.json file
            which has token details
            """
            file_metadata = {"name": filename, "parents": [parent_id]}
            media = MediaFileUpload(
                file_path, mimetype=mimetype, resumable=True
            )
            file = (
                drive_service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(filename, "is uploaded to the drive")
            print("File ID: %s" % file.get("id"))

        def folder_creation(folder, parent_id):
            """
            Function to create folders in a parent folder
            """
            file_metadata = {
                "name": folder,
                "parents": [parent_id],
                "mimeType": "application/vnd.google-apps.folder",
            }
            file = (
                drive_service.files()
                .create(body=file_metadata, fields="id")
                .execute()
            )
            folder_id = file.get("id")
            print("Folder ID: %s" % file.get("id"))
            return folder_id

        def list_folders(folder_id):
            """
            Function to list all the folders/files in a specific folder of the drive
            """
            query = "'" + folder_id + "'" + " in parents"

            response = (
                drive_service.files()
                .list(
                    q=query, spaces="drive", fields="files(id, name, parents)"
                )
                .execute()
            )
            items = response.get("files", [])
            return items

        # Function to get the data from response to a file
        def file_response(file_path, file_name):
            file_path.mkdir(parents=True, exist_ok=True)
            file_path = str(file_path) + "/" + file_name
            print(file_path)
            with open(file_path, "wb") as data:
                data.write(response.body)
            # getting the mimetype of the object
            mime_type = mimetypes.guess_type(file_name)[0]
            #
            print("mime_type is", mime_type)
            return mime_type, file_path

        """
        Auth for google drive: https://cloud.google.com/docs/authentication/end-user
        """
        storage_file = open(
            "../../libs/downloads/factly/downloads/storage.json"
        )
        storage = json.load(storage_file)

        credentials = cred.Credentials(
            storage["access_token"],
            refresh_token=storage["refresh_token"],
            token_uri=storage["token_uri"],
            client_id=storage["client_id"],
            client_secret=storage["client_secret"],
        )
        """
        part to create folders and upload the file onto the drive
        """
        drive_service = discovery.build(
            "drive", "v3", credentials=credentials, cache_discovery=False
        )
        file_path = Path(parent_folder + "/" + path_value)
        drive_path = str(path_value + "/" + file_name)
        path_list = drive_path.split("/")
        # Home directory Folder ID at the initiation
        # WE NEED TO PROVIDE THIS
        parent_id = "1DJ_7PSbib8rvFzXqv8LzH_tsrFh8mAUg"
        for folder in path_list:
            if folder == path_list[-1]:
                mime_type, file_path = file_response(file_path, file_name)
                # uploading the file
                upload_to_gdrive(file_name, parent_id, file_path, mime_type)
                print("file is uploaded to gdrive on this path: ", drive_path)
            else:
                folder_dict = list_folders(parent_id)
                folder_names = list()
                folder_id = list()
                if len(folder_dict) > 0:
                    for each in folder_dict:
                        folder_names.append(each["name"])
                        folder_id.append(each["id"])
                    folder_tuple = zip(folder_names, folder_id)
                    flag = 1
                    for f_name, f_id in folder_tuple:
                        if folder == f_name:
                            parent_id = f_id
                            flag = 0
                            break
                    if flag == 1:
                        parent_id = folder_creation(folder, parent_id)
                else:
                    parent_id = folder_creation(folder, parent_id)
