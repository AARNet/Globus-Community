---
title: AARNet eResearch Australasia "Advanced Globus" Workshop
permalink: /globus-community-australasia/workshops/advanced_globus_workshop/
---

## AARNet eResearch Australasia 2025 Workshop - Advanced Globus

## Overview

In this half-day workshop, we will be exploring some advanced Globus configurations. At the conclusion of the workshop, you should be able to:

- Use connectors to interface Globus with storage systems other than Posix (e.g. S3)
- Implement automated workflows using Globus Flows to streamline your data processing and management tasks
- Use tools like Jupyter Notebooks with Globus
- Use Globus Compute to schedule jobs in HPC environments
- Set up custom user mappings for Globus authentication on local resources and optimise security settings

If time permits, we hope to have an round-table discussion of real-life Globus use-cases.

Note that there is a shared document for the workshop [here](http://tiny.cc/eRA25AdvGlobus). You will be able to add questions on notice if we don't have time to answer them interactively during the workshop.

## Workshop Prerequisites

You will need to bring the following to the workshop:

- A laptop with the ability to connect to an AWS EC2 instance via SSH in order to complete the hands-on sections of the workshop. Please ensure that your firewall permits outbound SSH access to arbitrary IP addresses. Power and WiFi will be provided.
- A valid educational or research institution account to gain access to Globus (must be available in [EduGain](https://edugain.org/) via the [Australian Access Federation (AAF)](https://aaf.edu.au/)) or [Tuakiri](https://www.reannz.co.nz/products-and-services/tuakiri/). A list of AAF institutions is available [here](https://aaf.edu.au/subscribers/), and Tuakiri [here](https://www.reannz.co.nz/membership/members/). Alternatively, you can also use ORCID, GitHub or Google to access Globus for the workshop.
- Sufficient familiarity with the Linux command line so that you are able to perform basic command line operations, edit text files, and install packages. If you are completely unfamiliar with Linux, you will still benefit from attending the workshop, but you may need assistance with the hands-on sections. Please let us know beforehand if you are likely to require this assistance.

Optionally, the following would be useful:

- The ability to install Globus Connect Personal (GCP) software on your laptop. You may wish to download this software from https://www.globus.org/globus-connect-personal and pre-install it before the workshop, or it can be downloaded and installed in the workshop. Note that if you are unable to install GCP due to restrictions on your laptop, you will only be able to observe demonstrations of its use.

To get the most out of this workshop, you should already be able to:

- Know what Globus is and the benefits it provides for researchers
- Use the Globus web interface to transfer files between collections
- Understand the high-level architecture of Globus
- Install Globus Connect Personal software and set up a local endpoint with collections
- Install Globus Connect software on a Linux host and set up an endpoint with collections
- Configure Globus Storage Gateways and Collections for fine-grained access control
- Know how to monitor user activity on your collections

These skills were covered in the half-day ["Introduction to Globus" workshop](../introduction_to_globus_workshop/) run by AARNet at eResearch Australasia in 2024, and also in the morning session before this afternoon workshop.

Please contact alex.ip@aarnet.edu.au, steele.cooke@aarnet.edu.au or chris.myers@aarnet.edu.au if you are unsure about any of the above requirements.

## Agenda
### PART I
#### PRELUDE (15-20 minutes) - Sara
##### Housekeeping - fire exits, break times + laptop checks
##### Acknowledgement of Country
##### Introductions - instructors, helpers + how to participate
##### Plan for the day - aims, learning objectives, timing (2 x 90min sessions + 30 min break)

### ADVANCED GLOBUS (90mins) - Alex, Chris and Steele
##### Quick Review of Globus System Architecture

##### Setting up a Globus Service User (Client App)

##### Setting up a Globus Endpoint automatically using Ansible

##### Using the Globus API tools with including Jupyter Notebooks

##### Implementing automated workflows using Globus Flows to streamline your data processing and management tasks

##### Using Globus Compute to schedule jobs in HPC environments

##### Using connectors to interface Globus with storage systems other than Posix (e.g. S3)

##### Setting up custom user mappings for Globus authentication on local resources and optimise security settings

##### Open Discussion (15-20 minutes)
- Introduce Globus Community Australasia
- Specific use Cases

## Quick Review of Globus System Architecture
Below is a high-level diagram of the major components of the Globus system.

<img src="../resources/globus_connect_server_architecture.png" alt="Globus Architecture and Concepts" width="1000"/>

### Definitions
#### Endpoint
A logical construct that identifies an instance of Globus Connect to the Globus service. Each endpoint is registered with Globus and receives a new DNS record. An endpoint aggregates one or more Data Transfer Nodes.

#### Data Transfer Node (DTN)
A physical manifestation of the endpoint. More DTNs for an endpoint mean a larger physical footprint and better resilience and performance. Each DTN has a unique IP address which is registered with the Globus and the DNS record for the endpoint.

#### Connector
A software package that implements an interface allowing the Globus service to access a specific storage system (e.g. POSIX, S3, etc). Note that users will never interact directly with a connector. Note also that POSIX is supported by default, and additional connectors may entail an extra cost.

#### Storage Gateway
An instance of a Globus Connector configured to access a storage system using specified policies (valid IDPs, path restrictions, etc.).

#### Collection
A logical construct that allows a user to access data via the Globus service (constrained by the underlying Storage Gateway). One could think of this as a "projection" of part or all of a storage system via the Globus service.

#### UUID
A Universally Unique Identifier (UUID) is a 128-bit label used for information in computer systems. The term Globally Unique Identifier (GUID) is also used, mostly in Microsoft systems. Every Globus entity is assigned a UUID, which looks like the following:
```
a3f0c02a-866a-472e-8f13-248360e296f7
```
These UUIDs are used by Globus to uniquely identify resources, so they are particularly important in the context of automation. They can also be used to search for endpoints or collections in the Web UI.


## Setting up a Globus Service User (Client App)
A client app is a script or application that you would create for a pre-defined service user to run. The service user would be authenticated using a client secret,
and its permissions would be determined by the policies applicable to that account. The service user ID is not sensitive, but the user secret should be closely 
guarded in the same way that you would protect a normal account password.

We will set up a service user that we can use to authenticate several automation tasks in this workshop

### Registering a Client App
To have persistent authentication for automation tasks, we will first need to register a client app (service user). The procedure for doing this is as follows:

1. Navigate to the Globus [Developer Site](https://app.globus.org/settings/developers) - also accessible under "Settings" in the web app.

<img src="../resources/globus_developers_page.png" alt="Globus Developer site" width="1000"/>

2. Select “Register a service account or application credential for automation.”
3. Create or Select a Project
    - A project is a collection of apps with a shared list of administrators.
    - If you don’t own any projects, you will automatically be prompted to create one.
    - If you do, you will be prompted to either select an existing or create a new one.

<img src="../resources/create_new_project.png" alt="Create New Project" width="1000"/>

4. Creating or selecting a project will prompt you for another login, sign in with an account that administers your project.
5. Give your App a name; this is what users will see when they are asked to authorize your app.

<img src="../resources/service_account_registration.png" alt="Service Account Registration" width="1000"/>

6. Click “Register App”. This will create your client app and take you to a page describing it.
7. Copy the “Client UUID” from the page.
    - This ID can be thought of as your Client App’s “username”. It is non-secure information and as such, feel free to hardcode it into scripts.

<img src="../resources/client_app_details.png" alt="Client App Details" width="1000"/>

8. Click on "Add Client Secret" and enter the name of your Client App

<img src="../resources/generate_new_client_secret.png" alt="Generate New Client Secret" width="1000"/>

9. Click on "Generate Secret"

<img src="../resources/generate_new_client_secret.png" alt="Generate New Client Secret" width="1000"/>

10. Copy the client secret and store it somewhere secure - you will only have this one opportunity to do so!

<img src="../resources/client_secret.png" alt="Client Secret" width="1000"/>

11. Add your service user to the list of users with write permissions on your writable guest collection

<!-- TODO: add pictures and instructions here -->

##### Setting up a Globus Endpoint automatically using Ansible
We have set up an Ansible script to automate the setup of a Globus endpoint, storage gateway and mapped collection on your workshop VM. The Ansible code can
be found [here](https://github.com/AARNet/Globus-Community/tree/main/code/examples/globus_ansible).

For this workshop, you will find the ansible code in your home directory ~/globus_ansible. We have already set up the files `~/globus_ansible/inventory/all.yml` and `~/globus_ansible/inventory/host_vars/globus-test-host.yml` with your public IP address for you, but you will need to edit the file `~/globus_ansible/roles/globus/defaults/main.yml` with your user details.

Specifically, you will need to provide values for these:
- `globus_svc_client_id: "{{ lookup('community.hashi_vault.vault_kv2_get', '{{ globus_secret_path.deploy_svc }}').secret.client_id if use_vault else '<Globus service user ID - use UUID before before @>' }}"`
- `globus_svc_secret_id: "{{ lookup('community.hashi_vault.vault_kv2_get', '{{ globus_secret_path.deploy_svc }}').secret.secret_id if use_vault else '<Globus service user secret>' }}"`




## Using tools like Jupyter Notebooks with the Globus API
Globus maintains a full SDK (System Developers Kit) including a Python API, with documentation at https://globus-sdk-python.readthedocs.io/en/stable/.

This has already been installed for you on your workshop VM, along with a number of Jupyter notebooks we will use.

### Authentication

#### Definitions
To use the API, we will need to authenticate with Globus. Details about this process can be found in the Globus documentation on [Clients, Scopes, and Consents](https://docs.globus.org/guides/overviews/clients-scopes-and-consents/).

The important points to note are 
- A __Client__ is an application like the CLI or Web Application.
    - Users can register their own Clients.
- __Scopes__ define actions which are permitted within Globus.
- __Tokens__ are credentials used by Clients to represent a user. They are always issued with some associated Scopes.
- __Consents__ are records of a user granting a Client permissions in the form of a set of Scopes.
    - Tokens will be issued to the Client, associated with the requested Scopes.

#### Application Types
There are two types of applications which can be authorised in Globus: UserApps and ClientApps.

- UserApp, for interactions in which a "real" end user communicates with Globus services
- ClientApp, for interactions in which an OAuth2 client, operating as a “service account”, communicates with Globus services.

Details about these application types can be found at https://globus-sdk-python.readthedocs.io/en/stable/authorization/globus_app/apps.html

The following table provides a comparison of these two options:

| UserApp | ClientApp |
| :--- | :--- |
| Appropriate for performing actions as a specific end user (e.g., the Globus CLI) | Appropriate for automating actions as a service account |
| Created resources (e.g., collections or flows) by default are owned by an end user | Created resources (e.g., collections or flows) by default are owned by the OAuth2 client |
| Existing resource access is evaluated based on an end user’s permissions | Existing resource access is evaluated based on the OAuth2 client’s permissions |
| OAuth2 tokens are obtained by putting an end user through a login flow (this occurs in a web browser) | OAuth2 tokens are obtained by programmatically exchanging an OAuth2 client’s secret |
| Should typically use a “native” OAuth2 client (Register a thick client) | May use a “confidential” OAuth2 client (Register a portal or science gateway) |
| Must use a “confidential” OAuth2 client | (Register a service account) |

### Registering and Running a User App in Globus Auth (taken from https://globus-sdk-python.readthedocs.io/en/stable/user_guide/getting_started/register_app.html)
A user app is a script that you would create for other users to run. The user would authenticate using their own credentials, and their permissions would be 
determined by the policies applicable to their own account. For example, if a user tried to run the script but did not have the permissions to read and/or write 
from a given collection, then they would be unable to run the script successfully.

#### Registering a User App
In order for a "real" user to run your script, we will need to register a user app with appropriate scopes. The procedure for doing this is as follows:

1. Navigate to the Globus [Developer Site](https://app.globus.org/settings/developers) - also accessible under "Settings" in the web app.

<img src="../resources/globus_developers_page.png" alt="Globus Developer site" width="1000"/>

2. Select “Register a thick client or script that will be installed and run by users on their devices.”
3. Create or Select a Project
    - A project is a collection of apps with a shared list of administrators.
    - If you don’t own any projects, you will automatically be prompted to create one.
    - If you do, you will be prompted to either select an existing or create a new one.

<img src="../resources/create_new_project.png" alt="Create New Project" width="1000"/>

4. Creating or selecting a project will prompt you for another login, sign in with an account that administers your project.

<img src="../resources/user_app_registration.png" alt="User App Registration" width="1000"/>

5. Give your App a name; this is what users will see when they are asked to authorize your app.
6. Click “Register App”. This will create your app and take you to a page describing it.

<img src="../resources/user_app_details.png" alt="User App Details" width="1000"/>

7. Copy the “Client UUID” from the page.
    - This ID can be thought of as your App’s “username”. It is non-secure information and as such, feel free to hardcode it into scripts.

#### Running a User App in a Jupyter Notebook
The Jupyter notebooks for the workshop should be pre-loaded on your VM. If you are going through these exercises in a different environment, then you may want to 
download the notebooks from [here](https://github.com/AARNet/Globus-Community/tree/main/globus-community-australasia/workshops/jupyter_notebooks).

We will run the Jupyter notebook examples on the VM using port-forwarding from a browser on your laptop.

Firstly, you would start the Jupyter Notebook server (JupyterLab) on the VM as follows:

```bash
cd jupyter_notebooks
jupyter lab
```
This will launch JupyterLab and you should see something like the following (with a different token) at the end of the output:
```
    To access the server, open this file in a browser:
        file:///home/workshop-user/.local/share/jupyter/runtime/jpserver-108989-open.html
    Or copy and paste one of these URLs:
        http://localhost:8888/lab?token=be631b49d54575dc6741c91b8043cc83592cd71d261dabbe
        http://127.0.0.1:8888/lab?token=be631b49d54575dc6741c91b8043cc83592cd71d261dabbe
```

We will need to forward port 8888 from your laptop browser to the remote JupyterLab server on the VM. More details on SSH port forwarding can be found [here](https://www.ssh.com/academy/ssh/tunneling-example).

We will need to establish an ssh connection with local port 8888 forwarded through to port 8888 on the remote host. The SSH command would look something like this:
```bash
ssh -L 8888:localhost:8888 <your VM IP address>
```

<!-- TODO: write better port forwarding instructions - maybe in appendix -->

Once you have established the port forwarding, you should be able to copy and paste one of the last two URLs into your local browser, and you should see something like this:

<img src="../resources/jupyterlab.png" alt="Jupyterlab" width="1000"/>

You should be able to open the Jupyter notebook `Initiating a Transfer with a UserApp.ipynb`

Edit the client ID and replace it with your user client ID that you copied from the registration. Edit the DST_COLLECTION value to be the UUID of the destination collection, noting that your personal Globus account must have write access to that collection.

Click on the double-arrow at the top of the notebook to restart the kernel and run all cells. You may be prompted to authenticate using a URL, and then pasting the 
resultant token into an edit box.

<img src="../resources/Initiating_a_Transfer_with_a_UserApp.png" alt="Initiating a Transfer with a UserApp" width="1000"/>

Check your destination collection, and, if all has gone well, the file should have been transferred there by the script.

**Congratulations! You should have initiated a transfer from one collection to another using your own user credentials!**

Of course, we may not want to have to go through the browser-based authenticate every time we run a script, so we will now look at creating a service user and running
a client app.

### Registering and Running a Client App in Globus Auth (service user)
A client app is a script that you would create for a pre-defined service user to run. The service user would be authenticated using a client secret, and its
permissions would be determined by the policies applicable to that account. The service user ID is not sensitive, but the user secret should be closely guarded in the
same way that you would protect a normal account password.

### Registering a Client App
In order for a service user to run your script, we will first need to register a client app (service user). The procedure for doing this is as follows:

1. Navigate to the Globus [Developer Site](https://app.globus.org/settings/developers) - also accessible under "Settings" in the web app.

<img src="../resources/globus_developers_page.png" alt="Globus Developer site" width="1000"/>

2. Select “Register a service account or application credential for automation.”
3. Create or Select a Project
    - A project is a collection of apps with a shared list of administrators.
    - If you don’t own any projects, you will automatically be prompted to create one.
    - If you do, you will be prompted to either select an existing or create a new one.

<img src="../resources/create_new_project.png" alt="Create New Project" width="1000"/>

4. Creating or selecting a project will prompt you for another login, sign in with an account that administers your project.
5. Give your App a name; this is what users will see when they are asked to authorize your app.

<img src="../resources/service_account_registration.png" alt="Service Account Registration" width="1000"/>

6. Click “Register App”. This will create your client app and take you to a page describing it.
7. Copy the “Client UUID” from the page.
    - This ID can be thought of as your Client App’s “username”. It is non-secure information and as such, feel free to hardcode it into scripts.

<img src="../resources/client_app_details.png" alt="Client App Details" width="1000"/>

8. Click on "Add Client Secret" and enter the name of your Client App

<img src="../resources/generate_new_client_secret.png" alt="Generate New Client Secret" width="1000"/>

9. Click on "Generate Secret"

<img src="../resources/generate_new_client_secret.png" alt="Generate New Client Secret" width="1000"/>

10. Copy the client secret and store it somewhere secure - you will only have this one opportunity to do so!

<img src="../resources/client_secret.png" alt="Client Secret" width="1000"/>

11. Add your service user to the list of users with write permissions on your writable guest collection

<!-- TODO: add pictures and instructions here -->

#### Running a Client App in a Jupyter Notebook
The Jupyter notebooks for the workshop should be pre-loaded on your VM. If you are going through these exercises in a different environment, then you may want to 
download the notebooks from [here](https://github.com/AARNet/Globus-Community/tree/main/globus-community-australasia/workshops/jupyter_notebooks).

As in the previous example, we will run the Jupyter notebook examples on the VM using port-forwarding from a browser on your laptop. Please follow the instructions above
to launch JupyterLab in your laptop browser.

Open the file `client_app_creds.py` and edit the `CLIENT_ID` and `CLIENT_SECRET` to match the values from your ClientApp registration. We will use these credentials for
some of the later coding examples.

You should now be able to open the Jupyter notebook `Initiating a Transfer with a ClientApp.ipynb`

Click on the double-arrow at the top of the notebook to restart the kernel and run all cells.

<img src="../resources/Initiating_a_Transfer_with_a_ClientApp.png" alt="Initiating a Transfer with a ClientApp" width="1000"/>

Congratulations! You should have initiated a transfer from one collection to another using a service user!
