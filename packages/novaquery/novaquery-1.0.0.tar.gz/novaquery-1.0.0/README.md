# novaquery

This application enables to retrieve the servers from OpenStack NOVA, using its API. And it enables to filter servers by
their attributes. E.g. to query the servers with the attribute "status" set to "ACTIVE", it is possible to use the following command:
```
novaquery status=ACTIVE
```

This command also enables to group results by one attribute, using the following command will obtain the servers that are not
in the "ACTIVE" status, grouped by the attribute "status":

```    
novaquery status!=ACTIVE -g status
```

Examples:
- command line to retrieve active VMs, grouped by host:
    ```
    novaquery status=ACTIVE -A -g OS-EXT-SRV-ATTR:host
    ```

- command line to retrieve the names and id of VMs that have pci_passthrough devices, grouped by host name:
    ```
    novaquery flavor.extra_specs.pci_passthrough:alias -f name -f id -g OS-EXT-SRV-ATTR:host
    ```
