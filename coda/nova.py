# Copyright [2015] Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
All Nova interactions go here.

Not much else to say.
"""


# import logging
# from django.core.cache import cache
from django.conf import settings
import json
import requests


def list_instances(auth_token, region, tenant_id):
    """Return a map keyed with user ids to a map with instance info."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    payload = {'all_tenants': '1', 'tenant_id': tenant_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/%s/servers/detail" % (
                settings.CODA_URL_MAP[region][settings.NOVA_ADMIN_URL_KEY],
                settings.CODA_TENANT_ID),
            headers=headers,
            params=payload,
            verify=False)

        if response.status_code == 200:
            server_dict = json.loads(response.text)

            if "servers" in server_dict:
                sorted_instances = \
                    sorted(server_dict['servers'], key=lambda k: k['user_id'])

                for instance in sorted_instances:
                    if instance['user_id'] not in result.keys():
                        result[instance['user_id']] = []

                    result[instance['user_id']].append(instance)
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def delete_instance(auth_token, region, tenant_id, instance_id):
    """Delete the instance."""
    result = 'Instance Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        payload = {'all_tenants': '1', 'tenant_id': tenant_id}

        response = requests.delete(
            "%s/%s/servers/%s" % (
                settings.CODA_URL_MAP[region][settings.NOVA_ADMIN_URL_KEY],
                settings.CODA_TENANT_ID,
                instance_id),
            headers=headers,
            params=payload,
            verify=False)

        if response.status_code != 204:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result
