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
The Coda views.

Not much else to say right now.
"""


from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
# from django.conf import settings
from horizon import views
import json
from openstack_dashboard.dashboards.coda.coda import cinder
from openstack_dashboard.dashboards.coda.coda import coda
from openstack_dashboard.dashboards.coda.coda import glance
from openstack_dashboard.dashboards.coda.coda import keystone
from openstack_dashboard.dashboards.coda.coda import neutron
from openstack_dashboard.dashboards.coda.coda import nova

DISPATCH_MAP = {
    'instances': nova.list_instances,
    'floating_ips': neutron.list_floating_ips,
    'security_groups': neutron.list_security_groups,
    'networks': neutron.list_networks,
    'subnets': neutron.list_subnets,
    'routers': neutron.list_routers,
    'volumes': cinder.list_volumes,
    'snapshots': cinder.list_snapshots,
    'backups': cinder.list_backups,
    'images': glance.list_images
}


class IndexView(views.APIView):
    """Class based definition of the index view."""

    template_name = 'coda/coda/index.html'

    def get_data(self, request, context, *args, **kwargs):
        """No context needed."""
        return context


def results(request):
    """The results view."""
    project_id = request.POST['project_id']
    update_cache = request.POST.get('update_cache', 'False')

    auth_token = coda.get_auth_token()

    if auth_token == 'error':
        msg = "Coda User failed to authenticate with the Identity Service."
        context = {
            'project_id': project_id,
            'error_message': msg
        }
        return render(request, 'coda/coda/error.html', context)

    project_exists, project_info = keystone.project_exists(
        auth_token,
        project_id)

    if project_exists:
        users = keystone.get_project_users(auth_token, project_id)
        regions = coda.get_coda_regions()

        context = {
            'project_id': project_id,
            'project_info': project_info,
            'users': users,
            'regions': regions,
            'update_cache': update_cache,
        }

        return render(request, 'coda/coda/results.html', context)
    else:
        context = {
            'project_id': project_id
        }
        return render(request, 'coda/coda/no_project.html', context)


def instances(request):
    """The instances view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST.get('update_cache', 'True')

    instances_dict = get_project_resource(
        region,
        project_id,
        'instances',
        update_cache)

    # todo (nathan) fix this later broken during port from hp pub cloud
    # images_key = region + '_coda_images'
    # coda_images = cache.get(images_key)
    coda_images = None

    if coda_images is not None:
        image_list = []

        if 'public' in coda_images:
            image_list.extend(coda_images['public'])

        if project_id in coda_images:
            image_list.extend(coda_images[project_id])

        coda.fill_image_info(instances_dict, image_list)
    else:
        coda.fill_image_info(instances_dict, None)

    return HttpResponse(json.dumps(instances_dict))


def floating_ips(request):
    """The floating ips view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']
    floating_ips_dict = get_project_resource(
        region,
        project_id,
        'floating_ips',
        update_cache)

    return HttpResponse(json.dumps(floating_ips_dict))


def security_groups(request):
    """The security groups view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']

    security_groups_dict = get_project_resource(
        region,
        project_id,
        'security_groups',
        update_cache)

    return HttpResponse(json.dumps(security_groups_dict))


def networks(request):
    """The networks view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']
    networks_dict = get_project_resource(
        region,
        project_id,
        'networks',
        update_cache)

    return HttpResponse(json.dumps(networks_dict))


def subnets(request):
    """The subnets view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']
    subnets_dict = get_project_resource(
        region,
        project_id,
        'subnets',
        update_cache)

    return HttpResponse(json.dumps(subnets_dict))


def routers(request):
    """The routers view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']
    routers_dict = get_project_resource(
        region,
        project_id,
        'routers',
        update_cache)

    return HttpResponse(json.dumps(routers_dict))


def volumes(request):
    """The volumes view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']
    volumes_dict = get_project_resource(
        region,
        project_id,
        'volumes',
        update_cache)
    snapshots_dict = get_project_resource(
        region,
        project_id,
        'snapshots',
        update_cache)
    backups_dict = get_project_resource(
        region,
        project_id,
        'backups',
        update_cache)

    volumes_dict = coda.fill_volume_info(
        volumes_dict,
        snapshots_dict,
        backups_dict)

    return HttpResponse(json.dumps(volumes_dict))


def images(request):
    """The images view."""
    project_id = request.POST['project_id']
    region = request.POST['region']
    update_cache = request.POST['update_cache']

    images_dict = None
    images_key = region + '_' + project_id + '_images'
    project_images = cache.get(images_key)

    if update_cache == 'True':
        images_dict = get_all_images(region, True)
    elif project_images is None:
        images_dict = get_all_images(region, False)

    if images_dict is not None:
        if project_id in images_dict:
            project_images = images_dict[project_id]
        else:
            project_images = {}
        cache.set(images_key, project_images, 600)

    return HttpResponse(json.dumps(project_images))


def get_all_images(region, reload_cache=False):
    """Utility method, might belong elsewhere."""
    images_key = region + '_coda_images'
    coda_images = cache.get(images_key)

    if reload_cache is True or coda_images is None or len(coda_images) == 0:
        auth_token = coda.get_auth_token()
        images_dict = glance.list_all_images(auth_token, region)
        coda_images = images_dict
        cache.set(images_key, coda_images, 3600)

    return coda_images


def confirm_delete(request):
    """The confirm delete view."""
    project_id = request.POST['project_id']
    auth_token = coda.get_auth_token()

    project_exists, project_info = keystone.project_exists(
        auth_token,
        project_id)
    users = keystone.get_project_users(auth_token, project_id)
    regions = coda.get_coda_regions()

    context = {
        'project_id': project_id,
        'project_info': project_info,
        'users': users,
        'regions': regions,
    }

    return render(request, 'coda/coda/confirm_delete.html', context)


