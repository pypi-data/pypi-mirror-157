#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Google
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# ----------------------------------------------------------------------------
#
#     ***     AUTO GENERATED CODE    ***    AUTO GENERATED CODE     ***
#
# ----------------------------------------------------------------------------
#
#     This file is automatically generated by Magic Modules and manual
#     changes will be clobbered when the file is regenerated.
#
#     Please read more about how to change this file at
#     https://www.github.com/GoogleCloudPlatform/magic-modules
#
# ----------------------------------------------------------------------------

from __future__ import absolute_import, division, print_function

__metaclass__ = type

################################################################################
# Documentation
################################################################################

ANSIBLE_METADATA = {'metadata_version': '1.1', 'status': ["preview"], 'supported_by': 'community'}

DOCUMENTATION = '''
---
module: gcp_compute_forwarding_rule_info
description:
- Gather info for GCP ForwardingRule
short_description: Gather info for GCP ForwardingRule
author: Google Inc. (@googlecloudplatform)
requirements:
- python >= 2.6
- requests >= 2.18.4
- google-auth >= 1.3.0
options:
  filters:
    description:
    - A list of filter value pairs. Available filters are listed here U(https://cloud.google.com/sdk/gcloud/reference/topic/filters).
    - Each additional filter in the list will act be added as an AND condition (filter1
      and filter2) .
    type: list
    elements: str
  region:
    description:
    - A reference to the region where the regional forwarding rule resides.
    - This field is not applicable to global forwarding rules.
    required: true
    type: str
  project:
    description:
    - The Google Cloud Platform project to use.
    type: str
  auth_kind:
    description:
    - The type of credential used.
    type: str
    required: true
    choices:
    - application
    - machineaccount
    - serviceaccount
  service_account_contents:
    description:
    - The contents of a Service Account JSON file, either in a dictionary or as a
      JSON string that represents it.
    type: jsonarg
  service_account_file:
    description:
    - The path of a Service Account JSON file if serviceaccount is selected as type.
    type: path
  service_account_email:
    description:
    - An optional service account email address if machineaccount is selected and
      the user does not wish to use the default email.
    type: str
  scopes:
    description:
    - Array of scopes to be used
    type: list
    elements: str
  env_type:
    description:
    - Specifies which Ansible environment you're running this module within.
    - This should not be set unless you know what you're doing.
    - This only alters the User Agent string for any API requests.
    type: str
notes:
- for authentication, you can set service_account_file using the C(gcp_service_account_file)
  env variable.
- for authentication, you can set service_account_contents using the C(GCP_SERVICE_ACCOUNT_CONTENTS)
  env variable.
- For authentication, you can set service_account_email using the C(GCP_SERVICE_ACCOUNT_EMAIL)
  env variable.
- For authentication, you can set auth_kind using the C(GCP_AUTH_KIND) env variable.
- For authentication, you can set scopes using the C(GCP_SCOPES) env variable.
- Environment variables values will only be used if the playbook values are not set.
- The I(service_account_email) and I(service_account_file) options are mutually exclusive.
'''

EXAMPLES = '''
- name: get info on a forwarding rule
  gcp_compute_forwarding_rule_info:
    region: us-west1
    filters:
    - name = test_object
    project: test_project
    auth_kind: serviceaccount
    service_account_file: "/tmp/auth.pem"
'''

