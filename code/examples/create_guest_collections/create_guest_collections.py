"""
This is a Python script to automatically set up guest collections on the host specified as
'globus_host' as configured in managed_guest_collections_config.
There is logic to prevent the creation of duplicate guest collections or permissions.

The Globus credentials for the service user must be provided via the environment variables
GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.
Any service user with write permissions to the mapped collection can run this script.

This script is used as the basis for a template in the Globus deployment Ansible, and this
is used to create Python scripts which create
guest collections under each mapped collection.
"""
import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from typing import Any, Optional
from globus_sdk import GCSClient, TransferClient, TransferAPIError, GuestCollectionDocument, \
    Scope, UserCredentialDocument, GCSAPIError
from globus_sdk.globus_app import ClientApp
from pprint import pprint

def manage_guest_collections(
    managed_guest_collections_config: dict[str, dict[str, Any]],
    client_id: str,
    client_secret: str,
    purge_guest_collections: bool=False,
    ) -> None:
    """
    Function to manage guest collections from a configuration dict.
    This function could be imported into another Python script and run with a different
    managed_guest_collections_config.

    Args:
        managed_guest_collections_config (dict[str, dict[str, Any]]): guest
            collection configuration dict
        client_id (str): UUID of service user.
        client_secret (str) Secret for service user.
        purge_guest_collections (bool): Boolean flag indicating whether to
            delete any existing guest collections NOT defined in managed_guest_collections_config.
            Default = False
    """
    assert client_id and client_secret, 'Please specify client_id and client_secret'

    client_app = ClientApp("guest_collection_manager", client_id=client_id, client_secret=client_secret)
    gcs_client = GCSClient(managed_guest_collections_config['globus_host'], app=client_app)

    storage_gateways = list(gcs_client.get_storage_gateway_list())
    # print('storage_gateways:')
    # pprint(storage_gateways)

    # Get all collections on this host
    collections = [
        collection
        for collection in gcs_client.get_collection_list()
        if collection['domain_name'].endswith(managed_guest_collections_config['globus_host'])
    ]
    # print('collections:')
    # pprint(collections)

    for storage_gateway_config in managed_guest_collections_config['storage_gateways']:
        storage_gateway_id = storage_gateway_config['storage_gateway_id']

        assert storage_gateway_id in [storage_gateway['id'] for storage_gateway in storage_gateways], f'Invalid Storage Gateway ID {storage_gateway_id}'

        ensure_user_credential(gcs_client, storage_gateway_id)

        for mapped_collection_config in storage_gateway_config['mapped_collections']:
            mapped_collection_id = mapped_collection_config['mapped_collection_id']

            assert mapped_collection_id in [mapped_collection['id'] for mapped_collection in collections if mapped_collection['collection_type'] == 'mapped'], \
                f'Invalid Mapped Collection ID {mapped_collection_id}'

            if not storage_gateway_config.get('high_assurance'):
                attach_data_access_scope(gcs_client, mapped_collection_id)

            transfer_client = TransferClient(app=client_app).add_app_data_access_scope(mapped_collection_id)

            for guest_collection_config in mapped_collection_config['guest_collections']:

                display_name = guest_collection_config['display_name']
                collection_base_path = guest_collection_config['collection_base_path']

                create_directory(transfer_client, mapped_collection_id, collection_base_path)

                matching_guest_collections = [
                    collection for collection in collections
                    if collection['collection_type'] == 'guest'
                    and collection['storage_gateway_id'] == storage_gateway_id
                    and collection['storage_gateway_id'] == storage_gateway_id
                    and collection['display_name'] == display_name
                    ]

                if matching_guest_collections:  # Update existing guest collection
                    print(f'Guest collection "{display_name}" already exists.')
                    if len(matching_guest_collections) == 1:
                        collection = matching_guest_collections[0]
                    else:
                        print(f'Unable to determine unique match for collection "{display_name}"')
                        exit(1)

                    # Unable to update collection_base_path (immutable), so we can't change that
                    collection_request = GuestCollectionDocument(
                        **({key: value for key, value in guest_collection_config.items() if key not in ['collection_base_path', 'permissions']} | 
                            {'mapped_collection_id': mapped_collection_id})
                    )

                    print(f'Updating existing guest collection "{display_name}" with collection ID {collection["id"]}')
                    gcs_client.update_collection(collection['id'], collection_request)

                else:  # Create new guest collection
                    collection_request = GuestCollectionDocument(
                        **({key: value for key, value in guest_collection_config.items() if key not in ['permissions']} | 
                            {'mapped_collection_id': mapped_collection_id})
                    )

                    new_guest_collection = gcs_client.create_collection(collection_request)
                    # print('new_guest_collection:')
                    # pprint(new_guest_collection)
                    print(f'Created new guest collection "{display_name}" with collection ID {new_guest_collection["id"]}')

                for permission_config in guest_collection_config['permissions']:
                    # Create guest collection subdirectory if it doesn't already exist
                    if permission_config['path'] != '/':
                        create_directory(transfer_client, mapped_collection_id, collection_base_path+permission_config['path'])

                    try:
                        result = transfer_client.add_endpoint_acl_rule(collection["id"], permission_config)
                        print(f'Added "{permission_config["permissions"]}" permissions to "{permission_config["path"]}" for {permission_config["principal_type"]} {permission_config["principal"]}')
                    except TransferAPIError as e:
                        if e.code == 'Exists':
                            print(f'Permissions already exist to "{permission_config["path"]}" for {permission_config["principal_type"]} {permission_config["principal"]}')
                        else:
                            raise e

            if purge_guest_collections:
                for existing_guest_collection in [
                    collection
                    for collection in collections
                    if collection['collection_type'] == 'guest'
                    and collection['mapped_collection_id'] == mapped_collection_id
                    ]:
                        if existing_guest_collection['display_name'] not in [
                            guest_collection_config['display_name']
                            for guest_collection_config in mapped_collection_config['guest_collections']
                            ]:
                            try:
                                print(f"Deleting collection {existing_guest_collection['display_name']} (ID: {existing_guest_collection['id']})...")
                                response = gcs_client.delete_collection(existing_guest_collection['id'])
                                print(f"{response['code']}: {response['message']}")
                            except GCSAPIError as e:
                                print(f"Error deleting collection {existing_guest_collection['display_name']}: {e.code} - {e.message}")
                            except Exception as e:
                                print(f"An unexpected error occurred: {e}")


