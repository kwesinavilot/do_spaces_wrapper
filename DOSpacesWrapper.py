import os
import boto3
from botocore.exceptions import ClientError
from botocore.config import Config

class DOSpacesWrapper:
    def __init__(self):
        """
        Initializes the DOSpacesWrapper object with the necessary configurations for interacting with DigitalOcean Spaces.
        """
        self.session = boto3.session.Session()
        self.client = self.session.client(
            's3',
            region_name=os.getenv('DO_SPACES_REGION'),
            endpoint_url=f"https://nyc3.digitaloceanspaces.com",
            aws_access_key_id=os.getenv('DO_SPACES_KEY_ID'),
            aws_secret_access_key=os.getenv('DO_SPACES_SECRET_KEY'),
            config=Config(s3={'addressing_style': 'virtual'}),
            # verify=False
        )
        self.signature_version='s3v4'
        self.use_ssl=True
        self.file_overwrite=True
        self.aws_media_location='storage'
        self.object_parameters={'CacheControl': 'max-age=86400'}
        self.default_acl='public-read-write'
        self.bucket_name = os.getenv('DO_SPACES_BUCKET_NAME')
        self.querystring_expire = 3600
        self.querystring_auth = True
        self.max_memory_size = 0 # don't roll over
        self.retries = {
            'max_attempts': 5,
            'mode': 'standard'
        }
        self.encryption_scheme = {'ServerSideEncryption': 'AES256'}

    def connectToBucket(self, bucketName=None):
        """Connects to a DO Spaces bucket.

        Args:
            bucketName: The name of the bucket to connect to (optional).
                If not provided, uses the bucket name from the class initialization.

        Raises:
            ClientError: If an error occurs while connecting to the bucket.
        """
        if bucketName is None:
            bucketName = self.bucket_name

        try:
            self.client.head_bucket(Bucket=bucketName)
            print(f"Successfully connected to bucket: {bucketName}")

            return bucketName
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"Bucket '{bucketName}' does not exist.")
            else:
                print(f"An error occurred: {e}")

    def listBuckets(self):
        """
        Lists all DigitalOcean Spaces buckets.
        """
        try:
            response = self.client.list_buckets()
            print("DigitalOcean Spaces buckets:")
            for bucket in response['Buckets']:
                print(f"  {bucket['Name']}")
        except ClientError as e:
            print(f"An error occurred: {e}")

    def createBucket(self):
        """
        Creates a new DigitalOcean Spaces bucket.
        """
        try:
            self.client.create_bucket(Bucket=self.bucket_name)
            print(f"Successfully created bucket: {self.bucket_name}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                print(f"Bucket '{self.bucket_name}' already exists.")
            else:
                print(f"An error occurred: {e}")

    def createFolder(self, folderPath):
        """
        Creates a folder (directory) within the DigitalOcean Spaces bucket.

        Args:
            folderPath (str): The path of the folder to be created.
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=f"{folderPath}/", Body=b'')
            print(f"Successfully created folder: {folderPath}")
        except ClientError as e:
            print(f"An error occurred while creating the folder: {e}")

    def folderExists(self, folderPath):
        """
        Checks if a folder exists within the DigitalOcean Spaces bucket.

        Args:
            folderPath (str): The path of the folder to check.

        Returns:
            bool: True if the folder exists, False otherwise.
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=f"{folderPath}/")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            else:
                print(f"An error occurred while checking folder existence: {e}")
                return False

    def fileExists(self, filePath):
        """
        Checks if a file exists within the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path of the file to check.

        Returns:
            bool: True if the file exists, False otherwise.
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=filePath)
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return False
            else:
                print(f"An error occurred while checking file existence: {e}")
                return False

    def uploadFile(self, filePath, fileData):
        """
        Uploads a file to the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path where the file should be uploaded.
            fileData (bytes or file-like object): The file data to be uploaded.
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=filePath, Body=fileData)
            print(f"Successfully uploaded file: {filePath}")
        except ClientError as e:
            print(f"An error occurred while uploading the file: {e}")

    def updateFile(self, filePath, fileData):
        """
        Updates a file in the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path of the file to be updated.
            fileData (bytes or file-like object): The new file data.
        """
        try:
            self.client.put_object(Bucket=self.bucket_name, Key=filePath, Body=fileData)
            print(f"Successfully updated file: {filePath}")
        except ClientError as e:
            print(f"An error occurred while updating the file: {e}")

    def deleteFile(self, filePath):
        """
        Deletes a file from the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path of the file to be deleted.
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=filePath)
            print(f"Successfully deleted file: {filePath}")
        except ClientError as e:
            print(f"An error occurred while deleting the file: {e}")

    def deleteFolder(self, folderPath):
        """
        Deletes a folder and its contents from the DigitalOcean Spaces bucket.

        Args:
            folderPath (str): The path of the folder to be deleted.
        """
        try:
            paginator = self.client.get_paginator('list_objects')
            operation_parameters = {'Bucket': self.bucket_name, 'Prefix': folderPath}
            page_iterator = paginator.paginate(**operation_parameters)

            for page in page_iterator:
                if 'Contents' in page:
                    delete_keys = [{'Key': obj['Key']} for obj in page['Contents']]
                    self.client.delete_objects(Bucket=self.bucket_name, Delete={'Objects': delete_keys})

            print(f"Successfully deleted folder: {folderPath}")
        except ClientError as e:
            print(f"An error occurred while deleting the folder: {e}")

    def listFolders(self, prefix=''):
        """
        Lists all folders within the DigitalOcean Spaces bucket or a specified prefix.

        Args:
            prefix (str, optional): The prefix to filter the folder list. Defaults to ''.

        Returns:
            list: A list of folder paths.
        """
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            operation_parameters = {'Bucket': self.bucket_name, 'Prefix': prefix, 'Delimiter': '/'}
            page_iterator = paginator.paginate(**operation_parameters)

            folders = []
            for page in page_iterator:
                if 'CommonPrefixes' in page:
                    folders.extend(prefix.replace(prefix, '') for prefix in page['CommonPrefixes'])

            return folders
        except ClientError as e:
            print(f"An error occurred while listing folders: {e}")
            return []

    def listFolderContents(self, folderPath):
        """
        Lists the contents (files and folders) within a specific folder in the DigitalOcean Spaces bucket.

        Args:
            folderPath (str): The path of the folder to list contents for.

        Returns:
            list: A list of file and folder paths within the specified folder.
        """
        print("Listing folder contents of ", folderPath)

        # check if the folder exists first
        if not self.folderExists(folderPath):
            raise Exception(f"Folder {folderPath} does not exist")

        try:
            paginator = self.client.get_paginator('list_objects_v2')
            operation_parameters = {'Bucket': self.bucket_name, 'Prefix': f'{folderPath}/', 'Delimiter': '/'}
            page_iterator = paginator.paginate(**operation_parameters)

            contents = []
            for page in page_iterator:

                if 'Contents' in page:
                    for object in page['Contents']:
                        key = object['Key']

                        if key != f'{folderPath}/':  # Exclude the folder path itself
                            contents.append(key)
                
                if 'CommonPrefixes' in page:
                    for prefix in page['CommonPrefixes']:

                        if prefix['Prefix'] != f'{folderPath}/':   # Exclude the folder path itself
                            contents.append(prefix['Prefix'])

            return contents
        except ClientError as e:
            print(f"An error occurred while listing folder contents: {e}")
            return []

    def streamFileContent(self, filePath, chunkSize=8192):
        """
        Streams the content of a file from the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path of the file to stream.
            chunkSize (int, optional): The size of each chunk in bytes. Defaults to 8192.

        Yields:
            bytes: The next chunk of the file content.
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=filePath)
            stream = response['Body']._raw_stream
            while True:
                chunk = stream.read(chunkSize)
                if not chunk:
                    break
                yield chunk
        except ClientError as e:
            print(f"An error occurred while streaming the file content: {e}")

    def readFile(self, filePath, chunkSize=8388608):
        """
        Reads data from a file in the DigitalOcean Spaces bucket.

        Args:
            filePath (str): The path of the file to read from.
            chunkSize (int, optional): The size of each chunk in bytes. Defaults to 8388608 (8MB).

        Yields:
            bytes: The next chunk of the file content.
        """
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=filePath)
            
            stream = response['Body']._raw_stream
            
            while True:
                chunk = stream.read(chunkSize)
                
                if not chunk:
                    break
                yield chunk
        except ClientError as e:
            print(f"An error occurred while reading from the file: {e}")

    def multipartUpload(self, filePath):
        """
        Initiates a multipart upload and returns an upload ID.

        Args:
            filePath (str): The path of the file for which the multipart upload will be initiated.

        Returns:
            str: The upload ID for the initiated multipart upload.
        """
        try:
            response = self.client.create_multipart_upload(Bucket=self.bucket_name, Key=filePath)
            return response['UploadId']
        except ClientError as e:
            print(f"An error occurred while initiating the multipart upload: {e}")
            return None
        
    def uploadFileChunked(self, filePath, fileData, chunkSize=8388608):  # 8MB chunks
        """
        Uploads a file to the DigitalOcean Spaces bucket in chunks.

        Args:
            filePath (str): The path where the file should be uploaded.
            fileData (bytes or file-like object): The file data to be uploaded.
            chunkSize (int, optional): The size of each chunk in bytes. Defaults to 8388608 (8MB).
        """
        try:
            if hasattr(fileData, 'read'):  # If fileData is a file-like object
                parts = []
                part_number = 1
                upload_id = self.client.create_multipart_upload(Bucket=self.bucket_name, Key=filePath)['UploadId']
                
                while True:
                    chunk = fileData.read(chunkSize)
                    if not chunk:
                        break
                    
                    part = self.client.upload_part(Body=chunk, Bucket=self.bucket_name, Key=filePath, PartNumber=part_number, UploadId=upload_id)
                    parts.append({'PartNumber': part_number, 'ETag': part['ETag']})
                    part_number += 1
                
                self.client.complete_multipart_upload(Bucket=self.bucket_name, Key=filePath, MultipartUpload={'Parts': parts}, UploadId=upload_id)
            else:  # If fileData is bytes
                self.client.put_object(Bucket=self.bucket_name, Key=filePath, Body=fileData)
            
            print(f"Successfully uploaded file: {filePath}")
        except ClientError as e:
            print(f"An error occurred while uploading the file: {e}")

    def getActualFileNames(filePaths):
        """Extracts filenames from a list of file paths.

        Args:
            file_paths (list): A list of file paths.

        Returns:
            list: A list containing only the filenames extracted from the paths.
        """
        filenames = []

        for path in filePaths:
            # Split the path and extract the last element (filename)
            filename = path.split("/")[-1]
            filenames.append(filename)
            
        return filenames