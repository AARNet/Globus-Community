# globus_https_download_process_upload

This is an example script to download, process, and upload files via HTTPS instead of via Globus transfers. 
This solution can be run anywhere and does not require a Globus Connect Endpoint or a Globus Compute Endpoint on the host.

It was written to help with a task where a subscription manager needed to automate the download of a Globus usage report
CSV file (`Globus_Usage_Transfer_Detail.csv`) from their subscription subdirectory in the Globus Secure Usage Data Guest 
Collection run a custom anonymisation script on it, and then upload the resulting file to their subdirectory in the 
AARNet Secure Guest Collection.

__Please note that the HTTPS download/upload is not as robust as the Globus transfer mechanism, but it is generally fine 
for smaller files (say, less than 1GB).__ You may wish to implement retries around the upload/download calls.

The script is shared in the Globus Community Australasia site because it may be useful in other scenarios. In particular,
you may find the derivation of the URLs and access tokens interesting.

Please contact AARNet if you have any questions, feedback, or suggestions.

## Prerequisites
You will need to define a service user with appropriate read/write permissions on the download/upload collections. For
the above usage scenario, you will need to add the service user to your subscription as a subscription manager so that 
it can read from the subscription subdirectory in the Globus Secure Usage Data Guest Collection, and you will need to ask 
AARNet to add the user to the users allowed to write to your subdirectory in the AARNet Secure Guest Collection.
Please see the "Registering a Client App" in the 
[Advanced Globus Workshop](https://aarnet.github.io/Globus-Community/globus-community-australasia/workshops/advanced_globus_workshop/) 
page for instructions.

The service user credentials will need to be stored in the following environment variables. 
__N.B: The script will error if these are not defined.__

```bash
GCS_CLI_CLIENT_ID="<your service user UUID>"
GCS_CLI_CLIENT_SECRET="<your service user secret>"
```

In the `globus_https_download_process_upload.__main__.py` module, you will find a bunch of hard-coded values for testing.
__Note that the script will fail with the current variables because you will have neither read nor write access to either 
of the subdirectories referenced in the guest collections., so you will need to set your own values.__ 
Please contact AARNet if you require assistance.
These are the variables you will need to customise
```python
SOURCE_COLLECTION_UUID = 'c0b773e5-7250-4ffd-88d8-da70215d6d35'  # Globus Secure Usage Data Guest Collection (source)
DESTINATION_COLLECTION_UUID = '3e6bb565-322e-4db8-a0dc-31ec4ace3a26'  # AARNet Secure Guest Collection (destination)

# N.B: Must include leading slashes in remote paths
DOWNLOAD_SOURCE_PATH = "/Australian Academic and Research Network (AARNet)-56107c7a-679f-11ea-960d-0afc9e7dd773/Globus_Usage_Transfer_Detail.csv"  # AARNet Usage Data CSV for testing
LOCAL_INPUT_FILE_NAME = "Globus_Usage_Transfer_Detail.csv"

LOCAL_OUTPUT_FILE_NAME = "Copied_Globus_Usage_Transfer_Detail.csv"
UPLOAD_DEST_PATH = "/AARNet (56107c7a-679f-11ea-960d-0afc9e7dd773)/Test_Upload_Globus_Usage_Transfer_Detail.csv"  # Test destination file
```

The script is invoked using:

```bash
python -m globus_https_download_process_upload 
```
If your service user permissions and file paths are correct, then you will see output something like this when you run the script:
```
> python -m globus_https_download_process_upload 
Remote file /Australian Academic and Research Network (AARNet)-56107c7a-679f-11ea-960d-0afc9e7dd773/Globus_Usage_Transfer_Detail.csv is 86.938 MB in size
Modification timestamp for remote file /Australian Academic and Research Network (AARNet)-56107c7a-679f-11ea-960d-0afc9e7dd773/Globus_Usage_Transfer_Detail.csv is 2026-07-06T17:19:08+00:00
Downloading file /tmp/Globus_Usage_Transfer_Detail.csv from https://g-dc7310.72412.75bc.data.globus.org/Australian%20Academic%20and%20Research%20Network%20%28AARNet%29-56107c7a-679f-11ea-960d-0afc9e7dd773/Globus_Usage_Transfer_Detail.csv
File downloaded successfully
Checksum for downloaded file /tmp/Globus_Usage_Transfer_Detail.csv is 424a9e1a0888ce0923f86bc05b75d64bd84129fc61c305b67fa8f6a783de5768
Copying file /tmp/Globus_Usage_Transfer_Detail.csv to /tmp/Copied_Globus_Usage_Transfer_Detail.csv as a dummy processing operation
        1 file(s) copied.

Removing local file /tmp/Globus_Usage_Transfer_Detail.csv
Checksum for file /tmp/Copied_Globus_Usage_Transfer_Detail.csv is 424a9e1a0888ce0923f86bc05b75d64bd84129fc61c305b67fa8f6a783de5768
Uploading file /tmp/Copied_Globus_Usage_Transfer_Detail.csv to https://g-02a7b6.0b2e93.03c0.gaccess.io/AARNet%20%2856107c7a-679f-11ea-960d-0afc9e7dd773%29/Test_Upload_Globus_Usage_Transfer_Detail.csv
File uploaded successfully.
Removing local file /tmp/Copied_Globus_Usage_Transfer_Detail.csv

Process finished with exit code 0
```