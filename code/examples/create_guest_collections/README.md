# create_guest_collections.py
This is a Python script to automatically set up guest collections on the host specified as `globus_host` in `GUEST_COLLECTION_CONFIG`.
There is logic to prevent the creation of duplicate guest collections or permissions.

The Globus credentials for the service user must be provided via the environment variables `GCS_CLI_CLIENT_ID` and `GCS_CLI_CLIENT_SECRET`.
Any service user with write permissions to the mapped collection can run this script.

This script is used as the basis for a [template](../globus_ansible/roles/globus/templates/create_guest_collections.py.j2)
in the [Globus deployment Ansible](../globus_ansible/), and this is used to create Python scripts which create guest collections 
under each mapped collection.