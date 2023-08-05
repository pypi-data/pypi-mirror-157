#!/usr/bin/python
""" this is cifs_server module

 (c) 2018-2022, NetApp, Inc
 # GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: na_ontap_cifs_server
short_description: NetApp ONTAP CIFS server configuration
extends_documentation_fragment:
    - netapp.ontap.netapp.na_ontap
version_added: 2.6.0
author: NetApp Ansible Team (@carchi8py) <ng-ansibleteam@netapp.com>

description:
    - Creating / deleting and modifying the CIFS server .

options:

  state:
    description:
      - Whether the specified cifs_server should exist or not.
    default: present
    choices: ['present', 'absent']
    type: str

  service_state:
    description:
      - CIFS Server Administrative Status.
    choices: ['stopped', 'started']
    type: str

  name:
    description:
      - Specifies the cifs_server name.
    required: true
    aliases: ['cifs_server_name']
    type: str

  admin_user_name:
    description:
      - Specifies the cifs server admin username.
      - When used with absent, the account will be deleted if admin_password is also provided.
    type: str

  admin_password:
    description:
      - Specifies the cifs server admin password.
      - When used with absent, the account will be deleted if admin_user_name is also provided.
    type: str

  domain:
    description:
      - The Fully Qualified Domain Name of the Windows Active Directory this CIFS server belongs to.
    type: str

  workgroup:
    description:
      - The NetBIOS name of the domain or workgroup this CIFS server belongs to.
    type: str

  ou:
    description:
      - The Organizational Unit (OU) within the Windows Active Directory this CIFS server belongs to.
    version_added: 2.7.0
    type: str

  force:
    type: bool
    description:
      - When state is present, if this is set and a machine account with the same name as specified in 'name' exists in the Active Directory,
        it will be overwritten and reused.
      - When state is absent, if this is set, the local CIFS configuration is deleted regardless of communication errors.
      - For REST, it requires ontap version 9.11.
    version_added: 2.7.0

  vserver:
    description:
      - The name of the vserver to use.
    required: true
    type: str

  from_name:
    description:
      - Specifies the existing cifs_server name.
      - This option is used to rename cifs_server.
      - Supported only in REST and requires force to be set to True.
      - Requires ontap version 9.11.0.
      - if the service is running, it will be stopped to perform the rename action, and automatically restarts.
      - if the service is stopped, it will be briefly restarted after the rename action, and stopped again.
    type: str
    version_added: 21.19.0

  encrypt_dc_connection:
    description:
      - Specifies whether encryption is required for domain controller connections.
      - Only supported with REST and requires ontap version 9.8 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  kdc_encryption:
    description:
      - Specifies whether AES-128 and AES-256 encryption is enabled for all Kerberos-based communication with the Active Directory KDC.
      - Only supported with REST. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  smb_encryption:
    description:
      - Determine whether SMB encryption is required for incoming CIFS traffic.
      - Only supported with REST. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  smb_signing:
    description:
      - Specifies whether signing is required for incoming CIFS traffic.
      - Only supported with REST. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  restrict_anonymous:
    description:
      - Specifies what level of access an anonymous user is granted.
      - Only supported with REST.
    choices: ['no_enumeration', 'no_restriction', 'no_access']
    type: str
    version_added: 21.20.0

  aes_netlogon_enabled:
    description:
      - Specifies whether or not an AES session key is enabled for the Netlogon channel.
      - Only supported with REST and requires ontap version 9.10.1 or later.
    type: bool
    version_added: 21.20.0

  ldap_referral_enabled:
    description:
      - Specifies whether or not LDAP referral chasing is enabled for AD LDAP connections.
      - Only supported with REST and requires ontap version 9.10.1 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  use_ldaps:
    description:
      - Specifies whether or not to use use LDAPS for secure Active Directory LDAP connections.
      - Only supported with REST and requires ontap version 9.10.1 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  use_start_tls:
    description:
      - Specifies whether or not to use SSL/TLS for allowing secure LDAP communication with Active Directory LDAP servers.
      - Only supported with REST and requires ontap version 9.10.1 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  try_ldap_channel_binding:
    description:
      - Specifies whether or not channel binding is attempted in the case of TLS/LDAPS.
      - Only supported with REST and requires ontap version 9.10.1 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    type: bool
    version_added: 21.20.0

  session_security:
    description:
      - Specifies client session security for AD LDAP connections.
      - Only supported with REST and requires ontap version 9.10.1 or later. Use na_ontap_vserver_cifs_security with ZAPI.
    choices: ['none', 'sign', 'seal']
    type: str
    version_added: 21.20.0

'''

EXAMPLES = '''
    - name: Create cifs_server
      netapp.ontap.na_ontap_cifs_server:
        state: present
        name: data2
        vserver: svm1
        service_state: stopped
        domain: "{{ id_domain }}"
        admin_user_name: "{{ domain_login }}"
        admin_password: "{{ domain_pwd }}"
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

    - name: Delete cifs_server
      netapp.ontap.na_ontap_cifs_server:
        state: absent
        name: data2
        vserver: svm1
        admin_user_name: "{{ domain_login }}"
        admin_password: "{{ domain_pwd }}"
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

    - name: Start cifs_server
      netapp.ontap.na_ontap_cifs_server:
        state: present
        name: data2
        vserver: svm1
        service_state: started
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

    - name: Stop cifs_server
      netapp.ontap.na_ontap_cifs_server:
        state: present
        name: data2
        vserver: svm1
        service_state: stopped
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

    - name: Rename cifs_server - REST
      netapp.ontap.na_ontap_cifs_server:
        state: present
        from_name: data2
        name: cifs
        vserver: svm1
        force: True
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

    - name: Modify cifs_server security - REST
      netapp.ontap.na_ontap_cifs_server:
        state: present
        name: data2
        vserver: svm1
        service_state: stopped
        encrypt_dc_connection: True,
        smb_encryption: True,
        kdc_encryption: True,
        smb_signing: True,
        aes_netlogon_enabled: True,
        ldap_referral_enabled: True,
        session_security: seal,
        try_ldap_channel_binding: False,
        use_ldaps: True,
        use_start_tls": True
        restrict_anonymous: no_access
        domain: "{{ id_domain }}"
        admin_user_name: "{{ domain_login }}"
        admin_password: "{{ domain_pwd }}"
        hostname: "{{ netapp_hostname }}"
        username: "{{ netapp_username }}"
        password: "{{ netapp_password }}"

'''

RETURN = '''
'''

import traceback

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils._text import to_native
import ansible_collections.netapp.ontap.plugins.module_utils.netapp as netapp_utils
from ansible_collections.netapp.ontap.plugins.module_utils.netapp_module import NetAppModule
from ansible_collections.netapp.ontap.plugins.module_utils.netapp import OntapRestAPI
from ansible_collections.netapp.ontap.plugins.module_utils import rest_generic


class NetAppOntapcifsServer:
    """
    object to describe  cifs_server info
    """

    def __init__(self):

        self.argument_spec = netapp_utils.na_ontap_host_argument_spec()
        self.argument_spec.update(dict(
            state=dict(required=False, choices=['present', 'absent'], default='present'),
            service_state=dict(required=False, choices=['stopped', 'started']),
            name=dict(required=True, type='str', aliases=['cifs_server_name']),
            workgroup=dict(required=False, type='str', default=None),
            domain=dict(required=False, type='str'),
            admin_user_name=dict(required=False, type='str'),
            admin_password=dict(required=False, type='str', no_log=True),
            ou=dict(required=False, type='str'),
            force=dict(required=False, type='bool'),
            vserver=dict(required=True, type='str'),
            from_name=dict(required=False, type='str'),
            smb_signing=dict(required=False, type='bool'),
            encrypt_dc_connection=dict(required=False, type='bool'),
            kdc_encryption=dict(required=False, type='bool'),
            smb_encryption=dict(required=False, type='bool'),
            restrict_anonymous=dict(required=False, type='str', choices=['no_enumeration', 'no_restriction', 'no_access']),
            aes_netlogon_enabled=dict(required=False, type='bool'),
            ldap_referral_enabled=dict(required=False, type='bool'),
            session_security=dict(required=False, type='str', choices=['none', 'sign', 'seal']),
            try_ldap_channel_binding=dict(required=False, type='bool'),
            use_ldaps=dict(required=False, type='bool'),
            use_start_tls=dict(required=False, type='bool')
        ))

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            mutually_exclusive=[('use_ldaps', 'use_start_tls')]
        )

        self.na_helper = NetAppModule()
        self.parameters = self.na_helper.set_parameters(self.module.params)

        self.parameters['cifs_server_name'] = self.parameters['name']
        # Set up Rest API
        self.rest_api = OntapRestAPI(self.module)
        unsupported_rest_properties = ['workgroup']
        partially_supported_rest_properties = [['encrypt_dc_connection', (9, 8)], ['aes_netlogon_enabled', (9, 10, 1)], ['ldap_referral_enabled', (9, 10, 1)],
                                               ['session_security', (9, 10, 1)], ['try_ldap_channel_binding', (9, 10, 1)], ['use_ldaps', (9, 10, 1)],
                                               ['use_start_tls', (9, 10, 1)], ['force', (9, 11)]]
        self.use_rest = self.rest_api.is_rest_supported_properties(self.parameters, unsupported_rest_properties, partially_supported_rest_properties)

        if not self.use_rest:
            unsupported_zapi_properties = ['smb_signing', 'encrypt_dc_connection', 'kdc_encryption', 'smb_encryption', 'restrict_anonymous',
                                           'aes_netlogon_enabled', 'ldap_referral_enabled', 'try_ldap_channel_binding', 'session_security',
                                           'use_ldaps', 'use_start_tls']
            used_unsupported_zapi_properties = [option for option in unsupported_zapi_properties if option in self.parameters]
            if used_unsupported_zapi_properties:
                self.module.fail_json(msg="Error: %s options supported only with REST." % " ,".join(unsupported_zapi_properties))
            if not netapp_utils.has_netapp_lib():
                self.module.fail_json(msg=netapp_utils.netapp_lib_is_required())
            self.server = netapp_utils.setup_na_ontap_zapi(module=self.module, vserver=self.parameters['vserver'])

    def get_cifs_server(self):
        """
        Return details about the CIFS-server
        :param:
            name : Name of the name of the cifs_server

        :return: Details about the cifs_server. None if not found.
        :rtype: dict
        """
        cifs_server_info = netapp_utils.zapi.NaElement('cifs-server-get-iter')
        cifs_server_attributes = netapp_utils.zapi.NaElement('cifs-server-config')
        cifs_server_attributes.add_new_child('cifs-server', self.parameters['cifs_server_name'])
        cifs_server_attributes.add_new_child('vserver', self.parameters['vserver'])
        query = netapp_utils.zapi.NaElement('query')
        query.add_child_elem(cifs_server_attributes)
        cifs_server_info.add_child_elem(query)
        result = self.server.invoke_successfully(cifs_server_info, True)
        return_value = None

        if result.get_child_by_name('num-records') and \
                int(result.get_child_content('num-records')) >= 1:

            cifs_server_attributes = result.get_child_by_name('attributes-list').\
                get_child_by_name('cifs-server-config')
            return_value = {
                'cifs_server_name': self.parameters['cifs_server_name'],
                'administrative-status': cifs_server_attributes.get_child_content('administrative-status')
            }

        return return_value

    def create_cifs_server(self):
        """
        calling zapi to create cifs_server
        """
        options = {'cifs-server': self.parameters['cifs_server_name'], 'administrative-status': 'up'
                   if self.parameters.get('service_state') == 'started' else 'down'}
        if 'workgroup' in self.parameters:
            options['workgroup'] = self.parameters['workgroup']
        if 'domain' in self.parameters:
            options['domain'] = self.parameters['domain']
        if 'admin_user_name' in self.parameters:
            options['admin-username'] = self.parameters['admin_user_name']
        if 'admin_password' in self.parameters:
            options['admin-password'] = self.parameters['admin_password']
        if 'ou' in self.parameters:
            options['organizational-unit'] = self.parameters['ou']
        if 'force' in self.parameters:
            options['force-account-overwrite'] = str(self.parameters['force']).lower()

        cifs_server_create = netapp_utils.zapi.NaElement.create_node_with_children(
            'cifs-server-create', **options)

        try:
            self.server.invoke_successfully(cifs_server_create,
                                            enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as exc:
            self.module.fail_json(msg='Error Creating cifs_server %s: %s' %
                                  (self.parameters['cifs_server_name'], to_native(exc)), exception=traceback.format_exc())

    def delete_cifs_server(self):
        """
        calling zapi to create cifs_server
        """
        options = {}
        if 'admin_user_name' in self.parameters:
            options['admin-username'] = self.parameters['admin_user_name']
        if 'admin_password' in self.parameters:
            options['admin-password'] = self.parameters['admin_password']
        if 'force' in self.parameters:
            options['force-account-delete'] = str(self.parameters['force']).lower()

        if options:
            cifs_server_delete = netapp_utils.zapi.NaElement.create_node_with_children('cifs-server-delete', **options)
        else:
            cifs_server_delete = netapp_utils.zapi.NaElement.create_node_with_children('cifs-server-delete')

        try:
            self.server.invoke_successfully(cifs_server_delete,
                                            enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as exc:
            self.module.fail_json(msg='Error deleting cifs_server %s: %s' % (self.parameters['cifs_server_name'], to_native(exc)),
                                  exception=traceback.format_exc())

    def start_cifs_server(self):
        """
        RModify the cifs_server.
        """
        cifs_server_modify = netapp_utils.zapi.NaElement.create_node_with_children(
            'cifs-server-start')
        try:
            self.server.invoke_successfully(cifs_server_modify,
                                            enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as e:
            self.module.fail_json(msg='Error modifying cifs_server %s: %s' % (self.parameters['cifs_server_name'], to_native(e)),
                                  exception=traceback.format_exc())

    def stop_cifs_server(self):
        """
        RModify the cifs_server.
        """
        cifs_server_modify = netapp_utils.zapi.NaElement.create_node_with_children(
            'cifs-server-stop')
        try:
            self.server.invoke_successfully(cifs_server_modify, enable_tunneling=True)
        except netapp_utils.zapi.NaApiError as e:
            self.module.fail_json(msg='Error modifying cifs_server %s: %s' % (self.parameters['cifs_server_name'], to_native(e)),
                                  exception=traceback.format_exc())

    def get_cifs_server_rest(self, from_name=None):
        """
        get details of the cifs_server.
        """
        query = {'svm.name': self.parameters['vserver'],
                 'fields': 'svm.uuid,'
                           'enabled,'
                           'security.smb_encryption,'
                           'security.kdc_encryption,'
                           'security.smb_signing,'
                           'security.restrict_anonymous,'}
        query['name'] = from_name or self.parameters['cifs_server_name']
        api = 'protocols/cifs/services'
        if self.rest_api.meets_rest_minimum_version(self.use_rest, 9, 8):
            query['fields'] += 'security.encrypt_dc_connection,'

        if self.rest_api.meets_rest_minimum_version(self.use_rest, 9, 10, 1):
            security_option_9_10 = ('security.use_ldaps,'
                                    'security.use_start_tls,'
                                    'security.try_ldap_channel_binding,'
                                    'security.session_security,'
                                    'security.ldap_referral_enabled,'
                                    'security.aes_netlogon_enabled,')
            query['fields'] += security_option_9_10
        record, error = rest_generic.get_one_record(self.rest_api, api, query)
        if error:
            self.module.fail_json(msg="Error on fetching cifs: %s" % error)
        if record:
            record['service_state'] = 'started' if record.pop('enabled') else 'stopped'
            return {
                'svm': {'uuid': self.na_helper.safe_get(record, ['svm', 'uuid'])},
                'name': self.na_helper.safe_get(record, ['name']),
                'service_state': self.na_helper.safe_get(record, ['service_state']),
                'smb_signing': self.na_helper.safe_get(record, ['security', 'smb_signing']),
                'encrypt_dc_connection': self.na_helper.safe_get(record, ['security', 'encrypt_dc_connection']),
                'kdc_encryption': self.na_helper.safe_get(record, ['security', 'kdc_encryption']),
                'smb_encryption': self.na_helper.safe_get(record, ['security', 'smb_encryption']),
                'aes_netlogon_enabled': self.na_helper.safe_get(record, ['security', 'aes_netlogon_enabled']),
                'ldap_referral_enabled': self.na_helper.safe_get(record, ['security', 'ldap_referral_enabled']),
                'session_security': self.na_helper.safe_get(record, ['security', 'session_security']),
                'try_ldap_channel_binding': self.na_helper.safe_get(record, ['security', 'try_ldap_channel_binding']),
                'use_ldaps': self.na_helper.safe_get(record, ['security', 'use_ldaps']),
                'use_start_tls': self.na_helper.safe_get(record, ['security', 'use_start_tls']),
                'restrict_anonymous': self.na_helper.safe_get(record, ['security', 'restrict_anonymous'])
            }
        return record

    def service_state_to_bool(self, modify=None):
        if modify and 'service_state' in modify:
            return modify['service_state'] == 'started'
        else:
            return self.parameters.get('service_state') == 'started'

    def build_ad_domain(self):
        ad_domain = {}
        if 'admin_user_name' in self.parameters:
            ad_domain['user'] = self.parameters['admin_user_name']
        if 'admin_password' in self.parameters:
            ad_domain['password'] = self.parameters['admin_password']
        if 'ou' in self.parameters:
            ad_domain['organizational_unit'] = self.parameters['ou']
        if 'domain' in self.parameters:
            ad_domain['fqdn'] = self.parameters['domain']
        return ad_domain

    def create_modify_body_rest(self, body, modify=None):
        """
        Function to define body for create and modify cifs server
        """
        security_options = ['smb_signing', 'encrypt_dc_connection', 'kdc_encryption', 'smb_encryption', 'restrict_anonymous',
                            'aes_netlogon_enabled', 'ldap_referral_enabled', 'try_ldap_channel_binding', 'session_security', 'use_ldaps', 'use_start_tls']
        ad_domain = self.build_ad_domain()
        if ad_domain:
            body['ad_domain'] = ad_domain
        query = {}
        if 'force' in self.parameters:
            query['force'] = self.parameters['force']
        security = {}
        for key in security_options:
            if not modify and key in self.parameters:
                security[key] = self.parameters[key]
            elif modify and key in modify:
                security[key] = modify[key]
        if security:
            body['security'] = security
        return body, query

    def create_cifs_server_rest(self):
        """
        create the cifs_server.
        """
        body = {'svm.name': self.parameters['vserver'],
                'name': self.parameters['cifs_server_name'],
                'enabled': self.service_state_to_bool()}
        body, query = self.create_modify_body_rest(body)
        api = 'protocols/cifs/services'
        dummy, error = rest_generic.post_async(self.rest_api, api, body, query)
        if error is not None:
            self.module.fail_json(msg="Error on creating cifs: %s" % error)

    def delete_cifs_server_rest(self, current):
        """
        delete the cifs_server.
        """
        ad_domain = self.build_ad_domain()
        body = {'ad_domain': ad_domain} if ad_domain else None
        query = {}
        if 'force' in self.parameters:
            query['force'] = self.parameters['force']
        api = 'protocols/cifs/services'
        dummy, error = rest_generic.delete_async(self.rest_api, api, current['svm']['uuid'], query, body=body)
        if error is not None:
            self.module.fail_json(msg="Error on deleting cifs server: %s" % error)

    def modify_cifs_server_rest(self, current, modify):
        """
        Modify the state of CIFS server.
        rename: cifs server should be in stopped state
        """
        body = {}
        body, query = self.create_modify_body_rest(body, modify)
        body['enabled'] = self.service_state_to_bool(modify)
        if 'name' in modify:
            body['name'] = self.parameters['name']
        api = 'protocols/cifs/services'
        dummy, error = rest_generic.patch_async(self.rest_api, api, current['svm']['uuid'], body, query)
        if error is not None:
            self.module.fail_json(msg="Error on modifying cifs server: %s" % error)

    def zapiapply(self):
        """
        calling all cifs_server features
        """

        changed = False
        cifs_server_exists = False
        netapp_utils.ems_log_event("na_ontap_cifs_server", self.server)
        cifs_server_detail = self.get_cifs_server()

        if cifs_server_detail:
            cifs_server_exists = True

            if self.parameters['state'] == 'present':
                administrative_status = cifs_server_detail['administrative-status']
                if self.parameters.get('service_state') == 'started' and administrative_status == 'down':
                    changed = True
                if self.parameters.get('service_state') == 'stopped' and administrative_status == 'up':
                    changed = True
            else:
                # we will delete the CIFs server
                changed = True
        elif self.parameters['state'] == 'present':
            changed = True

        if changed and not self.module.check_mode:
            if self.parameters['state'] == 'present':
                if not cifs_server_exists:
                    self.create_cifs_server()

                elif self.parameters.get('service_state') == 'stopped':
                    self.stop_cifs_server()

                elif self.parameters.get('service_state') == 'started':
                    self.start_cifs_server()

            elif self.parameters['state'] == 'absent':
                self.delete_cifs_server()

        self.module.exit_json(changed=changed)

    def apply(self):
        if not self.use_rest:
            self.zapiapply()
        current = self.get_cifs_server_rest()
        cd_action, rename = None, None
        modify = None
        cd_action = self.na_helper.get_cd_action(current, self.parameters)
        if cd_action == 'create' and 'from_name' in self.parameters:
            cifs_info = self.get_cifs_server_rest(self.parameters['from_name'])
            rename = self.na_helper.is_rename_action(cifs_info, current)
            if rename is None:
                self.module.fail_json(msg='Error renaming cifs server: %s - no cifs server with from_name: %s.'
                                      % (self.parameters['name'], self.parameters['from_name']))
            elif rename:
                if 'force' in self.parameters and self.parameters.get('force') is True:
                    current = cifs_info
                    cd_action = None
                else:
                    self.module.fail_json(msg='Error renaming cifs server from %s to %s without force.'
                                          % (self.parameters['from_name'], self.parameters['name']))
        modify = self.na_helper.get_modified_attributes(current, self.parameters) if cd_action is None else None
        if self.na_helper.changed and not self.module.check_mode:
            if rename:
                current['name'] = self.parameters.get('name')
                self.modify_cifs_server_rest(current, modify)

            if cd_action == 'create':
                self.create_cifs_server_rest()
            elif cd_action == 'delete':
                self.delete_cifs_server_rest(current)

            if modify:
                self.modify_cifs_server_rest(current, modify)
        self.module.exit_json(changed=self.na_helper.changed)


def main():
    cifs_server = NetAppOntapcifsServer()
    cifs_server.apply()


if __name__ == '__main__':
    main()
