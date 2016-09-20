# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing images.
"""

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from docker import Client


def get_name_images():
    IMAGES = [('-1', _('Select Image'))]
    cli = Client(base_url='unix://var/run/docker.sock')
    for image in cli.images():
        repo = image['RepoTags']
        repoTags = repo[0]
        IMAGES.append((repoTags, _(repoTags)))

    return IMAGES


class CreateContainerForm(forms.SelfHandlingForm):


    image = forms.ChoiceField(
        label=_('Image Source'),
        choices=get_name_images(),
        )
    name = forms.CharField(max_length=255, label=_("Name Container"),required=False)
    def handle(self, request, data):
        try:
            cli = Client(base_url='unix://var/run/docker.sock')
            cli.create_container(image=data['image'], name=data['name'])
        except Exception:
            exceptions.handle(request, _('Unable to create container.'))
            return False
        return True