RETURN = '''
resources:
  description: List of resources
  returned: always
  type: complex
  contains:
    creationTimestamp:
      description:
      - Creation timestamp in RFC3339 text format.
      returned: success
      type: str
    isMirroringCollector:
      description:
      - Indicates whether or not this load balancer can be used as a collector for
        packet mirroring. To prevent mirroring loops, instances behind this load balancer
        will not have their traffic mirrored even if a PacketMirroring rule applies
        to them. This can only be set to true for load balancers that have their loadBalancingScheme
        set to INTERNAL.
      returned: success
      type: bool
    description:
      description:
      - An optional description of this resource. Provide this property when you create
        the resource.
      returned: success
      type: str
    id:
      description:
      - The unique identifier for the resource.
      returned: success
      type: int
    IPAddress:
      description:
      - The IP address that this forwarding rule is serving on behalf of.
      - Addresses are restricted based on the forwarding rule's load balancing scheme
        (EXTERNAL or INTERNAL) and scope (global or regional).
      - When the load balancing scheme is EXTERNAL, for global forwarding rules, the
        address must be a global IP, and for regional forwarding rules, the address
        must live in the same region as the forwarding rule. If this field is empty,
        an ephemeral IPv4 address from the same scope (global or regional) will be
        assigned. A regional forwarding rule supports IPv4 only. A global forwarding
        rule supports either IPv4 or IPv6.
      - When the load balancing scheme is INTERNAL, this can only be an RFC 1918 IP
        address belonging to the network/subnet configured for the forwarding rule.
        By default, if this field is empty, an ephemeral internal IP address will
        be automatically allocated from the IP range of the subnet or network configured
        for this forwarding rule.
      - 'An address can be specified either by a literal IP address or a URL reference
        to an existing Address resource. The following examples are all valid: * 100.1.2.3
        * U(https://www.googleapis.com/compute/v1/projects/project/regions/region/addresses/address)
        * projects/project/regions/region/addresses/address * regions/region/addresses/address
        * global/addresses/address * address .'
      returned: success
      type: str
    IPProtocol:
      description:
      - The IP protocol to which this rule applies.
      - When the load balancing scheme is INTERNAL, only TCP and UDP are valid.
      returned: success
      type: str
    backendService:
      description:
      - A BackendService to receive the matched traffic. This is used only for INTERNAL
        load balancing.
      returned: success
      type: dict
    loadBalancingScheme:
      description:
      - This signifies what the ForwardingRule will be used for and can be EXTERNAL,
        INTERNAL, or INTERNAL_MANAGED. EXTERNAL is used for Classic Cloud VPN gateways,
        protocol forwarding to VMs from an external IP address, and HTTP(S), SSL Proxy,
        TCP Proxy, and Network TCP/UDP load balancers.
      - INTERNAL is used for protocol forwarding to VMs from an internal IP address,
        and internal TCP/UDP load balancers.
      - INTERNAL_MANAGED is used for internal HTTP(S) load balancers.
      returned: success
      type: str
    name:
      description:
      - Name of the resource; provided by the client when the resource is created.
        The name must be 1-63 characters long, and comply with RFC1035. Specifically,
        the name must be 1-63 characters long and match the regular expression `[a-z]([-a-z0-9]*[a-z0-9])?`
        which means the first character must be a lowercase letter, and all following
        characters must be a dash, lowercase letter, or digit, except the last character,
        which cannot be a dash.
      returned: success
      type: str
    network:
      description:
      - For internal load balancing, this field identifies the network that the load
        balanced IP should belong to for this Forwarding Rule. If this field is not
        specified, the default network will be used.
      - This field is only used for INTERNAL load balancing.
      returned: success
      type: dict
    portRange:
      description:
      - This field is used along with the target field for TargetHttpProxy, TargetHttpsProxy,
        TargetSslProxy, TargetTcpProxy, TargetVpnGateway, TargetPool, TargetInstance.
      - Applicable only when IPProtocol is TCP, UDP, or SCTP, only packets addressed
        to ports in the specified range will be forwarded to target.
      - Forwarding rules with the same [IPAddress, IPProtocol] pair must have disjoint
        port ranges.
      - 'Some types of forwarding target have constraints on the acceptable ports:
        * TargetHttpProxy: 80, 8080 * TargetHttpsProxy: 443 * TargetTcpProxy: 25,
        43, 110, 143, 195, 443, 465, 587, 700, 993, 995, 1883, 5222 * TargetSslProxy:
        25, 43, 110, 143, 195, 443, 465, 587, 700, 993, 995, 1883, 5222 * TargetVpnGateway:
        500, 4500 .'
      returned: success
      type: str
    ports:
      description:
      - This field is used along with the backend_service field for internal load
        balancing.
      - When the load balancing scheme is INTERNAL, a single port or a comma separated
        list of ports can be configured. Only packets addressed to these ports will
        be forwarded to the backends configured with this forwarding rule.
      - You may specify a maximum of up to 5 ports.
      returned: success
      type: list
    subnetwork:
      description:
      - The subnetwork that the load balanced IP should belong to for this Forwarding
        Rule. This field is only used for INTERNAL load balancing.
      - If the network specified is in auto subnet mode, this field is optional. However,
        if the network is in custom subnet mode, a subnetwork must be specified.
      returned: success
      type: dict
    target:
      description:
      - The URL of the target resource to receive the matched traffic.
      - The target must live in the same region as the forwarding rule.
      - The forwarded traffic must be of a type appropriate to the target object.
      returned: success
      type: str
    allowGlobalAccess:
      description:
      - If true, clients can access ILB from all regions.
      - Otherwise only allows from the local region the ILB is located at.
      returned: success
      type: bool
    allPorts:
      description:
      - For internal TCP/UDP load balancing (i.e. load balancing scheme is INTERNAL
        and protocol is TCP/UDP), set this to true to allow packets addressed to any
        ports to be forwarded to the backends configured with this forwarding rule.
        Used with backend service. Cannot be set if port or portRange are set.
      returned: success
      type: bool
    networkTier:
      description:
      - The networking tier used for configuring this address. If this field is not
        specified, it is assumed to be PREMIUM.
      returned: success
      type: str
    serviceLabel:
      description:
      - An optional prefix to the service name for this Forwarding Rule.
      - If specified, will be the first label of the fully qualified service name.
      - The label must be 1-63 characters long, and comply with RFC1035.
      - Specifically, the label must be 1-63 characters long and match the regular
        expression `[a-z]([-a-z0-9]*[a-z0-9])?` which means the first character must
        be a lowercase letter, and all following characters must be a dash, lowercase
        letter, or digit, except the last character, which cannot be a dash.
      - This field is only used for INTERNAL load balancing.
      returned: success
      type: str
    serviceName:
      description:
      - The internal fully qualified service name for this Forwarding Rule.
      - This field is only used for INTERNAL load balancing.
      returned: success
      type: str
    region:
      description:
      - A reference to the region where the regional forwarding rule resides.
      - This field is not applicable to global forwarding rules.
      returned: success
      type: str
'''

