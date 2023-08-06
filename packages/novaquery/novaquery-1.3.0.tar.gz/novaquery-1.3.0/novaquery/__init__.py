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
from .cache import CacheFile

def convert_lists_of_object(obj):
    if isinstance(obj, dict):
        listable = True
        try:
            [ int(k) for k, v in obj.items() ]
        except:
            listable = False
        if listable:
            obj = [ convert_lists_of_object(v) for k, v in obj.items() ]
        else:
            for k, v in obj.items():
                obj[k] = convert_lists_of_object(v)
    return obj

def findInObject(obj, key):
    keys = key.split(".")
    if keys[0] in obj:
        if len(keys) == 1:
            return obj[keys[0]]
        else:
            return findInObject(obj[keys[0]], ".".join(keys[1:]))
    else:
        if isinstance(obj, list):
            try:
                keys[0] = int(keys[0])
            except:
                return None
            if keys[0] < len(obj):
                if len(keys) == 1:
                    return obj[keys[0]]
                else:
                    return findInObject(obj[keys[0]], ".".join(keys[1:]))
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
            if isinstance(src, list):
                try:
                    # Why we do in this way: because the key may be an integer for the list, but in the destination
                    #   maybe we do not want to copy all the keys even if they are integers. So we safely transform
                    #   the list into a dictionary whose keys are the string of the integer.
                    nkey0 = int(keys[0])
                    copyToObject(dst[keys[0]], src[nkey0], ".".join(keys[1:]))
                except Exception as e:
                    # Do not know what to do with this
                    pass
            else:
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
    parser.add_argument("-X", "--clear-cache", help="Forces clearing the cache prior to querying OpenStack (cache is valid for 10 min.)", default=False, action="store_true", dest="clear_cache")
    parser.add_argument("-O", "--cache-only", help="Use only the data in the cache", default=False, action="store_true", dest="cache_only")
    parser.add_argument("-k", "--no-convert-dict-to-list", help="Do not try to convert dictionaries of resulting objects to lists, even if they have all numeric keys", default=False, dest="keep_dicts", action="store_true")
    parser.add_argument("-v", "--version", action='version', version=VERSION)
    parser.add_argument("searchfield", help="Fields to search for in the server and the value that we want to match (e.g. flavor.extra_specs.pci_passthrough:alias=V100:1); if multiple query args are used, the behavior is 'or'",nargs="*")
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

    for searchfield in args.searchfield:
        searchfield = searchfield.split("=")
        value = None
        is_negative = False
        if len(searchfield) > 1:
            value = "=".join(searchfield[1:])
            if searchfield[0][-1] == "!":
                searchfield[0] = searchfield[0][:-1]
                is_negative = True

        search_fields[searchfield[0]] = { "value": value, "negative": is_negative }

    # Prepare the cache
    cache = CacheFile.create("~/.novaquery/servers")
    if args.cache_only:
        cache.validity = -1
    if args.clear_cache:
        cache.clear()

    # If the user requested to add the searched fields, add them to the output
    if args.add_searched:
        for field in search_fields:
            args.fields.append(field)

    # If no fields are requested, we interpret that we are requesting the fields used to search
    if len(args.fields) == 0:
        args.all_fields = True

    # Must add the group field to the output fields
    group_added = False
    if (args.group_field is not None) and (not args.all_fields):
        # Let's check whether the group field is a subfield of a field (in that case we'll not add it because it adds hidden complexity)
        containers = list(filter(lambda x: args.group_field.find(f"{x}.") == 0, args.fields))
        if len(containers) == 0:
            args.fields.append(args.group_field)
            group_added = True

    if args.cache_only:
        # Build a fake server list with the servers in the cache
        servers = {
            'servers': [ {'links':[{'rel': 'self', 'href': url}]} for url in cache.keys ]
        }
    else:
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

            server_info = cache.get(server_link)
            if server_info is None:
                # Get the server information
                server_info = oc.tokenQuery(token, server_link, headers={"X-OpenStack-Nova-API-Version": args.apiversion}, timeout=15)
                cache.add(server_link, server_info)

            if server_info is not None:
                server_info = server_info['server']

                # At first, the object does not match the search fields
                matches = False

                if len(search_fields) > 0:
                    for field, value_expression in search_fields.items():
                        object_value = findInObject(server_info, field)

                        value = value_expression['value']
                        # If the object has a value in the searched field, check if it matches the value
                        if object_value is not None:

                            # If the user did not request a value, we match always                        
                            if value is None:
                                matches = True
                            else:
                                if type(object_value) == type(value):
                                    matches = object_value == value
                                else:
                                    matches = str(object_value) == str(value)
                                if (not matches) and args.starts_with:
                                    matches = str(object_value).startswith(str(value))
                                if (not matches) and args.contains:
                                    matches = str(object_value).find(str(value)) != -1

                            if value_expression['negative']:
                                matches = not matches

                            # If matches, store the requested fields
                            if matches:
                                break
                else:
                    matches = True
                
                if matches:
                    # If there are no search fields, it will understand that we want any object
                    if args.all_fields:
                        current_object = server_info
                    else:
                        for field in args.fields:
                            copyToObject(current_object, server_info, field)

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
                    if not args.keep_dicts:
                        object = convert_lists_of_object(object)
                    grouped[v].append(object)
            objects_retrieved = grouped
        else:
            # Finally store the object
            if not args.keep_dicts:
                objects_retrieved = [ convert_lists_of_object(o) for o in objects_retrieved ]

        if args.format == "json":
            print(json.dumps(objects_retrieved, indent=4))
        else:
            json2keys(objects_retrieved)
