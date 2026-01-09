# create_and_populate_groups.py
A basic example Python script to use a service user to automatically create and populate groups defined in managed groups configuration file
(path supplied as command line argument).
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in subscription_id in the group config to verify the group within the subscription. The service must have Administrator access to permit this

## Group configuration file format

The path to a valid YAML or JSON group configuration file needs to be supplied as a command line argument.

### YAML

```yaml
---
<group name>:
  description: "<optional group description>"
  members:
  - id: "<globus user uuid>"
    role: "<admin | member>"
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
                "role": "<admin | member>"
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