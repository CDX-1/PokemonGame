# This file provides utilities for performing HTTP requests and downloading
# content from the internet.

# Imports

import urllib.request
import urllib.response
import json
import zipfile
import os
import ssl

# Create an SSL context object for securing HTTP requests

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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
    res = urllib.request.urlopen(req, context=ssl_context)
    # Return the underlying response wrapped in our custom Response class
    return Response(res)

# Define the 'download' function that takes a URL, a file path, and an optional boolean 'unzip' flag that defaults to false
def download(url: str, path: str, unzip: bool = False, use_ssl: bool = True):
    # Set 'target_path' to the 'path' argument
    target_path = path
    # Check if the 'unzip' flag is true
    if unzip:
        # Update 'target_path' to a modified version of 'path' prefixed with '.temp.zip'
        target_path = f"{path}.temp.zip"

    # Define 'resolve_ssl_context' function to handle assignment of 'use_ssl' variable and
    # return the SSL context object
    def resolve_ssl_context():
        # Check if using SSL
        if use_ssl:
            # Return SSL Context object
            return ssl_context
        else:
            # Return none
            return None

    # Using urllib, create a request body to prepare to send the request
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Create parent directories for target path if not existing
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    # Use urllib to access the content at the URL and open the target path in write binary (wb) mode
    with urllib.request.urlopen(req, context=resolve_ssl_context()) as res, open(target_path, 'wb') as file:
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