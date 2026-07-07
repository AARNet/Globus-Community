import os

# N.B: The following values will fail because they will only work with the AARNet service user
# You will need to set your own valid values.
SOURCE_COLLECTION_UUID = 'c0b773e5-7250-4ffd-88d8-da70215d6d35'  # Globus Secure Usage Data Guest Collection (source)
DESTINATION_COLLECTION_UUID = '3e6bb565-322e-4db8-a0dc-31ec4ace3a26'  # AARNet Secure Guest Collection (destination)

# N.B: Must include leading slashes in remote paths
DOWNLOAD_SOURCE_PATH = "/Australian Academic and Research Network (AARNet)-56107c7a-679f-11ea-960d-0afc9e7dd773/Globus_Usage_Transfer_Detail.csv"  # AARNet Usage Data CSV for testing
LOCAL_INPUT_FILE_NAME = "Globus_Usage_Transfer_Detail.csv"

LOCAL_OUTPUT_FILE_NAME = "Copied_Globus_Usage_Transfer_Detail.csv"
UPLOAD_DEST_PATH = "/AARNet (56107c7a-679f-11ea-960d-0afc9e7dd773)/Test_Upload_Globus_Usage_Transfer_Detail.csv"  # Test destination file

from globus_https_download_process_upload import GlobusHTTPSDownloadProcessUpload
import tempfile

def main():
    temp_dir = tempfile.gettempdir()
    local_input_file_path = os.path.join(temp_dir, LOCAL_INPUT_FILE_NAME)
    local_output_file_path = os.path.join(temp_dir, LOCAL_OUTPUT_FILE_NAME)

    ghdpu = GlobusHTTPSDownloadProcessUpload(SOURCE_COLLECTION_UUID, DESTINATION_COLLECTION_UUID, verbose=True)

    print(f"Remote file {DOWNLOAD_SOURCE_PATH} is {ghdpu.get_remote_file_size(DOWNLOAD_SOURCE_PATH) / 1048576:.3f} MB in size")

    print(f"Modification timestamp for remote file {DOWNLOAD_SOURCE_PATH} is {ghdpu.get_remote_file_mtime(DOWNLOAD_SOURCE_PATH).isoformat()}")

    ghdpu.download_file(DOWNLOAD_SOURCE_PATH, local_input_file_path)

    print(f"Checksum for downloaded file {local_input_file_path} is {ghdpu.get_file_checksum(local_input_file_path)}")

    print(f"Copying file {local_input_file_path} to {local_output_file_path} as a dummy processing operation")
    ghdpu.process_command(f"{'copy' if os.name == 'nt' else 'cp'} {local_input_file_path} {local_output_file_path}")  # Just copy the file for testing

    print(f"Removing local file {local_input_file_path}")
    os.remove(local_input_file_path)

    print(f"Checksum for file {local_output_file_path} is {ghdpu.get_file_checksum(local_output_file_path)}")

    ghdpu.upload_file(local_output_file_path, UPLOAD_DEST_PATH)

    print(f"Removing local file {local_output_file_path}")
    os.remove(local_output_file_path)

if __name__ == "__main__":
    main()
