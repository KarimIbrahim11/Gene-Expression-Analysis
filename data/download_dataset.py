import logging
import zipfile
import urllib.request

from tqdm import tqdm
from pathlib import Path
from typing import List
from urllib.parse import urlparse

from src.configs.config_parser import PathConfigParser, data_config_file, project_root


# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(sh)

def download_file(url: str, download_path: Path) -> Path:
    """
        Downloads a single file from url.
    """
    try:
        # Open the URL and get the response headers
        with urllib.request.urlopen(url) as response:
            # Check for the Content-Disposition header to get the filename
            content_disposition = response.getheader('Content-Disposition')
            if content_disposition and 'attachment' in content_disposition:
                # Extract the filename from the Content-Disposition header
                file_name = content_disposition.split('filename=')[1].strip('\"')
            else:
                # If the header is not found, use the URL as fallback
                parsed_url = urlparse(url)
                file_name = Path(parsed_url.path).name  # Get the file name from the URL path

            # Get the file size from the response headers (for progress bar)
            file_size = int(response.getheader('Content-Length', 0))
            
            # Download the file with the extracted name
            with open(download_path / file_name, 'wb') as out_file:
                # Create a tqdm progress bar
                with tqdm(total=file_size, unit='B', unit_scale=True, desc=file_name) as pbar:
                    # Download and write the file in chunks
                    while True:
                        chunk = response.read(1024)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        pbar.update(len(chunk))  # Update the progress bar with each chunk

                # out_file.write(response.read())
            logger.info(f"Downloaded: {file_name}")

            return file_name
        
    except Exception as e:
        logger.info(f"Error downloading {url}: {e}")


def unzip_file(zip_path: Path, extract_to: Path) -> None:
    """
        Unzips .zip Files.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        logger.info(f"Unzipped: {zip_path}")
    except zipfile.BadZipFile:
        logger.info(f"Error unzipping {zip_path}: Not a valid zip file")
    except Exception as e:
        logger.info(f"Error unzipping {zip_path}: {e}")


def get_dataset(dataset_urls: List[str], dataset_path: Path = project_root / Path("data/raw")) -> None:
    """
        Downloads dataset from the list of dataset_urls given.
    """
    if not dataset_path.exists():
        dataset_path.mkdir(parents=True, exist_ok=True)

    # Loop through each URL
    for url in dataset_urls:
        logger.info(f"Downloading from URL: {url}")
        # Download the file
        file_name = download_file(url, dataset_path)
        
         # Unzip the file if needed
        zip_file_path = dataset_path / file_name
        if zip_file_path.suffix == '.zip':
            unzip_dir = dataset_path / file_name.replace(".zip", "")
            if not unzip_dir.exists():
                unzip_dir.mkdir(parents=True, exist_ok=True)  # Create a directory for unzipped files
            unzip_file(zip_file_path, unzip_dir)


def main():
# Configs Directory
    parser = PathConfigParser(str(data_config_file))
    parser.load()

    # List of Data URLs:
    DATASET_URLS = parser.get("data_urls")
    
    # Download Dataset URLs
    get_dataset(DATASET_URLS)


if __name__=="__main__":
    main()