################################################################################
# Imports
################################################################################
from ansible_collections.google.cloud.plugins.module_utils.gcp_utils import navigate_hash, GcpSession, GcpModule, GcpRequest
import json

################################################################################
# Main
################################################################################


def main():
    module = GcpModule(argument_spec=dict(filters=dict(type='list', elements='str'), region=dict(required=True, type='str')))

    if not module.params['scopes']:
        module.params['scopes'] = ['https://www.googleapis.com/auth/compute']

    return_value = {'resources': fetch_list(module, collection(module), query_options(module.params['filters']))}
    module.exit_json(**return_value)


def collection(module):
    return "https://compute.googleapis.com/compute/v1/projects/{project}/regions/{region}/forwardingRules".format(**module.params)


def fetch_list(module, link, query):
    auth = GcpSession(module, 'compute')
    return auth.list(link, return_if_object, array_name='items', params={'filter': query})


def query_options(filters):
    if not filters:
        return ''

    if len(filters) == 1:
        return filters[0]
    else:
        queries = []
        for f in filters:
            # For multiple queries, all queries should have ()
            if f[0] != '(' and f[-1] != ')':
                queries.append("(%s)" % ''.join(f))
            else:
                queries.append(f)

        return ' '.join(queries)


def return_if_object(module, response):
    # If not found, return nothing.
    if response.status_code == 404:
        return None

    # If no content, return nothing.
    if response.status_code == 204:
        return None

    try:
        module.raise_for_status(response)
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, ['error', 'errors']):
        module.fail_json(msg=navigate_hash(result, ['error', 'errors']))

    return result


if __name__ == "__main__":
    main()
