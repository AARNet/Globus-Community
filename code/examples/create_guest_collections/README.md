# create_guest_collections.py
This is a Python script to automatically set up guest collections on the host specified as `globus_host` in `GUEST_COLLECTION_CONFIG`.
There is logic to prevent the creation of duplicate guest collections or permissions.

The Globus credentials for the service user must be provided via the environment variables `GCS_CLI_CLIENT_ID` and `GCS_CLI_CLIENT_SECRET`.
Any service user with write permissions to the mapped collection can run this script.

The configuration for this script is used as the basis for a [template](../globus_ansible/roles/globus/templates/guest_collections_config.json.j2)
in the [Globus deployment Ansible](../globus_ansible/), and this is used to feed this Python script which creates guest collections 
under each mapped collection.

## Guest collection configuration file format

The path to a valid YAML or JSON guest collection configuration file needs to be supplied as a command line argument.

### YAML

```yaml
---
globus_host: <globus hostname (e.g. c4e1bc.e229.gaccess.io)>
high_assurance: <true | false>
storage_gateways:
- mapped_collections:
  - guest_collections:
    - base_path: <directory path with leading />
      display_name: <guest collection name>
      permissions:
      - DATA_TYPE: access
        path: <relative path under guest collection>
        permissions: <r | rw>
        principal: <principal UUID>
        principal_type: <identity | group | all_authenticated_users>
      ...
      public: <true | false>
    mapped_collection_id: <mapped collection UUID>"
  ...
  storage_gateway_id: <storage gateway UUID>
...
```

### JSON

```json
{
	"globus_host": "<globus hostname (e.g. c4e1bc.e229.gaccess.io)>",
	"high_assurance": <true | false>,
	"storage_gateways": [
		{
			"storage_gateway_id": "<storage gateway UUID>",
			"mapped_collections": [
				{
					"mapped_collection_id": "<mapped collection UUID>",
					"guest_collections": [
						{
							"base_path": "<directory path with leading />",
							"display_name": "<guest collection name>",
							"public": <true | false>,
							"permissions": [
								{
									"DATA_TYPE": "access",
									"path": "<relative path under guest collection>",
									"permissions": "<r | rw>",
									"principal": "<principal UUID>",
									"principal_type": "<identity | group | all_authenticated_users>"
								},
								...
							]
						},
                        ...
					]
				},
                ...
			]
		},
        ...
	]
}
```