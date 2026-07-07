import hashlib
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib import request, error
from urllib.parse import quote

import pytz
from globus_sdk import (
    AuthClient,
    ClientApp,
    ConfidentialAppAuthClient,
    GlobusAppConfig,
    Scope,
    TransferClient,
)
from globus_sdk.token_storage import JSONTokenStorage


class GlobusHTTPSDownloadProcessUpload:

    @staticmethod
    def get_file_checksum(file_path: str | Path, algorithm: str = "sha256") -> str:
        """
        Compute hash of file contents.

        :param file_path:
        :param algorithm:
        :return: str
        """
        # Open the file in binary read mode ('rb')
        with open(file_path, "rb") as f:
            # Generate the hash digest object
            digest_obj = hashlib.file_digest(f, algorithm)
        # Return the readable hexadecimal string
        return digest_obj.hexdigest()

    def get_https_details(
            self,
            guest_collection_uuids: list[str],
    ) -> dict[str, tuple[str, Any]]:
        """
        Function to return access token for all known guest collections keyed by base URL
        Args:
            guest_collection_uuids: list[str]

        Returns: dict[str, tuple[str, Any]] - dict keyed by guest collection UUID containing base URL and access token for all transfer file URLs
        """
        https_details = {}
        for guest_collection_uuid in guest_collection_uuids:
            https_server = self.transfer_client.get_endpoint(guest_collection_uuid)["https_server"]

            token_response = self.confidential_client.oauth2_client_credentials_tokens(
                requested_scopes=[Scope(f"https://auth.globus.org/scopes/{guest_collection_uuid}/https"), ]
            )

            https_details[guest_collection_uuid] = {
                "base_url": https_server,
                "access_token": token_response.by_scopes[f"https://auth.globus.org/scopes/{guest_collection_uuid}/https"][
                    "access_token"]
            }

        return https_details

    def get_remote_file_mtime(
            self,
            remote_source_file_path: str,
            source_collection_uuid: Optional[str] = None
    ) -> Optional[datetime]:
        source_collection_uuid = source_collection_uuid or self.source_collection_uuid

        mod_time = None
        try:
            # Fetch file metadata
            response = self.transfer_client.operation_stat(source_collection_uuid, path=str(remote_source_file_path))

            # Extract the mtime from the metadata dict
            mod_time = datetime.strptime(response.data["last_modified"], "%Y-%m-%d %H:%M:%S%z").replace(tzinfo=pytz.utc)
        except Exception as e:
            print(f"Failed to get file modification time for {remote_source_file_path}: {e}")

        return mod_time

    def __init__(
            self,
            source_collection_uuid: str,
            dest_collection_uuid: str,
            verbose: bool = False,
    ):
        self.source_collection_uuid = source_collection_uuid
        self.dest_collection_uuid = dest_collection_uuid
        self.verbose = verbose

        service_user = {
            "UUID": os.environ['GCS_CLI_CLIENT_ID'],
            "SECRET": os.environ['GCS_CLI_CLIENT_SECRET'],
        }

        self.confidential_client = ConfidentialAppAuthClient(
            service_user['UUID'],
            service_user['SECRET']
        )

        _jsonfile_token = JSONTokenStorage(filepath="/tokens/globus_tokens.json")
        _appconfig = GlobusAppConfig(token_storage=_jsonfile_token)
        self.client_app = ClientApp(
            "globus_dashboard_data_ingester",
            login_client=self.confidential_client,
            config=_appconfig
        )

        self.transfer_client = TransferClient(
            app=self.client_app,
        )

        self.auth_client = AuthClient(app=self.client_app)

        self.https_details = self.get_https_details([self.source_collection_uuid, self.dest_collection_uuid])

    def get_remote_file_size(
            self,
            remote_source_file_path: str,
            source_collection_uuid: Optional[str] = None
    ):
        source_collection_uuid = str(source_collection_uuid or self.source_collection_uuid)
        https_details = self.https_details[source_collection_uuid]

        download_url = f"{https_details['base_url']}{quote(remote_source_file_path)}"

        headers = {'Authorization': f'Bearer {https_details["access_token"]}'}
        head_request = request.Request(str(download_url), headers=headers, method='HEAD')

        content_length = 0
        try:
            head_response = request.urlopen(head_request)
            content_length = int(head_response.headers.get('Content-Length'))
        except Exception as e:
            print(f'Failed to read size of {download_url}. Exception: {e}')

        return content_length

    def download_file(
            self,
            remote_source_file_path: str,
            local_dest_file_path: Path | str,
            source_collection_uuid: Optional[str] = None
    ):
        source_collection_uuid = str(source_collection_uuid or self.source_collection_uuid)
        https_details = self.https_details[source_collection_uuid]

        download_url = f"{https_details['base_url']}{quote(remote_source_file_path)}"

        headers = {'Authorization': f'Bearer {https_details["access_token"]}'}

        if self.verbose:
            print(f"Downloading file {local_dest_file_path} from {download_url}")

        with open(local_dest_file_path, 'wb') as dest_file:

            download_request = request.Request(download_url, headers=headers)

            # Open the URL using the authenticated request
            try:
                with request.urlopen(download_request) as response:
                    # Read the response data (in bytes)
                    file_content = response.read()

                    # Write the content to the local file in binary mode ('wb')
                    dest_file.write(file_content)

                    if self.verbose:
                        print(f"File downloaded successfully")
            except error.HTTPError as e:
                print(f"Download failed. Error: {e.code} - {e.reason}")
            except error.URLError as e:
                print(f"Network error: {e.reason}")

    def process_command(
            self,
            command: str
    ):
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,  # Captures stdout and stderr
                text=True,  # Returns strings instead of bytes
                check=True  # Raises an exception if the command fails
            )

            # Print the command's terminal output
            if self.verbose:
                print(result.stdout)

        except subprocess.CalledProcessError as e:
            print(f'Command "{command}" failed with error:', e.stderr)

    def upload_file(
            self,
            local_source_file_path: Path | str,
            remote_dest_file_path: Path | str,
            dest_collection_uuid: Optional[str] = None,
    ):
        dest_collection_uuid = str(dest_collection_uuid or self.dest_collection_uuid)
        https_details = self.https_details[dest_collection_uuid]

        upload_url = f"{https_details['base_url']}{quote(remote_dest_file_path)}"

        if self.verbose:
            print(f"Uploading file {local_source_file_path} to {upload_url}")

        headers = {
            'Authorization': f'Bearer {https_details["access_token"]}',
            "Content-Type": "application/octet-stream",
        }

        with open(local_source_file_path, 'rb') as local_file:
            file_data = local_file.read()

        upload_request = request.Request(
            upload_url,
            data=file_data,
            method='PUT',
            headers=headers
        )

        # Execute the upload
        try:
            with request.urlopen(upload_request) as response:
                if response.status == 200:
                    print("File uploaded successfully.")
        except error.HTTPError as e:
            print(f"Upload of file {local_source_file_path} to {upload_url} failed. Error: {e.code} - {e.reason}")
        except error.URLError as e:
            print(f"Network error uploading file {local_source_file_path} to {upload_url}: {e.reason}")
