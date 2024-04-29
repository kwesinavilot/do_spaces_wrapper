# DigitalOcean Spaces Wrapper

This Python class provides a convenient wrapper around the `boto3` package for interacting with DigitalOcean Spaces, a cloud object storage service provided by DigitalOcean that's similar to AWS S3.

This wrapper offers a high-level, Pythonic API that abstracts away the low-level details of the underlying `boto3` library, making it easier for developers to integrate DigitalOcean Spaces functionality into their applications. 

This wrapper simplifies common operations such as uploading, downloading, listing, and managing objects and directories within DigitalOcean Spaces buckets.

Additionally, **the wrapper includes built-in support for AWS S3**, allowing seamless integration with both DigitalOcean Spaces and Amazon S3 storage services.

For context, this wrapper was created out of the frustrations experienced when working with the DigitalOcean Spaces API on the UruBytes project backend. I decided to create this wrapper to simplify the process of interacting with DigitalOcean Spaces. 

I may create a package around it in the future, but for now, this wrapper serves as a convenient and reliable way to interact with DigitalOcean Spaces.

## Features
- Connect to a DigitalOcean Spaces bucket
- List all available buckets
- Create a new bucket
- Create folders (directories) within a bucket
- Check if a folder or file exists
- Upload, update, and delete files
- Delete folders and their contents
- List folders within a bucket or within a specific prefix
- List contents (files and folders) of a specific folder
- Stream file contents
- Read files in chunks
- Perform multipart uploads for large files
- Extract filenames from file paths

## Prerequisites

Before using this wrapper, make sure you have the following:

- Python 3.x installed on your system
- `boto3` package installed (`pip install boto3`)
- `botocore` package installed (`pip install botocore`)
- DigitalOcean Spaces credentials set in your environment

## Environment Variables

The wrapper class expects the following environment variables to be set with your DigitalOcean Spaces credentials:

- `DO_SPACES_KEY_ID`: Your DigitalOcean Spaces Access Key ID
- `DO_SPACES_SECRET_KEY`: Your DigitalOcean Spaces Secret Access Key
- `DO_SPACES_BUCKET_NAME`: The name of your DigitalOcean Spaces bucket
- `DO_SPACES_REGION`: The region where your DigitalOcean Spaces bucket is located
- `DO_SPACES_ORIGIN_URL`: The origin URL of your DigitalOcean Spaces bucket

## Usage

1. Import the `DOSpacesWrapper` class:

```python
from DOSpacesWrapper import DOSpacesWrapper
```

2. Create an instance of the `DOSpacesWrapper` class:

```python
spaces_wrapper = DOSpacesWrapper()
```

3. Use the provided methods to perform various operations:

### `connectToBucket(bucketName):`

Establishes a connection to the DigitalOcean Spaces bucket specified by the `DO_SPACES_BUCKET_NAME` environment variable.

```python
# defaults to bucket name set in environment
spaces_wrapper.connectToBucket()

# specify bucket name
spaces_wrapper.connectToBucket("my-bucket")
```

### `createFolder(folderPath)`

Creates a folder (directory) within the DigitalOcean Spaces bucket.

- `folderPath` (str): The path of the folder to be created.

```python
folder_path = "sources/orgID/static"
spaces_wrapper.createFolder(folder_path)
```

### `folderExists(folderPath)`

Checks if a folder exists within the DigitalOcean Spaces bucket.

- `folderPath` (str): The path of the folder to check.
- Returns `True` if the folder exists, `False` otherwise.

```python
folder_path = "sources/orgID/static"
exists = spaces_wrapper.folderExists(folder_path)
print(exists)
```

### `fileExists(filePath)`

Checks if a file exists within the DigitalOcean Spaces bucket.

- `filePath` (str): The path of the file to check.
- Returns `True` if the file exists, `False` otherwise.

```python
file_path = "sources/orgID/static/file.txt"
exists = spaces_wrapper.fileExists(file_path)
print(exists)
```

### `uploadFile(filePath, fileData)`

Uploads a file to the DigitalOcean Spaces bucket.

- `filePath` (str): The path where the file should be uploaded.
- `fileData` (bytes or file-like object): The file data to be uploaded.

```python
file_path = "sources/orgID/static/file.txt"
with open("local_file.txt", "rb") as file:
    file_data = file.read()
    spaces_wrapper.uploadFile(file_path, file_data)
```

### `updateFile(filePath, fileData)`

Updates a file in the DigitalOcean Spaces bucket.

- `filePath` (str): The path of the file to be updated.
- `fileData` (bytes or file-like object): The new file data.

```python
file_path = "sources/orgID/static/file.txt"
with open("updated_file.txt", "rb") as file:
    file_data = file.read()
    spaces_wrapper.updateFile(file_path, file_data)
```

### `deleteFile(filePath)`

Deletes a file from the DigitalOcean Spaces bucket.

- `filePath` (str): The path of the file to be deleted.

```python
file_path = "sources/orgID/static/file.txt"
spaces_wrapper.deleteFile(file_path)
```

### `deleteFolder(folderPath)`

Deletes a folder and its contents from the DigitalOcean Spaces bucket.

- `folderPath` (str): The path of the folder to be deleted.

```python
folder_path = "sources/orgID/static"
spaces_wrapper.deleteFolder(folder_path)
```

### `listFolders(prefix='')`

Lists all folders within the DigitalOcean Spaces bucket or a specified prefix.

- `prefix` (str, optional): The prefix to filter the folder list. Defaults to an empty string.
- Returns a list of folder paths.

```python
folders = spaces_wrapper.listFolders()
print(folders)

# Filter by prefix
folders = spaces_wrapper.listFolders(prefix="sources/")
print(folders)
```

### `listFolderContents(folderPath)`

Lists the contents (files and folders) within a specific folder in the DigitalOcean Spaces bucket.

- `folderPath` (str): The path of the folder to list contents for.
- Returns a list of file and folder paths within the specified folder.

```python
folder_path = "sources/orgID/static"
contents = spaces_wrapper.listFolderContents(folder_path)
print(contents)
```

Here's a somewhat practical example of how to use the DOSpacesWrapper class:
```python
import os
from DOSpacesWrapper import DOSpacesWrapper

# Set environment variables
os.environ['DO_SPACES_REGION'] = 'your_region'
os.environ['DO_SPACES_KEY_ID'] = 'your_access_key_id'
os.environ['DO_SPACES_SECRET_KEY'] = 'your_secret_access_key'
os.environ['DO_SPACES_BUCKET_NAME'] = 'your_bucket_name'

# Create an instance of DOSpacesWrapper
spaces = DOSpacesWrapper()

# Connect to the default bucket
spaces.connectToBucket()

# Upload a file
file_path = 'path/to/file.txt'
file_data = b'This is the file content.'
spaces.uploadFile(file_path, file_data)

# List folders in the bucket
folders = spaces.listFolders()
print(folders)

# Get the actual filenames from a list of file paths
file_paths = ['path/to/file1.txt', 'path/to/folder/file2.pdf']
filenames = spaces.getActualFileNames(file_paths)
print(filenames)
```

## Error Handling

The wrapper class provides basic error handling by catching `ClientError` exceptions thrown by the boto3 library. If an error occurs during an operation, an error message is printed to the console. You can modify the error handling behavior according to your needs.

## Contributions

Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
The `DOSpacesWrapper` is released under the MIT License.