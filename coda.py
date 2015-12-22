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

"""Settings for the coda panel.

There may be a better way or place to do this but for now this works
so I'm rolling with it.
"""

CODA_USERNAME = "coda_admin"
CODA_TENANT_NAME = "coda_admin"
CODA_TENANT_ID = "coda_project_id"
CODA_PASSWORD = "coda_pw"
CODA_AUTH_URL = "http://127.0.0.1:5000/v2.0/"
CODA_KEYSTONE_URL = "http://10.23.214.201:35357/v2.0/"

CODA_AUTH_URL_KEY = "CODA_AUTH_URL"
NOVA_ADMIN_URL_KEY = "NOVA_ADMIN_URL"
NEUTRON_ADMIN_URL_KEY = "NEUTRON_ADMIN_URL"
CINDER_ADMIN_URL_KEY = "CINDER_ADMIN_URL"
GLANCE_ADMIN_URL_KEY = "GLANCE_ADMIN_URL"

CODA_BLACK_LIST = ["00000000001001", "15420898376896"]

CODA_URL_MAP = {
    "region-a": {
        "CODA_AUTH_URL": "http://127.0.0.1:35357/v2.0/",
        "NOVA_ADMIN_URL": "http://127.0.0.1:8774/v2",
        "NEUTRON_ADMIN_URL": "http://127.0.0.1:9696/v2.0",
        "CINDER_ADMIN_URL": "http://127.0.0.1:8776/v2",
        "GLANCE_ADMIN_URL": "http://127.0.0.1:9292/v2",
    },
    # "region-b": {
    #     "CODA_AUTH_URL": "https://127.0.0.1:35357/v2.0/",
    #     "NOVA_ADMIN_URL": "https://127.0.0.1/v2",
    #     "NEUTRON_ADMIN_URL": "https://127.0.0.1/v2.0",
    #     "CINDER_ADMIN_URL": "https://127.0.0.1:8776/v1",
    #     "GLANCE_ADMIN_URL": "https://127.0.0.1:9292/v1.0",
    # },
}
