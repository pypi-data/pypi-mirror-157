#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2019, Dag Wieers (@dagwieers) <dag@wieers.com>
# Copyright: (c) 2021, Anvitha Jain (@anvitha-jain) <anvjain@cisco.com>
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: mso_schema_site_bd_l3out
short_description: Manage site-local BD l3out's in schema template
description:
- Manage site-local BDs l3out's in schema template on Cisco ACI Multi-Site.
author:
- Dag Wieers (@dagwieers)
- Anvitha Jain (@anvitha-jain)
options:
  schema:
    description:
    - The name of the schema.
    type: str
    required: yes
  site:
    description:
    - The name of the site.
    type: str
    required: yes
  template:
    description:
    - The name of the template.
    type: str
    required: yes
  bd:
    description:
    - The name of the BD.
    type: str
    required: yes
    aliases: [ name ]
  l3out:
    description:
    - The name of the l3out.
    type: str
  state:
    description:
    - Use C(present) or C(absent) for adding or removing.
    - Use C(query) for listing an object or multiple objects.
    type: str
    choices: [ absent, present, query ]
    default: present
notes:
- The ACI MultiSite PATCH API has a deficiency requiring some objects to be referenced by index.
  This can cause silent corruption on concurrent access when changing/removing on object as
  the wrong object may be referenced. This module is affected by this deficiency.
seealso:
- module: cisco.mso.mso_schema_site_bd
- module: cisco.mso.mso_schema_template_bd
extends_documentation_fragment: cisco.mso.modules
'''

EXAMPLES = r'''
- name: Add a new site BD l3out
  cisco.mso.mso_schema_site_bd_l3out:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema1
    site: Site1
    template: Template1
    bd: BD1
    l3out: L3out1
    state: present
  delegate_to: localhost

- name: Remove a site BD l3out
  cisco.mso.mso_schema_site_bd_l3out:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema1
    site: Site1
    template: Template1
    bd: BD1
    l3out: L3out1
    state: absent
  delegate_to: localhost

- name: Query a specific site BD l3out
  cisco.mso.mso_schema_site_bd_l3out:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema1
    site: Site1
    template: Template1
    bd: BD1
    l3out: L3out1
    state: query
  delegate_to: localhost
  register: query_result

- name: Query all site BD l3outs
  cisco.mso.mso_schema_site_bd_l3out:
    host: mso_host
    username: admin
    password: SomeSecretPassword
    schema: Schema1
    site: Site1
    template: Template1
    bd: BD1
    state: query
  delegate_to: localhost
  register: query_result
'''

RETURN = r'''
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.cisco.mso.plugins.module_utils.mso import MSOModule, mso_argument_spec


def main():
    argument_spec = mso_argument_spec()
    argument_spec.update(
        schema=dict(type='str', required=True),
        site=dict(type='str', required=True),
        template=dict(type='str', required=True),
        bd=dict(type='str', required=True),
        l3out=dict(type='str', aliases=['name']),  # This parameter is not required for querying all objects
        state=dict(type='str', default='present', choices=['absent', 'present', 'query']),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ['state', 'absent', ['l3out']],
            ['state', 'present', ['l3out']],
        ],
    )

    schema = module.params.get('schema')
    site = module.params.get('site')
    template = module.params.get('template').replace(' ', '')
    bd = module.params.get('bd')
    l3out = module.params.get('l3out')
    state = module.params.get('state')

    mso = MSOModule(module)

    # Get schema objects
    schema_id, schema_path, schema_obj = mso.query_schema(schema)

    # Get template
    templates = [t.get('name') for t in schema_obj.get('templates')]
    if template not in templates:
        mso.fail_json(msg="Provided template '{0}' does not exist. Existing templates '{1}'".format(template, ', '.join(templates)))
    template_idx = templates.index(template)

    # Get site
    site_id = mso.lookup_site(site)

    # Get site_idx
    if 'sites' not in schema_obj:
        mso.fail_json(msg="No site associated with template '{0}'. Associate the site with the template using mso_schema_site.".format(template))
    sites = [(s.get('siteId'), s.get('templateName')) for s in schema_obj.get('sites')]
    if (site_id, template) not in sites:
        mso.fail_json(msg="Provided site/template '{0}-{1}' does not exist. Existing sites/templates '{2}'".format(site, template, ', '.join(sites)))

    # Schema-access uses indexes
    site_idx = sites.index((site_id, template))
    # Path-based access uses site_id-template
    site_template = '{0}-{1}'.format(site_id, template)

    payload = dict()
    ops = []
    op_path = ''

    # Get BD
    bd_ref = mso.bd_ref(schema_id=schema_id, template=template, bd=bd)
    bds = [v.get('bdRef') for v in schema_obj.get('sites')[site_idx]['bds']]
    bds_in_temp = [a.get('name') for a in schema_obj['templates'][template_idx]['bds']]
    if bd not in bds_in_temp:
        mso.fail_json(msg="Provided BD '{0}' does not exist. Existing BDs '{1}'".format(bd, ', '.join(bds_in_temp)))

    # If bd not at site level but exists at template level
    if bd_ref not in bds:
        op_path = '/sites/{0}/bds'.format(site_template)
        payload.update(
            bdRef=dict(
                schemaId=schema_id,
                templateName=template,
                bdName=bd,
            ),
        )
    else:
        # Get bd index at site level
        bd_idx = bds.index(bd_ref)

    # Get L3out
    # If bd is at site level
    if 'bdRef' not in payload:
        l3outs = schema_obj.get('sites')[site_idx]['bds'][bd_idx]['l3Outs']
        if l3out is not None and l3out in l3outs:
            l3out_idx = l3outs.index(l3out)
            # FIXME: Changes based on index are DANGEROUS
            op_path = '/sites/{0}/bds/{1}/l3Outs/{2}'.format(site_template, bd, l3out_idx)
            mso.existing = schema_obj.get('sites')[site_idx]['bds'][bd_idx]['l3Outs'][l3out_idx]
        else:
            op_path = '/sites/{0}/bds/{1}/l3Outs'.format(site_template, bd)

    if state == 'query':
        if l3out is None:
            mso.existing = schema_obj.get('sites')[site_idx]['bds'][bd_idx]['l3Outs']
        elif not mso.existing:
            mso.fail_json(msg="L3out '{l3out}' not found".format(l3out=l3out))
        mso.exit_json()

    ops = []

    mso.previous = mso.existing
    if state == 'absent':
        if mso.existing:
            mso.sent = mso.existing = {}
            ops.append(dict(op='remove', path=op_path))

    elif state == 'present':
        if not payload:
            payload = l3out
        else:
            # If bd in payload, add l3out to payload
            payload['l3Outs'] = [l3out]

        mso.sanitize(payload, collate=True)

        if not mso.existing:
            ops.append(dict(op='add', path=op_path + '/-', value=payload))

        mso.existing = l3out

    if not module.check_mode:
        mso.request(schema_path, method='PATCH', data=ops)

    mso.exit_json()


if __name__ == "__main__":
    main()
