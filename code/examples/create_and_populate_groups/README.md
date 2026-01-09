# create_and_populate_groups.py
A basic example Python script to use a service user to automatically create and populate groups defined in managed groups configuration file
(path supplied as command line argument).
There is logic to prevent the creation of duplicate groups.

The Globus credentials for the service user must be provided via the environment variables GCS_CLI_CLIENT_ID and GCS_CLI_CLIENT_SECRET.

Provide a subscription UUID in subscription_id in the group config to verify the group within the subscription. The service must have Administrator access to permit this
