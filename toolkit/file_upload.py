import os

import constants
import requests
from bs4 import BeautifulSoup

import main
logger = main.logging_func()

def upload_files_to_drive(tracked_website_piece, file_selector, parent_folder, gdrive, sub_folder = None):
    soup = BeautifulSoup(tracked_website_piece, "lxml")
    file_urls = [i.attrs.get("href") for i in soup.select(file_selector)]
    file_names = [i.text.strip() for i in soup.select(file_selector)]
    files = {}

    for i in range(len(file_names)):
        files[file_names[i]] = file_urls[i]

    parent_folder_id = gdrive.GetFolderID(parent_folder)

    for file_name, f in files.items():
        file_name = extract_extension(file_name, f)

        if not sub_folder:
            if (not gdrive.GetFileID(file_name, parent_folder_id)):
                logger.info("Uploading %s to %s...", file_name, parent_folder.title())
                download_file(file_name, f)
                gdrive.FileUpload(os.path.join(constants.TEMP_PATH, file_name), parent_folder_id)
                os.remove(os.path.join(constants.TEMP_PATH, file_name))
            else:
                logger.info("File %s already exists on Drive.", file_name)

        else:
            if not gdrive.GetFolderID(sub_folder, parent_folder_id):
                gdrive.CreateFolder(sub_folder, parent_folder_id)

            sub_folder_id = gdrive.GetFolderID(sub_folder, parent_folder_id)

            if not gdrive.GetFileID(file_name, sub_folder_id):
                logger.info("Uploading %s to %s ...", file_name, sub_folder.title())
                download_file(file_name, f)
                gdrive.FileUpload(os.path.join(constants.TEMP_PATH, file_name), sub_folder_id)
                os.remove(os.path.join(constants.TEMP_PATH, file_name))
            else:
                logger.info("File %s already exists on Drive.", file_name)

def download_file(file_name, file_link):
    r = requests.get(file_link, allow_redirects=True, stream=True)
    r.raise_for_status()

    if not os.path.exists(constants.TEMP_PATH):
        os.mkdir(constants.TEMP_PATH)

    with open(os.path.join(constants.TEMP_PATH, file_name), "wb") as handle:
        for block in r.iter_content(1024):
            handle.write(block)

def extract_extension(file_name, file_url):
    _, ext = os.path.splitext(file_url)
    _, existing_ext = os.path.splitext(file_name)

    if (existing_ext == '.'):
        full_file_name = file_name[:-1] + ext
    elif not existing_ext:
        full_file_name = file_name + ext
    else:
        full_file_name = file_name

    return full_file_name