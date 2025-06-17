# globus_ansible

This Ansible repo is provided for reference purposes. It was modified from the relevant section of the AARNet operational Ansible written by Crystal Chua.

## Prerequisites

### Globus Service User
You will need to create a Globus service user to automate the endpoint setup before you configure the role.

Please follow the instructions at the [Globus Automated Endpoint Deployment Guide](https://docs.globus.org/globus-connect-server/v5.4/automated-deployment/#register_for_service_credentials).

Additional information is available at [Globus How To Use Application Credentials or Service Accounts to Automate Data Transfer](https://docs.globus.org/guides/recipes/automate-with-service-account/).

### SSH keys
You will also need to have a valid SSH public key installed in authorized_hosts on the target machine for the remote Ansible user, and the private key accessible on the Ansible host with this repository.

## Configuration

Please refer to the [globus role README](./roles/globus/README.md) for detailed instructions on how to configure the variables.

## Usage

Navigate to the `code/examples/globus_ansible` directory of this repository. Note that we set the `ANSIBLE_ROLES_PATH` enfironment variable to the path of the subdirectory containing the roles.

After you have configured the variables, use the following command line to create a Globus endpoint:

```ANSIBLE_ROLES_PATH=./roles ansible-playbook -vv -i inventory/all.yml --user <remote_ansible_user> --private-key <path_of_SSH_private_key> playbooks/globus.yml```

To decommission the endpoint, use the following command line:

```ANSIBLE_ROLES_PATH=./roles ansible-playbook -vv -i inventory/all.yml --user <remote_ansible_user> --private-key <path_of_SSH_private_key> playbooks/globus.yml --tags "globus_destroy"```
