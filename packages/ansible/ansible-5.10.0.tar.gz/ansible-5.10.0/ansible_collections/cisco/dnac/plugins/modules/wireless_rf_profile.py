#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2021, Cisco Systems
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: wireless_rf_profile
short_description: Resource module for Wireless Rf Profile
description:
- Manage operations create and delete of the resource Wireless Rf Profile.
- Create or Update RF profile.
- Delete RF profiles.
version_added: '3.1.0'
extends_documentation_fragment:
  - cisco.dnac.module
author: Rafael Campos (@racampos)
options:
  channelWidth:
    description: Channel Width.
    type: str
  defaultRfProfile:
    description: Is Default Rf Profile.
    type: bool
  enableBrownField:
    description: Enable Brown Field.
    type: bool
  enableCustom:
    description: Enable Custom.
    type: bool
  enableRadioTypeA:
    description: Enable Radio Type A.
    type: bool
  enableRadioTypeB:
    description: Enable Radio Type B.
    type: bool
  enableRadioTypeC:
    description: Enable Radio Type C (6GHz).
    type: bool
  name:
    description: RF Profile Name.
    type: str
  radioTypeAProperties:
    description: Wireless Rf Profile's radioTypeAProperties.
    suboptions:
      dataRates:
        description: Data Rates.
        type: str
      mandatoryDataRates:
        description: Mandatory Data Rates.
        type: str
      maxPowerLevel:
        description: Max Power Level.
        type: int
      minPowerLevel:
        description: Rx Sop Threshold.
        type: int
      parentProfile:
        description: Parent Profile.
        type: str
      powerThresholdV1:
        description: Power Threshold V1.
        type: int
      radioChannels:
        description: Radio Channels.
        type: str
      rxSopThreshold:
        description: Rx Sop Threshold.
        type: str
    type: dict
  radioTypeBProperties:
    description: Wireless Rf Profile's radioTypeBProperties.
    suboptions:
      dataRates:
        description: Data Rates.
        type: str
      mandatoryDataRates:
        description: Mandatory Data Rates.
        type: str
      maxPowerLevel:
        description: Max Power Level.
        type: int
      minPowerLevel:
        description: Min Power Level.
        type: int
      parentProfile:
        description: Parent Profile.
        type: str
      powerThresholdV1:
        description: Power Threshold V1.
        type: int
      radioChannels:
        description: Radio Channels.
        type: str
      rxSopThreshold:
        description: Rx Sop Threshold.
        type: str
    type: dict
  radioTypeCProperties:
    description: Wireless Rf Profile's radioTypeCProperties.
    suboptions:
      dataRates:
        description: Data Rates.
        type: str
      mandatoryDataRates:
        description: Mandatory Data Rates.
        type: str
      maxPowerLevel:
        description: Max Power Level.
        type: int
      minPowerLevel:
        description: Min Power Level.
        type: int
      parentProfile:
        description: Parent Profile.
        type: str
      powerThresholdV1:
        description: Power Threshold V1.
        type: int
      radioChannels:
        description: Radio Channels.
        type: str
      rxSopThreshold:
        description: Rx Sop Threshold.
        type: str
    type: dict
  rfProfileName:
    description: RfProfileName path parameter. RF profile name to be deleted(required)
      *non-custom RF profile cannot be deleted.
    type: str
requirements:
- dnacentersdk >= 2.5.0
- python >= 3.5
seealso:
- name: Cisco DNA Center documentation for Wireless CreateOrUpdateRFProfile
  description: Complete reference of the CreateOrUpdateRFProfile API.
  link: https://developer.cisco.com/docs/dna-center/#!create-or-update-rf-profile
- name: Cisco DNA Center documentation for Wireless DeleteRFProfiles
  description: Complete reference of the DeleteRFProfiles API.
  link: https://developer.cisco.com/docs/dna-center/#!delete-rf-profiles
notes:
  - SDK Method used are
    wireless.Wireless.create_or_update_rf_profile,
    wireless.Wireless.delete_rf_profiles,

  - Paths used are
    post /dna/intent/api/v1/wireless/rf-profile,
    delete /dna/intent/api/v1/wireless/rf-profile/{rfProfileName},

"""

EXAMPLES = r"""
- name: Create
  cisco.dnac.wireless_rf_profile:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    state: present
    channelWidth: string
    defaultRfProfile: true
    enableBrownField: true
    enableCustom: true
    enableRadioTypeA: true
    enableRadioTypeB: true
    enableRadioTypeC: true
    name: string
    radioTypeAProperties:
      dataRates: string
      mandatoryDataRates: string
      maxPowerLevel: 0
      minPowerLevel: 0
      parentProfile: string
      powerThresholdV1: 0
      radioChannels: string
      rxSopThreshold: string
    radioTypeBProperties:
      dataRates: string
      mandatoryDataRates: string
      maxPowerLevel: 0
      minPowerLevel: 0
      parentProfile: string
      powerThresholdV1: 0
      radioChannels: string
      rxSopThreshold: string
    radioTypeCProperties:
      dataRates: string
      mandatoryDataRates: string
      maxPowerLevel: 0
      minPowerLevel: 0
      parentProfile: string
      powerThresholdV1: 0
      radioChannels: string
      rxSopThreshold: string

- name: Delete by name
  cisco.dnac.wireless_rf_profile:
    dnac_host: "{{dnac_host}}"
    dnac_username: "{{dnac_username}}"
    dnac_password: "{{dnac_password}}"
    dnac_verify: "{{dnac_verify}}"
    dnac_port: "{{dnac_port}}"
    dnac_version: "{{dnac_version}}"
    dnac_debug: "{{dnac_debug}}"
    state: absent
    rfProfileName: string

"""

RETURN = r"""
dnac_response:
  description: A dictionary or list with the response returned by the Cisco DNAC Python SDK
  returned: always
  type: dict
  sample: >
    {
      "executionId": "string",
      "executionUrl": "string",
      "message": "string"
    }
"""
