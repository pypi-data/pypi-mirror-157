#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2018, Mikhail Yohman (@FragmentedPacket) <mikhail.yohman@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: netbox_vrf
short_description: Create, update or delete vrfs within NetBox
description:
  - Creates, updates or removes vrfs from NetBox
notes:
  - Tags should be defined as a YAML list
  - This should be ran with connection C(local) and hosts C(localhost)
author:
  - Mikhail Yohman (@FragmentedPacket)
requirements:
  - pynetbox
version_added: '0.1.0'
extends_documentation_fragment:
  - netbox.netbox.common
options:
  data:
    type: dict
    description:
      - Defines the vrf configuration
    suboptions:
      name:
        description:
          - The name of the vrf
        required: true
        type: str
      rd:
        description:
          - The RD of the VRF. Must be quoted to pass as a string.
        required: false
        type: str
      tenant:
        description:
          - The tenant that the vrf will be assigned to
        required: false
        type: raw
      enforce_unique:
        description:
          - Prevent duplicate prefixes/IP addresses within this VRF
        required: false
        type: bool
      import_targets:
        description:
          - Import targets tied to VRF
        required: false
        type: list
        elements: str
        version_added: 2.0.0
      export_targets:
        description:
          - Export targets tied to VRF
        required: false
        type: list
        elements: str
        version_added: 2.0.0
      description:
        description:
          - The description of the vrf
        required: false
        type: str
      tags:
        description:
          - Any tags that the vrf may need to be associated with
        required: false
        type: list
        elements: raw
      custom_fields:
        description:
          - must exist in NetBox
        required: false
        type: dict
    required: true
"""

EXAMPLES = r"""
- name: "Test NetBox modules"
  connection: local
  hosts: localhost
  gather_facts: False

  tasks:
    - name: Create vrf within NetBox with only required information
      netbox_vrf:
        netbox_url: http://netbox.local
        netbox_token: thisIsMyToken
        data:
          name: Test VRF
        state: present

    - name: Delete vrf within netbox
      netbox_vrf:
        netbox_url: http://netbox.local
        netbox_token: thisIsMyToken
        data:
          name: Test VRF
        state: absent

    - name: Create vrf with all information
      netbox_vrf:
        netbox_url: http://netbox.local
        netbox_token: thisIsMyToken
        data:
          name: Test VRF
          rd: "65000:1"
          tenant: Test Tenant
          enforce_unique: true
          import_targets:
            - "65000:65001"
          export_targets:
            - "65000:65001"
          description: VRF description
          tags:
            - Schnozzberry
        state: present
"""

RETURN = r"""
vrf:
  description: Serialized object as created or already existent within NetBox
  returned: success (when I(state=present))
  type: dict
msg:
  description: Message indicating failure or info about what has been achieved
  returned: always
  type: str
"""

from ansible_collections.netbox.netbox.plugins.module_utils.netbox_utils import (
    NetboxAnsibleModule,
    NETBOX_ARG_SPEC,
)
from ansible_collections.netbox.netbox.plugins.module_utils.netbox_ipam import (
    NetboxIpamModule,
    NB_VRFS,
)
from copy import deepcopy


def main():
    """
    Main entry point for module execution
    """
    argument_spec = deepcopy(NETBOX_ARG_SPEC)
    argument_spec.update(
        dict(
            data=dict(
                type="dict",
                required=True,
                options=dict(
                    name=dict(required=True, type="str"),
                    rd=dict(required=False, type="str"),
                    tenant=dict(required=False, type="raw"),
                    enforce_unique=dict(required=False, type="bool"),
                    import_targets=dict(required=False, type="list", elements="str"),
                    export_targets=dict(required=False, type="list", elements="str"),
                    description=dict(required=False, type="str"),
                    tags=dict(required=False, type="list", elements="raw"),
                    custom_fields=dict(required=False, type="dict"),
                ),
            ),
        )
    )

    required_if = [("state", "present", ["name"]), ("state", "absent", ["name"])]

    module = NetboxAnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True, required_if=required_if
    )

    netbox_vrf = NetboxIpamModule(module, NB_VRFS)
    netbox_vrf.run()


if __name__ == "__main__":  # pragma: no cover
    main()
