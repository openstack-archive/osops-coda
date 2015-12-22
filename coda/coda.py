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

"""Code that is specific to Coda.

Methods that aren't specific to an OpenStack API go here.
"""


from django.conf import settings
from django.core.cache import cache
from openstack_dashboard.dashboards.coda.coda import keystone

CODA_CACHE = 'coda_cache'


def get_coda_regions():
    """Return a list of regions for the Coda installation."""
    return settings.CODA_URL_MAP.keys()


def get_auth_token():
    """Abstract getting the Coda auth token from cache or API as needed."""
    coda_cache = {}

    if cache.get(CODA_CACHE) is not None:
        coda_cache = cache.get(CODA_CACHE)

    if 'coda_token' not in coda_cache:
        coda_token = keystone.get_coda_token()
        coda_cache['coda_token'] = coda_token
        # keep for an hour
        cache.set('coda_cache', coda_cache, 3600)
    else:
        coda_token = coda_cache['coda_token']

    return coda_token


def fill_image_info(instances, images):
    """Use image dict to fill in image name for instances."""
    for user_id in instances:
        for instance in instances[user_id]:
            if images is None:
                instance['image']['name'] = "Image Info Unavailable"
            else:
                for image in images:
                    if image['id'] == instance['image']['id']:
                        instance['image']['name'] = image['name']
                        break

                if 'name' not in instance['image']:
                    instance['image']['name'] = "Error Getting Image Info"

    return instances


def fill_volume_info(volumes, snapshots, backups):
    """Unify volume, snapshot, and backup in a single dict."""

    print backups
    for volume in volumes:
        volume['snapshots'] = []
        volume['backups'] = []

        for snapshot in snapshots:
            if snapshot['volume_id'] == volume['id']:
                volume['snapshots'].append(snapshot)

        for backup in backups:
            if backup['volume_id'] == volume['id']:
                volume['backups'].append(backup)

    return volumes


def is_project_black_listed(project_id):
    """Check if a project ID is blacklisted (i.e. shouldn't be cleaned)."""
    return project_id in settings.CODA_BLACK_LIST