def delete_resources(request):
    """The deleting resources view."""
    project_id = request.POST['project_id']
    os_tenant_id = request.POST['os_tenant_id']
    os_username = request.POST['os_username']
    os_password = request.POST['os_password']

    user_token = keystone.user_authenticate(
        os_tenant_id,
        os_username,
        os_password)
    project_exists, project_info = keystone.project_exists(
        user_token,
        project_id)
    users = keystone.get_project_users(user_token, project_id)
    regions = coda.get_coda_regions()

    context = {
        'project_id': project_id,
        'project_info': project_info,
        'users': users,
        'regions': regions,
        'user_token': user_token
    }

    return render(request, 'coda/coda/delete/results.html', context)


def delete_instances(request):
    """The deleting instances view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    instance_dict = remove_project_resource(region, project_id, 'instances')

    if instance_dict is not None:
        for user_id, instance_list in instance_dict.iteritems():
            for instance in instance_list:
                result[instance['id']] = nova.delete_instance(
                    user_token,
                    region,
                    project_id,
                    instance['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_floating_ips(request):
    """The deleting floating ips view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    floating_ips_dict = remove_project_resource(
        region,
        project_id,
        'floating_ips')

    if floating_ips_dict is not None:
        for floating_ip in floating_ips_dict:
            result[floating_ip['id']] = neutron.delete_floating_ip(
                user_token,
                region,
                project_id,
                floating_ip['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_security_groups(request):
    """The deleting security groups view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    security_groups_dict = remove_project_resource(
        region,
        project_id,
        'security_groups')

    if security_groups_dict is not None:
        for sec_group in security_groups_dict:
            result[sec_group['id']] = neutron.delete_security_group(
                user_token,
                region,
                project_id,
                sec_group['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_networks(request):
    """The deleting networks view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    networks_dict = remove_project_resource(region, project_id, 'networks')
    remove_project_resource(region, project_id, 'subnets')

    if networks_dict is not None:
        for network in networks_dict:
            result[network['id']] = neutron.delete_network(
                user_token,
                region,
                project_id,
                network['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_routers(request):
    """The deleting routers view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    routers_dict = remove_project_resource(region, project_id, 'routers')

    if routers_dict is not None:
        for router in routers_dict:
            result[router['id']] = neutron.delete_router(
                user_token,
                region,
                project_id,
                router['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_volumes(request):
    """The deleting volumes view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    volumes_dict = remove_project_resource(region, project_id, 'volumes')

    if volumes_dict is not None:
        for volume in volumes_dict:
            result[volume['id']] = cinder.delete_volume(
                user_token,
                region,
                project_id,
                volume['id'])
    else:
        result = 'ERROR'

    return HttpResponse(json.dumps(result))


def delete_snapshots(request):
    """The deleting snapshots view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    snapshots_dict = remove_project_resource(region, project_id, 'snapshots')

    if snapshots_dict is not None:
        for snapshot in snapshots_dict:
            result[snapshot['id']] = cinder.delete_snapshot(
                user_token,
                region,
                project_id,
                snapshot['id'])

    return HttpResponse(json.dumps(result))


def delete_backups(request):
    """The deleting backups view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    backups_dict = remove_project_resource(region, project_id, 'backups')

    if backups_dict is not None:
        for backup in backups_dict:
            result[backup['id']] = cinder.delete_backup(
                user_token,
                region,
                project_id,
                backup['id'])

    return HttpResponse(json.dumps(result))


def delete_images(request):
    """The deleting images view."""
    result = {}
    project_id = request.POST['project_id']
    user_token = request.POST['user_token']
    region = request.POST['region']

    images_key = region + '_' + project_id + '_images'
    tenant_images = cache.get(images_key)
    error_images = []

    if tenant_images is not None:
        # todo (nathan) improve this
        # remove the tenant image cached
        # cache.delete(images_key)
        # scrubber_images = get_all_images(region)
        # scrubber_images.pop(tenant_id, None)
        # cache.set('scrubber_images', scrubber_images, 3600)

        for image in tenant_images:
            result[image['id']] = glance.delete_image(
                user_token,
                region,
                image['id'])

            if result[image['id']] != 'Image Deleted':
                error_images.append(image)
    else:
        # todo (nathan) log that there were no images to delete
        result = {}

    # related to above, this is hackish, but it works for now
    if len(error_images) > 0:
        cache.set(images_key, error_images, 600)
    else:
        cache.set(images_key, {}, 600)

    return HttpResponse(json.dumps(result))


def get_project_resource(region, project_id, resource, update_cache='True'):
    """Utility method to get resource map from cache."""
    resource_map = 'ERROR'
    resource_key = region + '_' + project_id + '_' + resource

    if resource in DISPATCH_MAP:
        if update_cache == 'True':
            coda_token = coda.get_auth_token()
            resource_map = DISPATCH_MAP[resource](
                coda_token,
                region,
                project_id)
        else:
            resource_map = cache.get(resource_key)

            if resource_map is None:
                coda_token = coda.get_auth_token()
                resource_map = DISPATCH_MAP[resource](
                    coda_token,
                    region,
                    project_id)

        cache.set(resource_key, resource_map, 600)

    return resource_map


def remove_project_resource(region, tenant_id, resource):
    """Utility method to remove resource map from cache."""
    resource_key = region + '_' + tenant_id + '_' + resource
    resource_map = cache.get(resource_key)

    if resource_map is not None:
        cache.delete(resource_key)

    return resource_map
