# RouteViews Google Cloud Storage Client

[![PyPI version](https://badge.fury.io/py/routeviews-google-upload.svg)](https://badge.fury.io/py/routeviews-google-upload)

This project provides a (Python) client that takes a file and sends it to the Google Cloud Storage solution for [the Google+RouteViews project](https://github.com/routeviews/google-cloud-storage).

## Install

This solution is deployed to PyPI, so you can install it simply using the command `pip install 
routeviews-google-upload`.

    pip install routeviews-google-upload

## Examples

Below are a couple of examples showing how to use this tool.

> Run the tool with the `--help` argument to see all the expected and available arguments.

### Example: gRPC Served via a Cloud Run Instance, with Authentication

> This example works with our current production environment.  

This example covers the case when the targeted gRPC server is backed by a Google Cloud Run instance, and requires authentication.
For this workflow, we've added the `--key-file` argument.
This argument requires a Google Service Account Key file (tested with a JSON key).

    routeviews-google-upload --dest grpc.routeviews.org --key-file <your-key.json> --file routeviews.sfmix/bgpdata/2021.03/UPDATES/update.20210331.2345.bz2

### Example: Local "Debug::Echo" test server

If you are interested in running the solution end-to-end but don't have a gRPC target server in-mind, then you might 
be interested in running a local "debug echo gRPC server". 
Fortunately, we have baked a simple gRPC server into this package for testing!
To use this debug server, you'll need two terminals open -- one for the `server` and one for the `client`.

First, in the 'server terminal' window, run the `routeviews-google-upload-test-server` CLI tool:

    routeviews-google-upload-test-server
    RouteViews gRPC debug server is running...

Then, in the 'client terminal' window, you can run the upload tool with `--dest localhost:50051`.

> Expect the server to respond with a failure status (2) and an 'Error Message' that contains the entire request (including the file contents).

    routeviews-google-upload --dest localhost:50051 --file requirements.txt 
    Status: 2
    Error Message: DEBUG::ECHO::
        filename: "requirements.txt"
        md5: "1af62f45fdf90b6a1addfb2b86043acb"
        content: "grpcio==1.37.0\ngrpcio-tools==1.37.0\nprotobuf==3.15.8\nsix==1.15.0\n"
        project: ROUTEVIEWS

