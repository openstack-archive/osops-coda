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


from django.conf import settings
import json
import requests

JSON_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}


def get_coda_token():
    """Return the auth token for the coda user."""
    payload = {
        "auth": {
            "tenantId": settings.CODA_TENANT_ID,
            "passwordCredentials": {
                "username": settings.CODA_USERNAME,
                "password": settings.CODA_PASSWORD
            }
        }
    }

    result = 'error'

    try:
        response = requests.post(
            "%s/tokens" % settings.CODA_AUTH_URL,
            data=json.dumps(payload),
            headers=JSON_HEADERS,
            verify=False)

        result = json.loads(response.text)['access']['token']['id']
    except Exception as ex:
        print("error in get_coda_token", ex)

    return result


def get_project_users(auth_token, project_id):
    """Return a map of user info for a given project."""
    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    response = requests.get(
        "%s/tenants/%s/users" % (settings.CODA_KEYSTONE_URL, project_id),
        headers=headers,
        verify=False)

    return json.loads(response.text)['users']


def user_authenticate(tenant_id, username, password):
    """Get the auth token for a user of Coda."""
    payload = {
        "auth": {
            "tenantId": tenant_id,
            "passwordCredentials": {
                "username": username,
                "password": password
            }
        }
    }

    result = 'error'

    try:
        response = requests.post("%s/tokens" % settings.CODA_AUTH_URL,
                                 data=json.dumps(payload),
                                 headers=JSON_HEADERS,
                                 verify=False)
        result = json.loads(response.text)['access']['token']['id']
    except Exception as ex:
        print("error in user_authenticate", ex)

    return result


def project_exists(auth_token, project_id):
    """Check if the project id is valid / exists.

    Returns true with info if it does and false and empty if not.
    """
    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    response = requests.get(
        "%s/tenants/%s" % (settings.CODA_KEYSTONE_URL, project_id),
        headers=headers,
        verify=False)

    if response.status_code == 200:
        return True, json.loads(response.text)
    else:
        return False, ''
