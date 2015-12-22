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
All keystone interactions go here.

Not much else to say.
"""


# import logging
# from django.core.cache import cache
from django.conf import settings
import json
import requests


def list_floating_ips(auth_token, region, project_id):
    """Return a list of maps with floating ip info."""
    result = {}

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }
        params = {'all_tenants': '1', 'tenant_id': project_id}
        col_filter = "fields=id&fields=floating_ip_address"
        col_filter += "&fields=fixed_ip_address&fields=port_id"

        response = requests.get(
            "%s/floatingips?%s" % (
                settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                col_filter),
            headers=headers, params=params, verify=False)

        if response.status_code == 200:
            floating_ip_dict = json.loads(response.text)

            result = floating_ip_dict['floatingips']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_security_groups(auth_token, region, project_id):
    """Return a list of maps with security group info."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'all_tenants': '1', 'tenant_id': project_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/security-groups" %
            settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
            headers=headers,
            params=params, verify=False)

        if response.status_code == 200:
            sec_group_dict = json.loads(response.text)

            result = sec_group_dict['security_groups']
            result = remove_default_security_group(result)
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_networks(auth_token, region, project_id):
    """List networks."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'all_tenants': '1', 'tenant_id': project_id}

    if region in settings.CODA_URL_MAP:
        result[region] = {}

        response = requests.get(
            "%s/networks" %
            settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
            headers=headers,
            params=params,
            verify=False)

        if response.status_code == 200:
            network_dict = json.loads(response.text)

            result = network_dict['networks']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_subnets(auth_token, region, project_id):
    """List subnets."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'all_tenants': '1', 'tenant_id': project_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/subnets" %
            settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
            headers=headers,
            params=params,
            verify=False)

        if response.status_code == 200:
            subnet_dict = json.loads(response.text)

            result = subnet_dict['subnets']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_routers(auth_token, region, project_id):
    """List routers."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'tenant_id': project_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/routers" %
            settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
            headers=headers,
            params=params,
            verify=False)

        if response.status_code == 200:
            router_dict = json.loads(response.text)

            result = router_dict['routers']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def delete_floating_ip(auth_token, region, tenant_id, floating_ip_id):
    """Delete floating ips."""
    result = 'Floating IP Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'tenant_id': tenant_id, 'fields': 'id'}

        response = requests.delete(
            "%s/floatingips/%s" % (
                settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                floating_ip_id),
            headers=headers,
            params=params,
            verify=False)

        if response.status_code != 204:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def delete_security_group(auth_token, region, tenant_id, security_group_id):
    """Delete security groups."""
    result = 'Security Group Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'tenant_id': tenant_id}

        response = requests.delete(
            "%s/security-groups/%s" % (
                settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                security_group_id),
            headers=headers,
            params=params,
            verify=False)

        if response.status_code != 204:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def delete_network(auth_token, region, tenant_id, network_id):
    """Delete networks."""
    result = 'Network Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'tenant_id': tenant_id}

        response = requests.delete(
            "%s/networks/%s" % (
                settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                network_id),
            headers=headers,
            params=params,
            verify=False)

        if response.status_code != 204:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def delete_router(auth_token, region, tenant_id, router_id):
    """Delete routers."""
    result = 'Router Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        ports = list_ports_for_device(
            auth_token,
            settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
            tenant_id,
            router_id)
        port_error = False

        for port in ports:
            data = {'port_id': port['id']}

            response = requests.put(
                "%s/routers/%s/remove_router_interface" %
                (settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                 router_id),
                headers=headers,
                data=json.dumps(data),
                verify=False)

            if response.status_code != 200:
                result = "Couldn't remove port id [%s]. Delete aborted." \
                         % port['id']
                port_error = True
                break

        # Remove the router if the interfaces were cleared ok.
        if not port_error:
            params = {'all_tenants': '1', 'tenant_id': tenant_id}
            response = requests.delete(
                "%s/routers/%s" %
                (settings.CODA_URL_MAP[region][settings.NEUTRON_ADMIN_URL_KEY],
                 router_id),
                headers=headers,
                params=params,
                verify=False)

            if response.status_code != 204:
                result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def list_ports_for_device(auth_token, url_base, tenant_id, device_id):
    """Utility method used by delete."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {
        'all_tenants': '1',
        'tenant_id': tenant_id,
        'device_id': device_id,
    }
    response = requests.get(
        "%s/ports" % url_base,
        headers=headers,
        params=params,
        verify=False)

    if response.status_code == 200:
        ports_dict = json.loads(response.text)

        result = ports_dict['ports']

    return result


def remove_default_security_group(security_groups):
    """Utility method to prevent default sec group from displaying."""
    # todo (nathan) awful, use a list comprehension for this
    result = []
    for group in security_groups:
        if group['name'] != 'default':
            result.append(group)

    return result
