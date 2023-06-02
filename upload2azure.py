"""Upload a local file to a blob storage on Azure"""

import logging

# pip install azure-storage-blob azure-identity python-dotenv tenacity

# from azure.core.exceptions import AzureError
from azure.storage.blob import BlobServiceClient
from dotenv import dotenv_values
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError


# Based on https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli

# Create a .env file with
# ACCOUNT_NAME=GRAB_IT_FROM_AZURE_PORTAL
# SAS_TOKEN=GRAB_IT_FROM_AZURE_PORTAL
# CONTAINER_NAME=GRAB_IT_FROM_AZURE_PORTAL


@retry(stop=stop_after_attempt(5), wait=wait_fixed(1))
def upload_to_blob_storage(local_filepath: str, remote_blob_file_name: str):
    try:
        # blob_service_client = BlobServiceClient.from_connection_string(
        #     config["CONNECTION_STRING"]
        # )
        blob_service_client = BlobServiceClient(
            account_url=f"https://{config['ACCOUNT_NAME']}.blob.core.windows.net",
            credential=config["SAS_TOKEN"],
        )
        blob_client = blob_service_client.get_blob_client(
            container=config["CONTAINER_NAME"], blob=remote_blob_file_name
        )
        with open(local_filepath, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
    except Exception as e:
        logger.error(f"Error occurred while uploading local file {local_filepath}: {e}")
        raise e
    logger.debug(
        f"Local file {local_filepath} uploaded successfully to {remote_blob_file_name} blob in {config['CONTAINER_NAME']} container."
    )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger_file_handler = logging.handlers.RotatingFileHandler(
        "status.log",
        maxBytes=1024 * 1024,
        backupCount=1,
        encoding="utf8",
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    logger_file_handler.setFormatter(formatter)
    logger.addHandler(logger_file_handler)

    config = dotenv_values(".env")

    try:
        upload_to_blob_storage("PATH_OF_FILE_TO_UPLOAD", "REMOTE_BLOB_FILE_NAME")
    except RetryError:
        logger.error(f"Maximum number of retries reached.")
