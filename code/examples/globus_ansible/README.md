# globus_ansible

This Ansible repo is provided for reference purposes. It was modified from the relevant section of the AARNet operational Ansible written by Crystal Chua.

## Prerequisites

### Globus Service User
You will need to create a Globus service user to automate the endpoint setup before you configure the role.

Please follow the instructions at the [Globus Automated Endpoint Deployment Guide](https://docs.globus.org/globus-connect-server/v5.4/automated-deployment/#register_for_service_credentials).

Additional information is available at [Globus How To Use Application Credentials or Service Accounts to Automate Data Transfer](https://docs.globus.org/guides/recipes/automate-with-service-account/).

NB: You will need to make sure that your service user is a valid subscription manager if you have a non-empty `globus_subscription_id` value.

### SSH keys
You will also need to have a valid SSH public key installed in authorized_hosts on the target machine for the remote Ansible user, and the private key accessible on the Ansible host with this repository.

## Configuration

Please refer to the [globus role README](./roles/globus/README.md) for detailed instructions on how to configure the variables.

## Usage

Navigate to the `code/examples/globus_ansible` directory of this repository. Note that we set the `ANSIBLE_ROLES_PATH` enfironment variable to the path of the subdirectory containing the roles.

After you have configured the variables, use the following command line to create a Globus endpoint:

```ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory/all.yml --user <remote_ansible_user> --private-key <path_of_SSH_private_key> playbooks/globus.yml```

To decommission the endpoint, use the following command line:

```ANSIBLE_ROLES_PATH=./roles ansible-playbook -i inventory/all.yml --user <remote_ansible_user> --private-key <path_of_SSH_private_key> playbooks/globus.yml --tags "globus_destroy"```

## Notes

### Private mapped collections on a non-subscription endpoint
This Ansible uses your Globus service user credentials as the owner of the endpoint, so this means that any ___private___ mapped collections created by the Ansible on an endpoint ___not___ associated with a subscription will only be visible to that service user, so, effectively, ___NOBODY___ will be able to see them. __You will need to make your collections public (using the respective `public_private` value in the `globus_default_storage_gateway.collections` configuration variable) for them to be visible to anyone in the Globus web UI if you are not a Globus subscriber.__

If you have a valid subscription ID in your configuration, then The role functionality used to assign administrative rights (set in the `globus_endpoint_roles` variable) will make any private collections on the endpoint visible to any administrators you add.

### Hashicorp Vault for storing secrets
If you have access to the Hashicorp Vault, you can use that for storing your secrets, including the ones created during the endpoint registration process.

To enable the use of Hashicorp Vault, you will need to set the following configuration variables:
- `use_vault` - set this to true
- `globus_secret_path.deploy_svc` - set this to the vault path where Globus auto-deploy service user credentials are located
- `globus_secret_path.deploy_key` - set this to the vault path where the Globus endpoint's `deployment-key.json` secret is stored