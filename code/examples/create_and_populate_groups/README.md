# create_and_populate_groups.py
This is a basic example Python script to use a service user to automatically create groups as defined in MANAGED_GROUPS.
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in SUBSCRIPTION_ID to verify group within the subscription. The service user must have Administrator access to permit this
