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
All glance interactions go here.

Not much else to say.
"""

from django.conf import settings
import json
import requests


def list_images(auth_token, region, tenant_id):
    """List all images for a project."""
    result = {}
    limit = 1000

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }

    params = {
        'limit': limit,
        'is_public': 'None',
        'property-owner_id': tenant_id,
    }

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/images/detail" %
            settings.CODA_URL_MAP[region][settings.GLANCE_ADMIN_URL_KEY],
            headers=headers,
            params=params,
            verify=False)

        if response.status_code == 200:
            images_dict = json.loads(response.text)

            result = images_dict['images']
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified.", region

    return result


def list_all_images(auth_token, region):
    """List all images for a region."""
    result = {'public': []}
    images = []
    limit = 1000

    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'limit': limit}

    if region in settings.CODA_URL_MAP:
        response = requests.get(
            "%s/images" %
            settings.CODA_URL_MAP[region][settings.GLANCE_ADMIN_URL_KEY],
            headers=headers, params=params, verify=False)

        if response.status_code == 200:
            images_dict = json.loads(response.text)
            count = len(images_dict['images'])

            if count < limit:
                images.extend(images_dict['images'])
            else:
                marker = images_dict['images'][count - 1]['id']
                images = get_next_images(auth_token, region, limit,
                                         images_dict['images'], marker)
        else:
            result['error'] = \
                repr(response.status_code) + " - " + response.text
    else:
        result['error'] = "Invalid region %s specified." % region

    for image in images:
        if image['owner'] is None and image['is_public'] is True:
            result['public'].append(image)
        else:
            if image['owner'] not in result:
                result[image['owner']] = []

            result[image['owner']].append(image)

    return result


def get_next_images(auth_token, region, limit, images, marker):
    """Recursive method used to list all images for a region."""
    headers = {
        "X-Auth-Token": auth_token,
        "Accept": "application/json",
    }
    params = {'limit': limit, 'is_public': 'None', 'marker': marker}

    response = requests.get(
        "%s/images/detail" %
        settings.CODA_URL_MAP[region][settings.GLANCE_ADMIN_URL_KEY],
        headers=headers,
        params=params,
        verify=False)

    if response.status_code == 200:
        images_dict = json.loads(response.text)
        count = len(images_dict['images'])

        if len(images_dict['images']) < limit:
            images.extend(images_dict['images'])
        else:
            images.extend(images_dict['images'])
            marker = images_dict['images'][count - 1]['id']
            images = get_next_images(auth_token, region, limit, images, marker)
    else:
        # todo (nathan) throw exception here
        print("todo throw exception")

    return images


def delete_image(auth_token, region, image_id):
    """Delete the image."""
    result = 'Image Deleted'

    if region in settings.CODA_URL_MAP:
        headers = {
            "X-Auth-Token": auth_token,
            "Accept": "application/json",
        }

        response = requests.delete(
            "%s/images/%s" % (
                settings.CODA_URL_MAP[region][settings.GLANCE_ADMIN_URL_KEY],
                image_id),
            headers=headers,
            verify=False)

        if response.status_code != 204:
            result = repr(response.status_code) + " - " + response.text
    else:
        result = "Invalid region %s specified.", region

    return result
