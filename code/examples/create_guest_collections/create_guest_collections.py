"""
This is a Python script to automatically set up guest collections on the host specified as 'globus_host' in managed_guest_collections_config.
There is logic to prevent the creation of duplicate guest collections or permissions.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.
Any service user with write permissions to the mapped collection can run this script.

This script is used as the basis for a template in the Globus deployment Ansible, and this is used to create Python scripts which create
guest collections under each mapped collection.
"""
import argparse
import json
import os
import sys
import yaml
from typing import Any, Optional
from globus_sdk import GCSClient, TransferClient, TransferAPIError, GuestCollectionDocument, Scope, UserCredentialDocument, GCSAPIError
from globus_sdk.globus_app import ClientApp

# This service user ID must be authorised to write to the destination collection. UUID only - do not include "@clients.auth.globus.org"
CLIENT_ID = os.environ['GCS_CLI_CLIENT_ID']
CLIENT_SECRET = os.environ['GCS_CLI_CLIENT_SECRET']


def main() -> None:
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Python script to automatically create guest collections defined in managed guest collections configuration file',
        epilog='Requires Globus credentials for the service user in the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET'
        )

    parser.add_argument('managed_guest_collections_config_path', help="guest collection configuration JSON or YAML file")
    parser.add_argument('-d', '--delete', action='store_true', help="Flag to pre-delete any existing managed guest collections")

    args = parser.parse_args()

    with open(args.managed_guest_collections_config_path) as managed_guest_collections_config_file:
        if args.managed_guest_collections_config_path.lower().endswith(".json"):
            managed_guest_collections_config = json.load(managed_guest_collections_config_file)
        elif args.managed_guest_collections_config_path.lower().endswith(".yaml") or args.managed_guest_collections_config_path.lower().endswith(".yml"):
            managed_guest_collections_config = yaml.load(managed_guest_collections_config_file)
        else:
            raise(Exception(f"Unrecognised guest collection configuration file type: {args.managed_guest_collections_config_path}"))

    assert CLIENT_ID and CLIENT_SECRET, "GCS_CLI_CLIENT_ID and/or GCS_CLI_CLIENT_SECRET undefined"

    manage_guest_collections(managed_guest_collections_config, delete_guest_collections=args.delete)


