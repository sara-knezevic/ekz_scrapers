
# import the required libraries 
from __future__ import print_function
import os.path 
import io 
import shutil
from mimetypes import MimeTypes 
from googleapiclient.discovery import build, key2param 
from google_auth_oauthlib.flow import InstalledAppFlow 
from google.auth.transport.requests import Request 
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from google.oauth2.credentials import Credentials
import constants

class DriveAPI: 
    global SCOPES 
      
    # Define the scopes 
    SCOPES = ['https://www.googleapis.com/auth/drive'] 
  
    def __init__(self): 
  
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(constants.CREDENTIALS):
            creds = Credentials.from_authorized_user_file(constants.CREDENTIALS, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    constants.CLIENT_SECRET, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(constants.CREDENTIALS, 'w') as token:
                token.write(creds.to_json())

        self.service = build('drive', 'v3', credentials=creds)
  
    def CreateFolder(self, name, parent_folder = None):
        file_metadata = {
            'name': name.title(),
            'parents': [parent_folder] if parent_folder else None,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        self.service.files().create(body=file_metadata, fields='id').execute()

    def FileDownload(self, file_id, file_name): 
        request = self.service.files().get_media(fileId=file_id) 
        fh = io.BytesIO() 
          
        # Initialise a downloader object to download the file 
        downloader = MediaIoBaseDownload(fh, request, chunksize=204800) 
        done = False
  
        try: 
            # Download the data in chunks 
            while not done: 
                status, done = downloader.next_chunk() 
  
            fh.seek(0) 
              
            # Write the received data to the file 
            with open(file_name, 'wb') as f: 
                shutil.copyfileobj(fh, f) 
  
            print("File Downloaded") 
            # Return True if file Downloaded successfully 
            return True
        except: 
            
            # Return False if something went wrong 
            print("Something went wrong.") 
            return False
  
    def FileUpload(self, filepath, folder_id): 
        
        # Extract the file name out of the file path
        # Windows filepath with \\, change according to OS
        name = os.path.basename(filepath)
          
        # Find the MimeType of the file 
        mimetype = MimeTypes().guess_type(name)[0] 
          
        # create file metadata
        file_metadata = {'name': name, "parents": [folder_id]} 
  
        try: 
            media = MediaFileUpload(filepath, mimetype=mimetype, resumable=True)
            request = self.service.files().create(body=file_metadata, media_body=media, fields='id')
            response = None

            # Create a new file in the Drive storage 
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print ("Uploaded %d%%." % int(status.progress() * 100))
              
            print("File", name, "uploaded.")
          
        except Exception as e: 
            print ("Upload failed!", e)

    def GetFolderID(self, name, folder_id='root'):
        # request a list of first N files or 
        # folders with name and id from the API.
        try:
            page_token = None
            while True:
                results = self.service.files().list(
                    q="'{}' in parents".format(folder_id),
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token).execute()

                items = results.get('files', [])

                for item in items:
                    if item["name"].strip() == name.title():
                        return item["id"]

                page_token = results.get('nextPageToken', None)
                if page_token is None:
                    break
        except Exception as e:
            print ("Folder", name, "doesn't exist on Drive.", e)

    def GetFileID(self, name, folderID):
        try:
            page_token = None
            while True:
                results = self.service.files().list(
                    q="'{}' in parents".format(folderID),
                    fields="nextPageToken, files(id, name)",
                    pageToken=page_token).execute()
                items = results['files']

                for item in items:
                    if item["name"].strip() == name:
                        return item["id"]

                page_token = results.get('nextPageToken', None)
                if page_token is None:
                    break
        except Exception as e:
            print ("File", name, "doesn't exist on Drive.", e)


