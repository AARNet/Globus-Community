# create_and_populate_groups.py
This is a Python script to use a service user to automatically create and populate groups defined in a managed groups configuration file
(path supplied as command line argument). You would invoke it from the command line as follows:

```
python3 create_and_populate_groups.py <name of configuration file>
```

You can also import the manage_groups function into your own Python script.
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in subscription_id in the group config to verify the group within the subscription. The service must have Administrator access to permit this

## Using the manage_groups Python function

You can import the manage_groups function into your own Python script as follows:

```python
from create_and_populate_groups import manage_groups
```

The manage_groups function declaration is as follows:

```python
def manage_groups(
    managed_groups_config: dict[str, dict[str, Any]],
    client_id: str,
    client_secret: str,
    delete_groups: bool=False
    ) -> None:
    """
    Function to manage groups from a configuration dict.
    This function could be imported into another Python script and run with a different managed_groups_config.

    Args:
        managed_groups_config (dict[dict[str, Any]]): Group configuration dict
        client_id (str): UUID of service user.
        client_secret (str) Secret for service user.
        delete_groups (bool): Boolean flag indicating whether to pre-delete any existing guest collections
            in managed_groups_config. Default = False
    """
```

## Group configuration file format

The path to a valid YAML or JSON group configuration file needs to be supplied as a command line argument.

### YAML

```yaml
---
<group name>:
  description: "<optional group description>"
  members:
  - id: "<globus user uuid>"
    role: "<admin | manager | member>"
    user: "<informational field only - user email?>"
  ...
  policies:
    authentication_assurance_timeout: 1800
    group_members_visibility: members
    group_visibility: authenticated
    is_high_assurance: false
    join_requests: false
    signup_fields: []
  subscription_id: "<optional subscription UUID>"
...
```

### JSON

```json
{
    "<group name>": {
        "description": "<optional group description>",
        "members": [
            {
                "user": "<informational field only - user email?>",
                "id": "<globus user uuid>",
                "role": "<admin | manager | member>"
            },
            ...
        ],
        "policies": {
            "is_high_assurance": false,
            "authentication_assurance_timeout": 1800,
            "group_visibility": "authenticated",
            "group_members_visibility": "members",
            "join_requests": false,
            "signup_fields": []
        },
        "subscription_id": "<optional subscription UUID>"
    },
    ...
}
```