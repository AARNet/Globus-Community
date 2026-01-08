"""
This is a Python script to automatically create groups as defined in MANAGED_GROUPS.
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in SUBSCRIPTION_ID to verify group within the subscription. The service must have Administrator access to permit this

"""
import json
import os
from datetime import datetime
from pprint import pprint, pformat
from typing import Optional, Any
from globus_sdk import GroupsClient, scopes, GroupsManager, GroupPolicies
from globus_sdk.globus_app import ClientApp

# Set this to True to delete and re-create managed groups - use with caution
DELETE_MANAGED_GROUPS = False

# This service user ID must be an authorised subscription Administrator. UUID only - do not include "@clients.auth.globus.org"
CLIENT_ID = os.environ['GCS_CLI_CLIENT_ID']
CLIENT_SECRET = os.environ['GCS_CLI_CLIENT_SECRET']

SUBSCRIPTION_ID = None # Set to subscription UUID for verification

DEFAULT_GROUP_POLICY = {
    "is_high_assurance": False,
    "authentication_assurance_timeout": 1800, # Timeout is in seconds
    "group_visibility": "authenticated", # members | authenticated
    "group_members_visibility": "members",
    "join_requests": False,
    "signup_fields": []
}

# Definition of new groups to be created/updated
MANAGED_GROUPS = {
    "Auto-created test group": {
        #"description": "Group description",
        "members": [
            {
                "id": "73d1b533-653d-4832-b8a1-56d9a5a41478", # alex.ip@aarnet.edu.au
                "role": 'admin'
            },
            {
                "id": "547541ca-d5dd-42e5-aa08-6174a61928b7", # steele.cooke@aarnet.edu.au
                "role": 'member'
            },
        ],
        "policies": dict(DEFAULT_GROUP_POLICY),
    }
}

def main() -> None:

    client_app = ClientApp(
        app_name="group_test_app",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
        )

    group_scope = scopes.data.GroupsScopes.all

    groups_client = GroupsClient(app=client_app, app_scopes=group_scope)

    groups_manager = GroupsManager(groups_client)

    my_groups = get_my_groups(groups_client)
    pprint(my_groups)

    if DELETE_MANAGED_GROUPS:
        print('=' * 25)
        for group in my_groups:
            if group["group_type"] == 'regular' and group["name"] in MANAGED_GROUPS.keys():
                print(f"Deleting group {group['name']}")
                groups_client.delete_group(group["id"])

        my_groups = get_my_groups(groups_client)
        pprint(my_groups)

    new_group_names = sorted(list(set(MANAGED_GROUPS.keys()) - set([group_info['name'] for group_info in my_groups])))
    if new_group_names:
        print('=' * 25)

        for new_group_name in new_group_names:
            new_group_config = MANAGED_GROUPS[new_group_name]
            print(f"Creating group \"{new_group_name}\"")
            new_group_info = create_group(
                groups_client=groups_client,
                group_name=new_group_name,
                group_description=new_group_config.get("description") or f"{new_group_name} created {datetime.now()}",
                #parent_id=SUBSCRIPTION_ID, # This doesn't work
                policies=new_group_config.get("policies"),
                )

            pprint(new_group_info)
            my_groups.append(new_group_info)

    print('=' * 25)

    for group_info in [group_info for group_info in my_groups if group_info["name"] in MANAGED_GROUPS.keys()]:
        print(f"""Updating subscription and policies for group \"{group_info['name']}\"""")
        update_group(
            groups_client=groups_client,
            group_id=group_info["id"],
            subscription_id=SUBSCRIPTION_ID,
            policies=MANAGED_GROUPS[group_info["name"]].get("policies"),
        )

        group_info['subscription_admin_verified_id'] = SUBSCRIPTION_ID

        # No way to list members, so we just go ahead and try to add them
        print(f"Adding members to group \"{group_info['name']}\"")
        add_members(
            groups_manager=groups_manager,
            group_id=group_info["id"],
            users=MANAGED_GROUPS[group_info["name"]]["members"]
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


def add_members(
    groups_manager: GroupsManager,
    group_id: str,
    users: list[dict[str, Any]],
    ) -> None:
    """Function to add members to group

    Args:
        groups_manager (GroupsManager): GroupsManager object
        group_id (str): UUID of group
        users (list[dict[str, Any]]): List of dict {"id": "<user UUID>", "role": "member | admin"}
    """
    for user in users:
        result = groups_manager.add_member(
            group_id,
            user["id"],
            role=user.get("role") or 'member'
            )
        print(f"\t{pformat(result)}")


if __name__ == '__main__':
    main()
