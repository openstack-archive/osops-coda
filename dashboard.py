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

"""The coda dashboard module.

Coda is a Horizon dashboard and panel (both share the name) that
facilitates resource clean up of a project once that project is no longer
needed http://openstack.org
"""


from django.utils.translation import ugettext_lazy as _

import horizon


class Codagroup(horizon.PanelGroup):
    """Defines the coda group, currently not used."""

    slug = "codagroup"
    name = _("Coda Group")
    panels = ('coda',)


class Coda(horizon.Dashboard):
    """The coda panel."""

    name = _("Coda")
    slug = "coda"
    panels = ('coda',)
    default_panel = 'coda'


horizon.register(Coda)