def create_directory(
    transfer_client: TransferClient,
    mapped_collection_id: str,
    directory_path: str
    ) -> None:
    """
    Function to create a directory under a mapped collection using a TransferClient

    Args:
        transfer_client (TransferClient): TransferClient object
        mapped_collection_id (str): UUID of mapped collection
        directory_path (str): relative path of guest collection under mapped collection.
            Must start with "/".

    Raises:
        e: Exception raised if any error other than directory already exists
    """
    try:
        response = transfer_client.operation_mkdir(mapped_collection_id, directory_path)
        print(f'Created directory "{directory_path}" in collection {mapped_collection_id}')
    except TransferAPIError as e:
        if e.code == 'ExternalError.MkdirFailed.Exists':
            print(f'Directory "{directory_path}" already exists in collection {mapped_collection_id}')
        else:
            raise e


def attach_data_access_scope(
    gcs_client: GCSClient,
    collection_id: str
    ) -> None:
    """
    Function to compose and attach a "data_access" scope for the specified mapped collection

    Args:
        gcs_client (GCSClient): GCSClient object
        collection_id (str): UUID of mapped collection
    """

    endpoint_scopes = gcs_client.get_gcs_endpoint_scopes(gcs_client.endpoint_client_id)
    collection_scopes = gcs_client.get_gcs_collection_scopes(collection_id)

    manage_collections = Scope(endpoint_scopes.manage_collections)
    data_access = Scope(collection_scopes.data_access, optional=True)

    manage_collections.add_dependency(data_access)

    gcs_client.add_app_scope(manage_collections)


def ensure_user_credential(
    gcs_client: GCSClient,
    storage_gateway_id: str
    ) -> None:
    """
    Function to ensure that the user has a user credential on the client.
    This is the mapping between Globus Auth (OAuth2) and the local system's permissions.

    Args:
        gcs_client (GCSClient): GCSClient object
        storage_gateway_id (str): UUID of storage gateway
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


def main() -> None:
    """
    Main function when invoked from command line
    Requires Globus credentials for the service user defined in the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET
    """
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Python script to automatically create guest collections defined in managed guest collections configuration file',
        epilog='Requires Globus credentials for the service user in the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET'
        )

    parser.add_argument(
        'managed_guest_collections_config_path',
        help="guest collection configuration JSON or YAML file"
        )

    parser.add_argument(
        '-d',
        '--delete',
        action='store_true',
        help="Flag to delete any existing guest collections not defined in managed guest collections configuration file"
        )

    args = parser.parse_args()

    with open(args.managed_guest_collections_config_path) as managed_guest_collections_config_file:
        if args.managed_guest_collections_config_path.lower().endswith(".json"):
            managed_guest_collections_config = json.load(managed_guest_collections_config_file)
        elif args.managed_guest_collections_config_path.lower().endswith(".yaml") or args.managed_guest_collections_config_path.lower().endswith(".yml"):
            managed_guest_collections_config = yaml.load(managed_guest_collections_config_file)
        else:
            raise(Exception(f"Unrecognised guest collection configuration file type - need JSON or YAML.: {args.managed_guest_collections_config_path}"))

    # This service user ID must be authorised to write to the mapped collection.
    # UUID only - do not include "@clients.auth.globus.org"
    client_id = os.environ.get('GCS_CLI_CLIENT_ID')
    client_secret = os.environ.get('GCS_CLI_CLIENT_SECRET')

    assert client_id and client_secret, "GCS_CLI_CLIENT_ID and/or GCS_CLI_CLIENT_SECRET environment variables undefined"

    manage_guest_collections(
        managed_guest_collections_config=managed_guest_collections_config,
        client_id=client_id,
        client_secret=client_secret,
        purge_guest_collections=args.delete,
        )


if __name__ == '__main__':
    main()
