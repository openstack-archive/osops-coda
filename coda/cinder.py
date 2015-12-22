# Copyright [2015] Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
All cinder interactions go here.

Not much else to say.
"""


from django.conf import settings
import json
import requests


def list_volumes(auth_token, region, project_id):
    """List volumes."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'all_tenants': '1', 'project_id': project_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/%s/volumes/detail" % (
                settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
                settings.CODA_TENANT_ID),
            headers=headers, params=params, verify=False)

        if response.status_code == 200:
            volumes_dict = json.loads(response.text)

            result = volumes_dict['volumes']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_snapshots(auth_token, region, project_id):
    """List snapshots."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'all_tenants': '1', 'project_id': project_id}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/%s/snapshots/detail" % (
                settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
                settings.CODA_TENANT_ID),
            headers=headers, params=params, verify=False)

        if response.status_code == 200:
            snapshots_dict = json.loads(response.text)

            result = snapshots_dict['snapshots']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_backups(auth_token, region, project_id):
    """List backups."""
    result = {}

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json"
    }
    # todo (nathan) figure out why this changed
    # params = {'all_tenants': '1', 'project_id': project_id}
    params = {}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/%s/backups/detail" % (
                settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
                settings.CODA_TENANT_ID),
            headers=headers, params=params, verify=False)

        if response.status_code == 200:
            backups_dict = json.loads(response.text)

            result = backups_dict['backups']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def delete_volume(auth_token, region, tenant_id, volume_id):
    """Delete volumes."""
    result = 'Volume Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'project_id': tenant_id}

        # todo double check why I used codas tenant id here vs user tenant id
        response = requests.delete("%s/%s/volumes/%s" % (
            settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
            settings.CODA_TENANT_ID,
            volume_id), headers=headers, params=params, verify=False)

        if response.status_code != 202:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def delete_snapshot(auth_token, region, tenant_id, snapshot_id):
    """Delete snapshots."""
    result = 'Snapshot Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'project_id': tenant_id}

        # todo double check why I used codas tenant id here vs user tenant id
        response = requests.delete("%s/%s/snapshots/%s" % (
            settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
            settings.CODA_TENANT_ID,
            snapshot_id), headers=headers, params=params, verify=False)

        if response.status_code != 202:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result


def delete_backup(auth_token, region, tenant_id, backup_id):
    """Delete backups."""
    result = 'Backup Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        params = {'all_tenants': '1', 'project_id': tenant_id}

        # todo double check why I used codas tenant id here vs user tenant id
        response = requests.delete("%s/%s/backups/%s" % (
            settings.CODA_URL_MAP[region][settings.CINDER_ADMIN_URL_KEY],
            settings.CODA_TENANT_ID,
            backup_id), headers=headers, params=params, verify=False)

        if response.status_code != 202:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result
