# novaquery

This application enables to retrieve the servers from OpenStack NOVA, using its API. And it enables to filter servers by
their attributes. E.g. to query the servers with the attribute "status" set to "ACTIVE", it is possible to use the following command:
```
novaquery status=ACTIVE
```

This command also enables to group results by one attribute, using the following command will obtain the servers that are not
in the "ACTIVE" status, grouped by the attribute "status":

```    
$ novaquery status!=ACTIVE -g status
...
```
## Installing

The easiest method to install is to use pip:

```console
$ pip install novaquery
```

## Using

There are a lot of useful switches, flags and parameters. To get the most updated help, please use `--help`:

```console
$ novaquery --help
usage: novaquery-cli [-h] [-n] [-A] [-s] [-c] [-f FIELDS] [-F {json,text}] [-p] [-g GROUP_FIELD] [-x APIVERSION] [-a] [-U USERNAME] [-P PASSWORD]
                     [-H KEYSTONE] [-v]
                     searchfield

    This application enables to retrieve the servers from OpenStack NOVA, using its API. And it enables to filter the servers by
    their attributes. 

positional arguments:
  searchfield           Field to search for in the server and the value that we want to match (e.g. flavor.extra_specs.pci_passthrough:alias=V100:1)

optional arguments:
  -h, --help            show this help message and exit
  -n, --no-add-searched
                        Do not add the searched fields to the output
  -A, --all-fields      Add all the fields of the object to the output
  -s, --starts-with     Match value even if only starts with it
  -c, --contains        Match value even if only contains it
  -f FIELDS, --field FIELDS
                        Field that has to be obtained (if not provided any, will include the fields used to search)
  -F {json,text}, --format {json,text}
                        Format of the output
  -p, --progress        Show progress bar
  -g GROUP_FIELD, --group-field GROUP_FIELD
                        Field to group the output by (e.g. OS-EXT-SRV-ATTR:host); will be added to the output
  -x APIVERSION, --nova-api-version APIVERSION
                        The version of the nova api to use (i.e. X-OpenStack-Nova-API-Version header) default: 2.48
  -a, --all-tenants     Retrieve the servers from all tenants
  -U USERNAME, --os-username USERNAME
                        OpenStack username (if not set, will be obtained using OS_USERNAME env var)
  -P PASSWORD, --os-password PASSWORD
                        OpenStack password  (if not set, will be obtained using OS_PASSWORD env var)
  -H KEYSTONE, --os-auth KEYSTONE
                        OpenStack keytsone authentication endpoint (if not set, will be obtained using OS_AUTH_URL env var)
  -v, --version         show program's version number and exit
```

## Examples

Some useful examples are included here:

- retrieve active VMs, grouped by host:
    ```
    $ novaquery status=ACTIVE -A -g OS-EXT-SRV-ATTR:host
    ...
    ```
- retrieve the VMs that are not active (from all tenants), grouped by the state and including the `id`:
    ```
    $ novaquery status!=ACTIVE -f id -g status --all-tenants
    {
        "SHUTOFF": [
            {
                "id": "beecb6af-e01c-4f19-b632-635761416b27",
                "status": "SHUTOFF"
            },
            {
                "id": "e967a7e6-42cd-45fa-94d3-0fd68a6f32a0",
                "status": "SHUTOFF"
            },
            {
                "id": "1a1d4c78-e4a8-47ef-9620-c44bde1b226d",
                "status": "SHUTOFF"
            },
            {
                "id": "72f960e5-c269-46cc-a121-97fc277e435c",
                "status": "SHUTOFF"
            },
            {
                "id": "0cfd6738-8614-4505-862c-231a6639a6dd",
                "status": "SHUTOFF"
            }
        ]
    }
    ```

- retrieve id of active VMs, grouped by host:
    ```
    $ novaquery status=ACTIVE -f id -g OS-EXT-SRV-ATTR:host
    {
        "fh09": [
            {
                "id": "65a247f7-41d4-480a-a343-baa72f25cce3",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh09"
            }
        ],
        "fh07": [
            {
                "id": "d6bc1688-55de-48f1-93cd-4e14a6b01528",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh07"
            },
            {
                "id": "bf4efac5-05b4-43b5-8753-d88de31aaada",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh07"
            }
        ],
        ...
        "fh05": [
            {
                "id": "0be615ae-2a69-4d16-98d5-b446ca89926c",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh05"
            },
            {
                "id": "87ffa5bc-02f8-446e-a3d5-f48f3cb88afb",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh05"
            },
            {
                "id": "b344e0c6-6a96-4360-8514-bf3cb6840190",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh05"
            }
        ],
        "fh02": [
            {
                "id": "35324838-cf3b-4560-a86c-c2112f1cf961",
                "status": "ACTIVE",
                "OS-EXT-SRV-ATTR:host": "fh02"
            }
        ]
    }
    ```

- retrieve the names and id of VMs that have pci_passthrough devices, grouped by host name:
    ```
    $ novaquery flavor.extra_specs.pci_passthrough:alias -f name -f id -g OS-EXT-SRV-ATTR:host
    {
        "fh06": [
            {
                "name": "spotG01",
                "id": "3602d1c6-0fe1-4c89-9a68-2a63cbc6c04a",
                "flavor": {
                    "extra_specs": {
                        "pci_passthrough:alias": "V100:1"
                    }
                },
                "OS-EXT-SRV-ATTR:host": "fh06"
            }
        ]
    }
    ```
- retrieve all the servers that have 4 VCPUs using an alternate format:
    ```
    $ novaquery flavor.vcpus=4 -f id -f name -f flavor --format text
    0.id=65a247f7-41d4-480a-a343-baa72f25cce3
    0.name=dockerbuilds
    0.flavor.ephemeral=40
    0.flavor.ram=16000
    0.flavor.original_name=Large
    0.flavor.vcpus=4
    0.flavor.swap=8000
    0.flavor.disk=14
    1.id=d6bc1688-55de-48f1-93cd-4e14a6b01528
    1.name=warrior
    1.flavor.ephemeral=40
    1.flavor.ram=16000
    1.flavor.original_name=Large
    1.flavor.vcpus=4
    1.flavor.swap=8000
    1.flavor.disk=14
    2.id=cbd889d5-5e78-4b85-80d0-1732599315dc
    2.name=myproxy
    2.flavor.ephemeral=0
    2.flavor.ram=8000
    2.flavor.original_name=Medium
    2.flavor.vcpus=4
    2.flavor.swap=4000
    2.flavor.disk=14
    3.id=b980c152-c4f4-44fb-a29e-c72c5f01c36e
    3.name=spot
    3.flavor.ephemeral=2000
    3.flavor.ram=7500
    3.flavor.original_name=Large.scratch
    3.flavor.vcpus=4
    3.flavor.swap=7500
    3.flavor.disk=14    
    ```
