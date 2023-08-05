#
#    Copyright 2022 - Carlos A. <https://github.com/dealfonso>
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
import osidle.osconnect as oc
import sys
import argparse
import json
from tqdm import tqdm
import os
from osidle.common import p_warning, p_info, p_error, p_debug, p_debugv, s_error
from .version import VERSION


def findInObject(obj, key):
    keys = key.split(".")
    if keys[0] in obj:
        if len(keys) == 1:
            return obj[keys[0]]
        else:
            return findInObject(obj[keys[0]], ".".join(keys[1:]))
    else:
        return None

def copyToObject(dst, src, key):
    keys = key.split(".")
    value = findInObject(src, key)
    if value is not None:
        if len(keys) == 1:
            dst[keys[0]] = value
        else:
            if keys[0] not in dst:
                dst[keys[0]] = {}
            copyToObject(dst[keys[0]], src[keys[0]], ".".join(keys[1:]))

def json2keys(obj, prefix = ""):
    # TODO: return to string
    if isinstance(obj, list):
        for key, value in enumerate(obj):
            json2keys(value, f"{key}" if prefix == "" else f"{prefix}.{key}")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            json2keys(value, f"{key}" if prefix == "" else f"{prefix}.{key}")
    else:
        print(f"{prefix}={obj}")

