"""
A Python script to automatically create and populate groups defined in managed groups configuration file (path supplied as command line argument).
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in subscription_id in the group config to verify the group within the subscription. The service must have Administrator access to permit this

"""
import argparse
import json
import os
import sys
import yaml
from datetime import datetime
from pprint import pprint, pformat
from typing import Optional, Any
from globus_sdk import GroupsClient, scopes, GroupsManager, GroupPolicies
from globus_sdk.globus_app import ClientApp

# CLIENT_ID is the service user UUID only - do not include "@clients.auth.globus.org"
CLIENT_ID = os.environ.get('GCS_CLI_CLIENT_ID')
CLIENT_SECRET = os.environ.get('GCS_CLI_CLIENT_SECRET')

DEFAULT_GROUP_POLICY = {
    "is_high_assurance": False,
    "authentication_assurance_timeout": 1800, # Timeout is in seconds
    "group_visibility": "authenticated", # members | authenticated
    "group_members_visibility": "members", # members | authenticated
    "join_requests": False,
    "signup_fields": []
}

def main() -> None:
    parser = argparse.ArgumentParser(
        prog=sys.argv[0],
        description='Python script to automatically create groups defined in managed groups configuration file',
        epilog='Requires Globus credentials for the service user in the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET'
        )

    parser.add_argument('managed_groups_config_path', help="group configuration JSON or YAML file")
    parser.add_argument('-d', '--delete', action='store_true', help="Flag to pre-delete any existing managed groups")

    args = parser.parse_args()

    with open(args.managed_groups_config_path) as managed_groups_config_file:
        if args.managed_groups_config_path.lower().endswith(".json"):
            managed_groups_config = json.load(managed_groups_config_file)
        elif args.managed_groups_config_path.lower().endswith(".yaml") or args.managed_groups_config_path.lower().endswith(".yml"):
            managed_groups_config = yaml.load(managed_groups_config_file)
        else:
            raise(Exception(f"Unrecognised group configuration file type: {args.managed_groups_config_path}"))

    assert CLIENT_ID and CLIENT_SECRET, "GCS_CLI_CLIENT_ID and/or GCS_CLI_CLIENT_SECRET undefined"

    manage_groups(managed_groups_config, delete_groups=args.delete)


def manage_groups(managed_groups_config: dict[dict[str, Any]], delete_groups: bool=False) -> None:
    """
    Function to manage groups from a configuration dict.
    This function could be imported into another Python script and run with a different managed_groups_config.

    :param managed_groups_config: Group configuration dict
    :type managed_groups_config: dict[dict[str, Any]]
    """
    client_app = ClientApp(
        app_name="group_test_app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
        )

    group_scope = scopes.data.GroupsScopes.all

    groups_client = GroupsClient(app=client_app, app_scopes=group_scope)

    my_groups = get_my_groups(groups_client)
    # pprint(my_groups)

    if delete_groups:
        print('=' * 25)
        for group in my_groups:
            if group["group_type"] == 'regular' and group["name"] in managed_groups_config.keys():
                print(f"Deleting group {group['name']}")
                groups_client.delete_group(group["id"])

        my_groups = get_my_groups(groups_client)
        # pprint(my_groups)

    new_group_names = sorted(list(set(managed_groups_config.keys()) - set([group_info['name'] for group_info in my_groups])))
    if new_group_names:
        print('=' * 25)

        for new_group_name in new_group_names:
            new_group_config = managed_groups_config[new_group_name]
            print(f"Creating group \"{new_group_name}\"")
            new_group_info = create_group(
                groups_client=groups_client,
                group_name=new_group_name,
                group_description=new_group_config.get("description") or f"{new_group_name} created {datetime.now()}",
                parent_id=new_group_config.get("parent_id"),
                policies=new_group_config.get("policies"),
                )

            # pprint(new_group_info)
            my_groups.append(new_group_info)

    print('=' * 25)

    for group_info in [group_info for group_info in my_groups if group_info["name"] in managed_groups_config.keys()]:
        print(f"""Updating subscription and policies for group \"{group_info['name']}\"""")
        subscription_id = managed_groups_config[group_info["name"]].get("subscription_id")
        update_group(
            groups_client=groups_client,
            group_id=group_info["id"],
            subscription_id=subscription_id,
            policies=managed_groups_config[group_info["name"]].get("policies"),
        )

        group_info['subscription_admin_verified_id'] = subscription_id

        print(f"Managing group membership for group \"{group_info['name']}\"")
        manage_membership(
            groups_client=groups_client,
            group_id=group_info["id"],
            users=managed_groups_config[group_info["name"]]["members"]
        )


