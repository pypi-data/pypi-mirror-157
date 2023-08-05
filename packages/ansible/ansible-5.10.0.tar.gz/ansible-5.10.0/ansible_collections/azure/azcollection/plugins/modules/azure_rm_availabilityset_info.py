#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2016, Julien Stroheker <juliens@microsoft.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: azure_rm_availabilityset_info

version_added: "0.1.2"

short_description: Get Azure Availability Set facts

description:
    - Get facts for a specific availability set or all availability sets.

options:
    name:
        description:
            - Limit results to a specific availability set.
        type: str
    resource_group:
        description:
            - The resource group to search for the desired availability set.
        type: str
    tags:
        description:
            - Limit results by providing a list of tags. Format tags as 'key' or 'key:value'.
        type: list
        elements: str

extends_documentation_fragment:
    - azure.azcollection.azure

author:
    - Julien Stroheker (@julienstroheker)
'''

EXAMPLES = '''
    - name: Get facts for one availability set
      azure_rm_availabilityset_info:
        name: Testing
        resource_group: myResourceGroup

    - name: Get facts for all availability sets in a specific resource group
      azure_rm_availabilityset_info:
        resource_group: myResourceGroup
        tags:
          - key
          - key:value

'''

RETURN = '''
azure_availabilityset:
    description: List of availability sets dicts.
    returned: always
    type: complex
    contains:
        location:
            description:
                - Location where the resource lives.
            type: str
            sample: eastus2
        name:
            description:
                - Resource name.
            type: str
            sample: myAvailabilitySet
        properties:
            description:
                - The properties of the resource.
            type: dict
            contains:
                platformFaultDomainCount:
                    description:
                        - Fault Domain count.
                    type: int
                    sample: 3
                platformUpdateDomainCount:
                    description:
                        - Update Domain count.
                    type: int
                    sample: 2
                virtualMachines:
                    description:
                        - A list of references to all virtualmachines in the availability set.
                    type: list
                    sample: []
        sku:
            description:
                - Location where the resource lives.
            type: str
            sample: Aligned
        type:
            description:
                - Resource type.
            type: str
            sample: "Microsoft.Compute/availabilitySets"
        tags:
            description:
                - Resource tags.
            type: dict
            sample: { env: sandbox }
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase

try:
    from azure.core.exceptions import ResourceNotFoundError
except Exception:
    # handled in azure_rm_common
    pass

AZURE_OBJECT_CLASS = 'AvailabilitySet'


class AzureRMAvailabilitySetInfo(AzureRMModuleBase):
    """Utility class to get availability set facts"""

    def __init__(self):

        self.module_args = dict(
            name=dict(type='str'),
            resource_group=dict(type='str'),
            tags=dict(type='list', elements='str')
        )

        self.results = dict(
            changed=False,
            ansible_info=dict(
                azure_availabilitysets=[]
            )
        )

        self.name = None
        self.resource_group = None
        self.tags = None

        super(AzureRMAvailabilitySetInfo, self).__init__(
            derived_arg_spec=self.module_args,
            supports_check_mode=True,
            supports_tags=False,
            facts_module=True
        )

    def exec_module(self, **kwargs):

        is_old_facts = self.module._name == 'azure_rm_availabilityset_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_availabilityset_facts' module has been renamed to 'azure_rm_availabilityset_info'", version=(2.9, ))

        for key in self.module_args:
            setattr(self, key, kwargs[key])

        if self.name and not self.resource_group:
            self.fail("Parameter error: resource group required when filtering by name.")
        if self.name:
            self.results['ansible_info']['azure_availabilitysets'] = self.get_item()
        else:
            self.results['ansible_info']['azure_availabilitysets'] = self.list_items()

        return self.results

    def get_item(self):
        """Get a single availability set"""

        self.log('Get properties for {0}'.format(self.name))

        item = None
        result = []

        try:
            item = self.compute_client.availability_sets.get(self.resource_group, self.name)
        except ResourceNotFoundError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            avase = self.serialize_obj(item, AZURE_OBJECT_CLASS)
            avase['name'] = item.name
            avase['type'] = item.type
            avase['sku'] = item.sku.name
            result = [avase]

        return result

    def list_items(self):
        """Get all availability sets"""

        self.log('List all availability sets')

        try:
            response = self.compute_client.availability_sets.list(self.resource_group)
        except ResourceNotFoundError as exc:
            self.fail('Failed to list all items - {0}'.format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                avase = self.serialize_obj(item, AZURE_OBJECT_CLASS)
                avase['name'] = item.name
                avase['type'] = item.type
                avase['sku'] = item.sku.name
                results.append(avase)

        return results


def main():
    """Main module execution code path"""

    AzureRMAvailabilitySetInfo()


if __name__ == '__main__':
    main()