def main():
    """
    This application enables to retrieve the servers from OpenStack NOVA, using its API. And it enables to filter the servers by
    their attributes. E.g. to query the servers with the attribute "status" set to "ACTIVE", it is possibile to use the following command:
        novaquery status=ACTIVE

    This command also enables to group the results by one attribute, using the following command will obtain the servers that are not
    in the "ACTIVE" status, grouped by the attribute "status":
        novaquery status!=ACTIVE -g status

    Examples:
        - command line to retrieve active VMs, grouped by host:
            novaquery status=ACTIVE -A -g OS-EXT-SRV-ATTR:host

        - command line to retrieve the names and id of VMs that have pci_passthrough devices, grouped by host name:
            novaquery flavor.extra_specs.pci_passthrough:alias -f name -f id -g OS-EXT-SRV-ATTR:host

    """
    parser = argparse.ArgumentParser(allow_abbrev=False, description=main.__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-n", "--no-add-searched", help="Do not add the searched fields to the output", default=True, action="store_false", dest="add_searched")
    parser.add_argument("-A", "--all-fields", help="Add all the fields of the object to the output", default=False, action="store_true", dest="all_fields")
    parser.add_argument("-s", "--starts-with", help="Match value even if only starts with it", action="store_true", default=False, dest="starts_with")
    parser.add_argument("-c", "--contains", help="Match value even if only contains it", action="store_true", default=False, dest="contains")
    parser.add_argument("-f", "--field", help="Field that has to be obtained (if not provided any, will include the fields used to search)", action="append", default=[], dest="fields")
    parser.add_argument("-F", "--format", help="Format of the output", default="json", dest="format", choices=["json", "text"])
    parser.add_argument("-p", "--progress", help="Show progress bar", default=False, action="store_true", dest="progress")
    parser.add_argument("-g", "--group-field", help="Field to group the output by (e.g. OS-EXT-SRV-ATTR:host); will be added to the output", default=None, dest="group_field")
    parser.add_argument("-x", "--nova-api-version", help="The version of the nova api to use (i.e. X-OpenStack-Nova-API-Version header) default: 2.48", default="2.48", dest="apiversion")
    parser.add_argument("-a", "--all-tenants", help="Retrieve the servers from all tenants", default=False, action="store_true", dest="all_tenants")
    parser.add_argument("-U", "--os-username", dest="username", help="OpenStack username (if not set, will be obtained using OS_USERNAME env var)", default=None)
    parser.add_argument("-P", "--os-password", dest="password", help="OpenStack password  (if not set, will be obtained using OS_PASSWORD env var)", default=None)
    parser.add_argument("-H", "--os-auth", dest="keystone", help="OpenStack keytsone authentication endpoint (if not set, will be obtained using OS_AUTH_URL env var)", default=None)
    parser.add_argument("-v", "--version", action='version', version=VERSION)
    parser.add_argument("searchfield", help="Field to search for in the server and the value that we want to match (e.g. flavor.extra_specs.pci_passthrough:alias=V100:1)")
    args = parser.parse_args()

    if args.username is not None:
        os.environ['OS_USERNAME'] = args.username
    if args.password is not None:
        os.environ['OS_PASSWORD'] = args.password
    if args.keystone is not None:
        os.environ['OS_AUTH_URL'] = args.keystone

    if 'OS_AUTH_URL' not in os.environ or os.environ['OS_AUTH_URL'] is None:
        p_error("OS_AUTH_URL environment variable not set")
        sys.exit(1)
    if 'OS_PASSWORD' not in os.environ or os.environ['OS_PASSWORD'] is None:
        p_error("OS_PASSWORD environment variable not set")
        sys.exit(1)
    if 'OS_USERNAME' not in os.environ or os.environ['OS_USERNAME'] is None:
        p_error("OS_USERNAME environment variable not set")
        sys.exit(1)

    # If no field is requested, we interpret that we are requesting the fields used to search
    if len(args.fields) == 0:
        args.add_searched = True

    # Now get a dictionary with the fields to search for and the value to match { "path.to.value": "value", ... }
    search_fields = {}

    searchfield = args.searchfield.split("=")
    value = None
    is_negative = False
    if len(searchfield) > 1:
        value = "=".join(searchfield[1:])
        if searchfield[0][-1] == "!":
            searchfield[0] = searchfield[0][:-1]
            is_negative = True

    search_fields[searchfield[0]] = { "value": value, "negative": is_negative }

    # If the user requested to add the searched fields, add them to the output
    if args.add_searched:
        for field in search_fields:
            args.fields.append(field)

    # Must add the group field to the output fields
    if args.group_field is not None:
        args.fields.append(args.group_field)

    # Let's begin by retrieving the list of servers
    token = oc.Token()
    if not token.get():
        p_error("Unable to get the token. Please check the credentials.")
        sys.exit(1)

    servers = oc.tokenQuery(token, "/servers" + ("?all_tenants=1" if args.all_tenants else ""))

    if servers is not None:
        # The list of objects retrieved
        objects_retrieved = []

        if args.progress:
            pbar = tqdm(total=len(servers['servers']), desc="Processing servers", unit="server")

        for server in servers['servers']:
            current_object = {}

            # Get the link from which to get the information of the server
            server_link = None
            for link in server['links']:
                if link['rel'] == 'self':
                    server_link = link['href']
                    break

            if server_link is None:
                p_warning("Error: Could not find the link to the information from the server")
                break

            # Get the server information
            server_info = oc.tokenQuery(token, server_link, headers={"X-OpenStack-Nova-API-Version": args.apiversion}, timeout=15)

            if server_info is not None:
                server_info = server_info['server']

                for field, value_expression in search_fields.items():
                    object_value = findInObject(server_info, field)

                    value = value_expression['value']
                    # If the object has a value in the searched field, check if it matches the value
                    if object_value is not None:
                        matches = False

                        # If the user did not request a value, we match always                        
                        if value is None:
                            matches = True
                        else:
                            matches = object_value == value
                            if (not matches) and args.starts_with:
                                matches = str(object_value).startswith(value)
                            if (not matches) and args.contains:
                                matches = str(object_value).find(value) != -1

                        if value_expression['negative']:
                            matches = not matches

                        # If matches, store the requested fields
                        if matches:
                            if args.all_fields:
                                current_object = server_info
                            else:
                                for field in args.fields:
                                    v = findInObject(server_info, field)
                                    copyToObject(current_object, server_info, field)

            # Finally store the object
            if len(current_object.keys()) > 0:
                objects_retrieved.append(current_object)

            if args.progress:
                pbar.update(1)

    if args.progress:
        pbar.close()

    # Print the output
    if len(objects_retrieved) > 0:

        if args.group_field is not None:
            grouped = {}
            for object in objects_retrieved:
                v = findInObject(object, args.group_field)
                if v is not None:
                    if v not in grouped:
                        grouped[v] = []
                    grouped[v].append(object)
            objects_retrieved = grouped

        if args.format == "json":
            print(json.dumps(objects_retrieved, indent=4))
        else:
            json2keys(objects_retrieved)