def get_my_groups(groups_client: GroupsClient) -> list[dict[str, Any]]:
    """Function to return a list of group information dicts for the current user

    Args:
        groups_client (GroupsClient): GroupsClient object

    Returns:
        list[dict[str, Any]]: list of group information dicts for the current user
    """
    groups = groups_client.get_my_groups()
    for group in groups:
        if group.get("enforce_session"):
            strict_session_enforcement = True
        else:
            strict_session_enforcement = False
        roles = ",".join({membership["role"] for membership in group["my_memberships"]})

    return list(groups)


def create_group(
    groups_client: GroupsClient,
    group_name: str,
    group_description: Optional[str]=None,
    terms_and_conditions: Optional[str]=None,
    parent_id: Optional[str]=None,
    policies: dict[str, Any]=DEFAULT_GROUP_POLICY,
    ) -> dict[str, Any]:
    """Function to create a new group

    Args:
        groups_client (GroupsClient): GroupsClient object
        group_name (str): Name of group
        group_description (Optional[str], optional): Description of group. Defaults to None.
        terms_and_conditions (Optional[str], optional): Termas and conditions for group. Defaults to None.
        parent_id (Optional[str], optional): Parent group ID for group. Defaults to None.

    Returns:
        dict[str, Any]: Group information from groups_client.create_group call
    """

    group_def = {
        "name": group_name,
        "description": group_description,
        "terms_and_conditions": terms_and_conditions,
        "parent_id": parent_id,
        "policies": policies
        }

    result = groups_client.create_group(group_def)

    return result.data


def update_group(
    groups_client: GroupsClient,
    group_id: str,
    subscription_id: Optional[str]=None,
    policies: Optional[dict[str, Any]]=DEFAULT_GROUP_POLICY,
    ) -> None:
    """Function to update a group

    Args:
        groups_client (GroupsClient): GroupsClient object
        group_id (str): UUID of group
        subscription_id (Optional[str], optional): UUID of subscription for verification or None
        policies (Optional[dict[str, Any]], optional): Dict defining policies. Defaults to DEFAULT_GROUP_POLICY.
    """

    result = groups_client.set_subscription_admin_verified_id(
        group_id=group_id,
        subscription_id=subscription_id,
    )
    print(f"\t{pformat(result)}")

    result = groups_client.set_group_policies(
        group_id=group_id,
        data=policies,
    )
    print(f"\t{pformat(result)}")


def manage_membership(
    groups_client: GroupsClient,
    group_id: str,
    users: list[dict[str, Any]],
    ) -> None:
    """Function to manage members in a group

    Args:
        groups_client (GroupsClient): GroupsClient object
        group_id (str): UUID of group
        users (list[dict[str, Any]]): List of dict {"id": "<user UUID>", "role": "member | manager | admin"}
    """
    groups_manager = GroupsManager(groups_client)

    existing_members = groups_client.get_group(group_id, include="memberships").data["memberships"]
    # pprint(existing_members)

    for user in users:
        try:
            existing_member = [member for member in existing_members if member["identity_id"] == user["id"] and member["status"] != "removed"][0]
        except IndexError:
            existing_member = None

        if existing_member and existing_member["role"] == user["role"]:
            # Nothing to do
            print(f"\tUser {existing_member['identity_id']} already exists with role {existing_member['role']}")
            continue

        role=user.get("role") or 'member'

        if existing_member:  # Need to modify role
            print(f"\tChanging existing group member {user['id']} from role \"{existing_member['role']}\" to role \"{role}\"")
            result = groups_manager.change_role(group_id, user["id"], role)
        else:  # Need to add new user
            print(f"\tAdding new group member {user['id']} with role \"{role}\"")
            result = groups_manager.add_member(
                group_id,
                user["id"],
                role=role
                )
        print(f"\t{pformat(result)}")

    member_ids = [user["id"] for user in users] + [CLIENT_ID]

    for existing_member in existing_members:
        existing_member_id = existing_member["identity_id"]
        if existing_member_id not in member_ids and existing_member['status'] != 'removed':
            print(f"\tDeleting existing user {existing_member_id} from group {group_id}")
            result = groups_manager.remove_member(
                group_id,
                existing_member_id,
                )
            print(f"\t{pformat(result)}")


if __name__ == '__main__':
    main()