def manage_guest_collections(managed_guest_collections_config: dict[str, dict[str, Any]], delete_guest_collections: bool=False) -> None:
    """
    Function to manage guest collections from a configuration dict.
    This function could be imported into another Python script and run with a different managed_guest_collections_config.

    :param managed_guest_collections_config: guest collection configuration dict
    :type managed_guest_collections_config: dict[dict[str, Any]]
    """
    client_app = ClientApp("guest_collection_manager", client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    gcs_client = GCSClient(managed_guest_collections_config['globus_host'], app=client_app)

    storage_gateways = list(gcs_client.get_storage_gateway_list())

    collections = list(gcs_client.get_collection_list())

    for storage_gateway in managed_guest_collections_config['storage_gateways']:
        storage_gateway_id = storage_gateway['storage_gateway_id']

        assert storage_gateway_id in [storage_gateway['id'] for storage_gateway in storage_gateways], f'Invalid Storage Gateway ID {storage_gateway_id}'

        ensure_user_credential(gcs_client, storage_gateway_id)

        for mapped_collection in storage_gateway['mapped_collections']:
            mapped_collection_id = mapped_collection['mapped_collection_id']

            assert mapped_collection_id in [collection['id'] for collection in collections if collection['collection_type'] == 'mapped'], f'Invalid Mapped Collection ID {mapped_collection_id}'

            if not storage_gateway.get('high_assurance'):
                attach_data_access_scope(gcs_client, mapped_collection_id)

            transfer_client = TransferClient(app=client_app).add_app_data_access_scope(mapped_collection_id)

            for guest_collection in mapped_collection['guest_collections']:

                display_name = guest_collection['display_name']
                base_path = guest_collection['base_path']
                public = guest_collection['public']

                create_directory(transfer_client, mapped_collection_id, base_path)

                found_collections = [
                    collection for collection in collections
                    if collection['collection_type'] == 'guest'
                    and collection['display_name'] == display_name
                    ]

                if found_collections:
                    print(f'Guest collection "{display_name}" already exists.')
                    if len(found_collections) == 1:
                        collection = found_collections[0]
                    else:
                        print(f'Unable to determine unique match for collection "{display_name}"')
                        exit(1)

                    # Unable to update base_path (immutable), so we can't change that
                    collection_request = GuestCollectionDocument(
                        public=public,
                        # collection_base_path=base_path,
                        display_name=display_name,
                        mapped_collection_id=mapped_collection_id,
                    )

                    print(f'Updating existing guest collection "{display_name}" with collection ID {collection["id"]}')
                    gcs_client.update_collection(collection['id'], collection_request)

                else:
                    collection_request = GuestCollectionDocument(
                        public=public,
                        collection_base_path=base_path,
                        display_name=display_name,
                        mapped_collection_id=mapped_collection_id,
                    )

                    collection = gcs_client.create_collection(collection_request)
                    print(f'Created new guest collection "{display_name}" with collection ID {collection["id"]}')

                for permission in guest_collection['permissions']:
                    # Create guest collection subdirectory if it doesn't already exist
                    if permission['path'] != '/':
                        create_directory(transfer_client, mapped_collection_id, base_path+permission['path'])

                    try:
                        result = transfer_client.add_endpoint_acl_rule(collection["id"], permission)
                        print(f'Added "{permission["permissions"]}" permissions to "{permission["path"]}" for {permission["principal_type"]} {permission["principal"]}')
                    except TransferAPIError as e:
                        if e.code == 'Exists':
                            print(f'Permissions already exist to "{permission["path"]}" for {permission["principal_type"]} {permission["principal"]}')
                        else:
                            raise e


def create_directory(transfer_client: TransferClient, mapped_collection_id: str, directory_path: str) -> None:
    """
    Create a directory under a mapped collection using a TransferClient
    """
    try:
        response = transfer_client.operation_mkdir(mapped_collection_id, directory_path)
        print(f'Created directory "{directory_path}" in collection {mapped_collection_id}')
    except TransferAPIError as e:
        if e.code == 'ExternalError.MkdirFailed.Exists':
            print(f'Directory "{directory_path}" already exists in collection {mapped_collection_id}')
        else:
            raise e


def attach_data_access_scope(gcs_client: GCSClient, collection_id: str) -> None:
    """
    Compose and attach a "data_access" scope for the supplied collection
    """
    endpoint_scopes = gcs_client.get_gcs_endpoint_scopes(gcs_client.endpoint_client_id)
    collection_scopes = gcs_client.get_gcs_collection_scopes(collection_id)

    manage_collections = Scope(endpoint_scopes.manage_collections)
    data_access = Scope(collection_scopes.data_access, optional=True)

    manage_collections.add_dependency(data_access)

    gcs_client.add_app_scope(manage_collections)


def ensure_user_credential(gcs_client: GCSClient, storage_gateway_id: str) -> None:
    """
    Ensure that the user has a user credential on the client.
    This is the mapping between Globus Auth (OAuth2) and the local system's permissions.
    """
    # Depending on the endpoint & storage gateway, this request document may need to
    # include more complex information such as a local username.
    # Consult with the endpoint owner for more detailed info on user mappings and
    # other particular requirements.
    req = UserCredentialDocument(storage_gateway_id=storage_gateway_id)
    try:
        gcs_client.create_user_credential(req)
    except GCSAPIError as err:
        # A user credential already exists, no need to create it.
        if err.http_status != 409:
            raise

if __name__ == '__main__':
    main()
