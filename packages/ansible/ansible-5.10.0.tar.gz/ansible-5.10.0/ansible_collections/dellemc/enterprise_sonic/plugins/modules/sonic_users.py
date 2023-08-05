#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2019 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the resource
#   module builder playbook.
#
# Do not edit this file manually.
#
# Changes to this file will be over written
#   by the resource module builder.
#
# Changes should be made in the model used to
#   generate this file or in the resource module
#   builder template.
#
#############################################

"""
The module file for sonic_users
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = """
---
module: sonic_users
version_added: 1.1.0
notes:
- Tested against Enterprise SONiC Distribution by Dell Technologies.
- Supports C(check_mode).
author: Niraimadaiselvam M (@niraimadaiselvamm)
short_description: Manage users and its parameters
description:
  - This module provides configuration management of users parameters on devices running Enterprise SONiC.
options:
  config:
    description:
      - Specifies the users related configuration.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Specifies the name of the user.
        type: str
        required: true
      role:
        description:
          - Specifies the role of the user.
        type: str
        choices:
          - admin
          - operator
      password:
        description:
          - Specifies the password of the user.
        type: str
      update_password:
        description:
          - Specifies the update password flag.
          - In case of always, password will be updated every time.
          - In case of on_create, password will be updated only when user is created.
        type: str
        choices:
          - always
          - on_create
        default: always
  state:
    description:
      - Specifies the operation to be performed on the users configured on the device.
      - In case of merged, the input configuration will be merged with the existing users configuration on the device.
      - In case of deleted the existing users configuration will be removed from the device.
    default: merged
    choices: ['merged', 'deleted']
    type: str
"""
EXAMPLES = """
# Using deleted
#
# Before state:
# -------------
#
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin
#username sysadmin password $6$3QNqJzpFAPL9JqHA$417xFKw6SRn.CiqMFJkDfQJXKJGjeYwi2A8BIyfuWjGimvunOOjTRunVluudey/W9l8jhzN1oewBW5iLxmq2Q1 role admin
#username sysoperator password $6$s1eTVjcX4Udi69gY$zlYgqwoKRGC6hGL5iKDImN/4BL7LXKNsx9e5PoSsBLs6C80ShYj2LoJAUZ58ia2WNjcHXhTD1p8eU9wyRTCiE0 role operator
#
- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_users:
    config:
      - name: sysoperator
    state: deleted
# After state:
# ------------
#
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin
#username sysadmin password $6$3QNqJzpFAPL9JqHA$417xFKw6SRn.CiqMFJkDfQJXKJGjeYwi2A8BIyfuWjGimvunOOjTRunVluudey/W9l8jhzN1oewBW5iLxmq2Q1 role admin


# Using deleted
#
# Before state:
# -------------
#
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin
#username sysadmin password $6$3QNqJzpFAPL9JqHA$417xFKw6SRn.CiqMFJkDfQJXKJGjeYwi2A8BIyfuWjGimvunOOjTRunVluudey/W9l8jhzN1oewBW5iLxmq2Q1 role admin
#username sysoperator password $6$s1eTVjcX4Udi69gY$zlYgqwoKRGC6hGL5iKDImN/4BL7LXKNsx9e5PoSsBLs6C80ShYj2LoJAUZ58ia2WNjcHXhTD1p8eU9wyRTCiE0 role operator
#
- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_users:
    config:
    state: deleted

# After state:
# ------------
#
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin


# Using merged
#
# Before state:
# -------------
#
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin
#
- name: Merge users configurations
  dellemc.enterprise_sonic.sonic_users:
    config:
      - name: sysadmin
        role: admin
        password: admin
        update_password: always
      - name: sysoperator
        role: operator
        password: operator
        update_password: always
    state: merged

# After state:
# ------------
#!
#do show running-configuration
#!
#username admin password $6$sdZt2C7F$3oPSRkkJyLZtsKlFNGWdwssblQWBj5dXM6qAJAQl7dgOfqLSpZJ/n6xf8zPRcqPUFCu5ZKpEtynJ9sZ/S8Mgj. role admin
#username sysadmin password $6$3QNqJzpFAPL9JqHA$417xFKw6SRn.CiqMFJkDfQJXKJGjeYwi2A8BIyfuWjGimvunOOjTRunVluudey/W9l8jhzN1oewBW5iLxmq2Q1 role admin
#username sysoperator password $6$s1eTVjcX4Udi69gY$zlYgqwoKRGC6hGL5iKDImN/4BL7LXKNsx9e5PoSsBLs6C80ShYj2LoJAUZ58ia2WNjcHXhTD1p8eU9wyRTCiE0 role operator


"""
RETURN = """
before:
  description: The configuration prior to the model invocation.
  returned: always
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
after:
  description: The resulting configuration model invocation.
  returned: when changed
  type: list
  sample: >
    The configuration returned will always be in the same format
     of the parameters above.
commands:
  description: The set of commands pushed to the remote device.
  returned: always
  type: list
  sample: ['command 1', 'command 2', 'command 3']
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.argspec.users.users import UsersArgs
from ansible_collections.dellemc.enterprise_sonic.plugins.module_utils.network.sonic.config.users.users import Users


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(argument_spec=UsersArgs.argument_spec,
                           supports_check_mode=True)

    result = Users(module).execute_module()
    module.exit_json(**result)


if __name__ == '__main__':
    main()
