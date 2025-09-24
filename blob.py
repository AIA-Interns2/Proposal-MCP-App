from azure.storage.blob import BlobServiceClient
import os
import logging
from dotenv import load_dotenv

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace with your connection string
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_CONNECTION_STRING")
CONTAINER_NAME = "proposals"

def upload_blob(local_file_path: str, blob_name: str) -> str:
    """
    Upload a file to Azure Blob Storage and return the blob URL.
    
    :param local_file_path: Path to the local file to upload
    :param blob_name: Name to give the blob in Azure
    :return: Blob URL if successful, empty string if failed
    """
    try:
        logger.info(f"Starting upload of {local_file_path} to blob {blob_name}")
        
        # Check if local file exists
        if not os.path.exists(local_file_path):
            logger.error(f"Local file not found: {local_file_path}")
            return ""
        
        # Get file size for logging
        file_size = os.path.getsize(local_file_path)
        logger.info(f"File size: {file_size} bytes")
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        
        # Get container client
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)
        
        # Try to create container if it doesn't exist
        try:
            container_client.create_container()
            logger.info(f"Created container: {CONTAINER_NAME}")
        except Exception as container_error:
            logger.info(f"Container already exists or creation issue: {str(container_error)}")
        
        # Upload the blob
        with open(local_file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)
            logger.info(f"Successfully uploaded blob: {blob_name}")
        
        # Get the blob client to construct proper URL
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        blob_url = blob_client.url
        
        logger.info(f"Blob URL: {blob_url}")
        
        return blob_url
        
    except FileNotFoundError as e:
        error_msg = f"File not found: {str(e)}"
        logger.error(error_msg)
        return ""
    except Exception as e:
        error_msg = f"Upload failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return ""

def download_blob(blob_name: str, download_file_path: str) -> bool:
    """
    Download a blob from Azure Blob Storage to a local file.
    
    :param blob_name: Name of the blob in Azure
    :param download_file_path: Path to save the downloaded file
    :return: True if successful, False if failed
    """
    try:
        logger.info(f"Starting download of blob {blob_name} to {download_file_path}")
        
        # Create blob service client
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        
        # Get blob client
        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
         
        # Check if blob exists
        if not blob_client.exists():
            error_msg = f"Blob not found: {blob_name}"
            logger.error(error_msg)
            return False
        
        # Download the blob
        with open(download_file_path, "wb") as download_file:
            blob_data = blob_client.download_blob()
            download_file.write(blob_data.readall())
        
        # Verify download
        if os.path.exists(download_file_path):
            logger.info(f"Successfully downloaded blob {blob_name} to {download_file_path}")
            return True
        else:
            logger.error("Download completed but file not found locally")
            return False
            
    except Exception as e:
        error_msg = f"Download failed: {type(e).__name__}: {str(e)}"
        logger.error(error_msg)
        return False