# This file provides utilities for performing HTTP requests and downloading
# content from the internet.

# Imports

import urllib.request
import urllib.response
import json
import zipfile
import os

# Define the 'Response' class that holds basic information about an HTTP response

class Response:
    # 'res' is the underlying urllib response object
    def __init__(self, res: urllib.response.addinfourl):
        self.status_code = res.getcode() # the HTTP status code (ex: 200 - success, 400 - client error, etc)
        self.headers = dict(res.getheaders()) # the HTTP response headers
        self.text = res.read().decode('utf-8') # the response body decoded in UTF 8

    # Define a 'json' function which converts the response body to a Python dictionary
    # that can be interacted with using Python code
    def json(self):
        # Return the dictionary object by using the 'json' native module to parse the raw text body
        return json.loads(self.text)

# Define the 'get' function that takes a URL and returns an HTTP response
def get(url: str) -> Response:
    # Define 'req' as the request object with the specified URL and the Mozilla/5.0 user-agent
    # The user-agent is changed to Mozilla/5.0 because the default python-urllib user-agent is
    # blocked by certain APIs
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Define 'res' as the response object produced by urllib
    res = urllib.request.urlopen(req)
    # Return the underlying response wrapped in our custom Response class
    return Response(res)

# Define the 'download' function that takes a URL, a file path, and an optional boolean 'unzip' flag that defaults to false
def download(url: str, path: str, unzip: bool = False):
    # Set 'target_path' to the 'path' argument
    target_path = path
    # Check if the 'unzip' flag is true
    if unzip:
        # Update 'target_path' to a modified version of 'path' prefixed with '.temp.zip'
        target_path = f"{path}.temp.zip"

    # Use urllib to access the content at the URL and open the target path in write binary (wb) mode
    with urllib.request.urlopen(url) as res, open(target_path, 'wb') as file:
        # Write the response body content to the file
        file.write(res.read())

    # Check if the 'unzip' flag is true
    if unzip:
        # Using the zipfile module, access the file at the target_path as zip_file
        with zipfile.ZipFile(target_path) as zip_file:
            # Extract the contents of the zip_file into the 'path' argument
            zip_file.extractall(path)
        # Delete the file at the 'target_path' or what was a temporary zip file
        os.remove(target_path)