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
Url patterns for Coda.

Not much else to say.
"""


from django.conf.urls import patterns
from django.conf.urls import url

from openstack_dashboard.dashboards.coda.coda import views


urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^results/$', views.results, name='results'),
    url(r'^instances/$', views.instances, name='instances'),
    url(r'^floating_ips/$', views.floating_ips, name='floating_ips'),
    url(r'^security_groups/$', views.security_groups, name='security_groups'),
    url(r'^networks/$', views.networks, name='networks'),
    url(r'^subnets/$', views.subnets, name='subnets'),
    url(r'^routers/$', views.routers, name='routers'),
    url(r'^volumes/$', views.volumes, name='volumes'),
    url(r'^images/$', views.images, name='images'),
    url(r'^confirm_delete/$', views.confirm_delete, name='confirm_delete'),
    url(r'^delete/results/$', views.delete_resources, name='delete_resources'),
    url(r'^delete/instances/$',
        views.delete_instances,
        name='delete_instances'),
    url(r'^delete/floating_ips/$',
        views.delete_floating_ips,
        name='delete_floating_ips'),
    url(r'^delete/security_groups/$',
        views.delete_security_groups,
        name='delete_security_groups'),
    url(r'^delete/networks/$', views.delete_networks, name='delete_networks'),
    url(r'^delete/routers/$', views.delete_routers, name='delete_routers'),
    url(r'^delete/snapshots/$', views.delete_snapshots,
        name='delete_snapshots'),
    url(r'^delete/backups/$', views.delete_backups, name='delete_backups'),
    url(r'^delete/volumes/$', views.delete_volumes, name='delete_volumes'),
    url(r'^delete/images/$', views.delete_images, name='delete_images'),
)
