#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: ovirt_vm
short_description: Module to manage Virtual Machines in oVirt/RHV
version_added: "1.0.0"
author:
- "Ondra Machacek (@machacekondra)"
- "Martin Necas (@mnecas)"
description:
    - This module manages whole lifecycle of the Virtual Machine(VM) in oVirt/RHV.
    - Since VM can hold many states in oVirt/RHV, this see notes to see how the states of the VM are handled.
options:
    name:
        description:
            - Name of the Virtual Machine to manage.
            - If VM don't exists C(name) is required. Otherwise C(id) or C(name) can be used.
        type: str
    id:
        description:
            - ID of the Virtual Machine to manage.
        type: str
    state:
        description:
            - Should the Virtual Machine be running/stopped/present/absent/suspended/next_run/registered/exported/reboot.
              When C(state) is I(registered) and the unregistered VM's name
              belongs to an already registered in engine VM in the same DC
              then we fail to register the unregistered template.
            - I(present) state will create/update VM and don't change its state if it already exists.
            - I(running) state will create/update VM and start it.
            - I(next_run) state updates the VM and if the VM has next run configuration it will be rebooted.
            - Please check I(notes) to more detailed description of states.
            - I(exported) state will export the VM to export domain or as OVA.
            - I(registered) is supported since 2.4.
            - I(reboot) is supported since 2.10, virtual machine is rebooted only if it's in up state.
        choices: [ absent, next_run, present, registered, running, stopped, suspended, exported, reboot ]
        default: present
        type: str
    cluster:
        description:
            - Name of the cluster, where Virtual Machine should be created.
            - Required if creating VM.
        type: str
    allow_partial_import:
        description:
            - Boolean indication whether to allow partial registration of Virtual Machine when C(state) is registered.
        type: bool
    vnic_profile_mappings:
        description:
            - "Mapper which maps an external virtual NIC profile to one that exists in the engine when C(state) is registered.
               vnic_profile is described by the following dictionary:"
        type: list
        elements: dict
        suboptions:
            source_network_name:
                description:
                    - The network name of the source network.
            source_profile_name:
                description:
                    - The profile name related to the source network.
            target_profile_id:
                description:
                    - The id of the target profile id to be mapped to in the engine.
    cluster_mappings:
        description:
            - "Mapper which maps cluster name between VM's OVF and the destination cluster this VM should be registered to,
               relevant when C(state) is registered.
               Cluster mapping is described by the following dictionary:"
        type: list
        elements: dict
        suboptions:
            source_name:
                description:
                    - The name of the source cluster.
            dest_name:
                description:
                    - The name of the destination cluster.
    role_mappings:
        description:
            - "Mapper which maps role name between VM's OVF and the destination role this VM should be registered to,
               relevant when C(state) is registered.
               Role mapping is described by the following dictionary:"
        type: list
        elements: dict
        suboptions:
            source_name:
                description:
                    - The name of the source role.
            dest_name:
                description:
                    - The name of the destination role.
    domain_mappings:
        description:
            - "Mapper which maps aaa domain name between VM's OVF and the destination aaa domain this VM should be registered to,
               relevant when C(state) is registered.
               The aaa domain mapping is described by the following dictionary:"
        type: list
        elements: dict
        suboptions:
            source_name:
                description:
                    - The name of the source aaa domain.
            dest_name:
                description:
                    - The name of the destination aaa domain.
    affinity_group_mappings:
        type: list
        description:
            - "Mapper which maps affinity name between VM's OVF and the destination affinity this VM should be registered to,
               relevant when C(state) is registered."
        elements: dict
    affinity_label_mappings:
        type: list
        description:
            - "Mapper which maps affinity label name between VM's OVF and the destination label this VM should be registered to,
               relevant when C(state) is registered."
        elements: dict
    lun_mappings:
        description:
            - "Mapper which maps lun between VM's OVF and the destination lun this VM should contain, relevant when C(state) is registered.
               lun_mappings is described by the following dictionary:"
        type: list
        elements: dict
        suboptions:
            logical_unit_id:
                description:
                    - The logical unit number to identify a logical unit,
            logical_unit_port:
                description:
                    - The port being used to connect with the LUN disk.
            logical_unit_portal:
                description:
                    - The portal being used to connect with the LUN disk.
            logical_unit_address:
                description:
                    - The address of the block storage host.
            logical_unit_target:
                description:
                    - The iSCSI specification located on an iSCSI server
            logical_unit_username:
                description:
                    - Username to be used to connect to the block storage host.
            logical_unit_password):
                description:
                    - Password to be used to connect to the block storage host.
            storage_type:
                description:
                    - The storage type which the LUN reside on (iscsi or fcp)"
    reassign_bad_macs:
        description:
            - "Boolean indication whether to reassign bad macs when C(state) is registered."
        type: bool
    template:
        description:
            - Name of the template, which should be used to create Virtual Machine.
            - Required if creating VM.
            - If template is not specified and VM doesn't exist, VM will be created from I(Blank) template.
        type: str
    template_version:
        description:
            - Version number of the template to be used for VM.
            - By default the latest available version of the template is used.
        type: int
    use_latest_template_version:
        description:
            - Specify if latest template version should be used, when running a stateless VM.
            - If this parameter is set to I(yes) stateless VM is created.
        type: bool
    storage_domain:
        description:
            - Name of the storage domain where all template disks should be created.
            - This parameter is considered only when C(template) is provided.
            - IMPORTANT - This parameter is not idempotent, if the VM exists and you specify different storage domain,
              disk won't move.
        type: str
    disk_format:
        description:
            - Specify format of the disk.
            - If C(cow) format is used, disk will by created as sparse, so space will be allocated for the volume as needed, also known as I(thin provision).
            - If C(raw) format is used, disk storage will be allocated right away, also known as I(preallocated).
            - Note that this option isn't idempotent as it's not currently possible to change format of the disk via API.
            - This parameter is considered only when C(template) and C(storage domain) is provided.
        choices: [ cow, raw ]
        default: cow
        type: str
    memory:
        description:
            - Amount of memory of the Virtual Machine. Prefix uses IEC 60027-2 standard (for example 1GiB, 1024MiB).
            - Default value is set by engine.
        type: str
    memory_guaranteed:
        description:
            - Amount of minimal guaranteed memory of the Virtual Machine.
              Prefix uses IEC 60027-2 standard (for example 1GiB, 1024MiB).
            - C(memory_guaranteed) parameter can't be lower than C(memory) parameter.
            - Default value is set by engine.
        type: str
    memory_max:
        description:
            - Upper bound of virtual machine memory up to which memory hot-plug can be performed.
              Prefix uses IEC 60027-2 standard (for example 1GiB, 1024MiB).
            - Default value is set by engine.
        type: str
    cpu_shares:
        description:
            - Set a CPU shares for this Virtual Machine.
            - Default value is set by oVirt/RHV engine.
        type: int
    cpu_cores:
        description:
            - Number of virtual CPUs cores of the Virtual Machine.
            - Default value is set by oVirt/RHV engine.
        type: int
    cpu_sockets:
        description:
            - Number of virtual CPUs sockets of the Virtual Machine.
            - Default value is set by oVirt/RHV engine.
        type: int
    cpu_threads:
        description:
            - Number of threads per core of the Virtual Machine.
            - Default value is set by oVirt/RHV engine.
        type: int
    type:
        description:
            - Type of the Virtual Machine.
            - Default value is set by oVirt/RHV engine.
            - I(high_performance) is supported since Ansible 2.5 and oVirt/RHV 4.2.
        choices: [ desktop, server, high_performance ]
        type: str
    quota_id:
        description:
            - "Virtual Machine quota ID to be used for disk. By default quota is chosen by oVirt/RHV engine."
        type: str
    operating_system:
        description:
            - Operating system of the Virtual Machine, for example 'rhel_8x64'.
            - Default value is set by oVirt/RHV engine.
            - Use the M(ovirt.ovirt.ovirt_vm_os_info) module to obtain the current list.
        type: str
    boot_devices:
        description:
            - List of boot devices which should be used to boot. For example C([ cdrom, hd ]).
            - Default value is set by oVirt/RHV engine.
        choices: [ cdrom, hd, network ]
        elements: str
        type: list
    boot_menu:
        description:
            - "I(True) enable menu to select boot device, I(False) to disable it. By default is chosen by oVirt/RHV engine."
        type: bool
    bios_type:
        description:
            - "Set bios type, necessary for some operating systems and secure boot."
            - "If no value is passed, default value is set from cluster."
            - "NOTE - Supported since oVirt 4.3."
        choices: [ i440fx_sea_bios, q35_ovmf, q35_sea_bios, q35_secure_boot ]
        type: str
    usb_support:
        description:
            - "I(True) enable USB support, I(False) to disable it. By default is chosen by oVirt/RHV engine."
        type: bool
    serial_console:
        description:
            - "I(True) enable VirtIO serial console, I(False) to disable it. By default is chosen by oVirt/RHV engine."
        type: bool
    sso:
        description:
            - "I(True) enable Single Sign On by Guest Agent, I(False) to disable it. By default is chosen by oVirt/RHV engine."
        type: bool
    host:
        description:
            - Specify host where Virtual Machine should be running. By default the host is chosen by engine scheduler.
            - This parameter is used only when C(state) is I(running) or I(present).
        type: str
    high_availability:
        description:
            - If I(yes) Virtual Machine will be set as highly available.
            - If I(no) Virtual Machine won't be set as highly available.
            - If no value is passed, default value is set by oVirt/RHV engine.
        type: bool
    high_availability_priority:
        description:
            - Indicates the priority of the virtual machine inside the run and migration queues.
              Virtual machines with higher priorities will be started and migrated before virtual machines with lower
              priorities. The value is an integer between 0 and 100. The higher the value, the higher the priority.
            - If no value is passed, default value is set by oVirt/RHV engine.
        type: int
    lease:
        description:
            - Name of the storage domain this virtual machine lease reside on. Pass an empty string to remove the lease.
            - NOTE - Supported since oVirt 4.1.
        type: str
    custom_compatibility_version:
        description:
            - "Enables a virtual machine to be customized to its own compatibility version. If
            'C(custom_compatibility_version)' is set, it overrides the cluster's compatibility version
            for this particular virtual machine."
        type: str
    host_devices:
        description:
            - Single Root I/O Virtualization - technology that allows single device to expose multiple endpoints that can be passed to VMs
            - host_devices is an list which contain dictionary with name and state of device
        type: list
        elements: dict
    delete_protected:
        description:
            - If I(yes) Virtual Machine will be set as delete protected.
            - If I(no) Virtual Machine won't be set as delete protected.
            - If no value is passed, default value is set by oVirt/RHV engine.
        type: bool
    stateless:
        description:
            - If I(yes) Virtual Machine will be set as stateless.
            - If I(no) Virtual Machine will be unset as stateless.
            - If no value is passed, default value is set by oVirt/RHV engine.
        type: bool
    clone:
        description:
            - If I(yes) then the disks of the created virtual machine will be cloned and independent of the template.
            - This parameter is used only when C(state) is I(running) or I(present) and VM didn't exist before.
        type: bool
        default: 'no'
    clone_permissions:
        description:
            - If I(yes) then the permissions of the template (only the direct ones, not the inherited ones)
              will be copied to the created virtual machine.
            - This parameter is used only when C(state) is I(running) or I(present) and VM didn't exist before.
        type: bool
        default: 'no'
    cd_iso:
        description:
            - ISO file from ISO storage domain which should be attached to Virtual Machine.
            - If you have multiple ISO disks with the same name use disk ID to specify which should be used or use C(storage_domain) to filter disks.
            - If you pass empty string the CD will be ejected from VM.
            - If used with C(state) I(running) or I(present) and VM is running the CD will be attached to VM.
            - If used with C(state) I(running) or I(present) and VM is down the CD will be attached to VM persistently.
        type: str
    force:
        description:
            - Please check to I(Synopsis) to more detailed description of force parameter, it can behave differently
              in different situations.
        type: bool
        default: 'no'
    nics:
        description:
            - List of NICs, which should be attached to Virtual Machine. NIC is described by following dictionary.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                    - Name of the NIC.
            profile_name:
                description:
                    - Profile name where NIC should be attached.
            interface:
                description:
                    - Type of the network interface.
                choices: ['virtio', 'e1000', 'rtl8139']
                default: 'virtio'
            mac_address:
                description:
                    - Custom MAC address of the network interface, by default it's obtained from MAC pool.
                    - "NOTE - This parameter is used only when C(state) is I(running) or I(present) and is able to only create NICs.
                    To manage NICs of the VM in more depth please use M(ovirt.ovirt.ovirt_nic) module instead."
    disks:
        description:
            - List of disks, which should be attached to Virtual Machine. Disk is described by following dictionary.
        type: list
        elements: dict
        suboptions:
            name:
                description:
                    - Name of the disk. Either C(name) or C(id) is required.
            id:
                description:
                    - ID of the disk. Either C(name) or C(id) is required.
            interface:
                description:
                    - Interface of the disk.
                choices: ['virtio', 'ide']
                default: 'virtio'
            bootable:
                description:
                    - I(True) if the disk should be bootable, default is non bootable.
                type: bool
            activate:
                description:
                    - I(True) if the disk should be activated, default is activated.
                    - "NOTE - This parameter is used only when C(state) is I(running) or I(present) and is able to only attach disks.
                    To manage disks of the VM in more depth please use M(ovirt.ovirt.ovirt_disk) module instead."
                type: bool
    sysprep:
        description:
            - Dictionary with values for Windows Virtual Machine initialization using sysprep.
        type: dict
        suboptions:
            host_name:
                description:
                    - Hostname to be set to Virtual Machine when deployed.
            active_directory_ou:
                description:
                    - Active Directory Organizational Unit, to be used for login of user.
            org_name:
                description:
                    - Organization name to be set to Windows Virtual Machine.
            domain:
                description:
                    - Domain to be set to Windows Virtual Machine.
            timezone:
                description:
                    - Timezone to be set to Windows Virtual Machine.
            ui_language:
                description:
                    - UI language of the Windows Virtual Machine.
            system_locale:
                description:
                    - System localization of the Windows Virtual Machine.
            input_locale:
                description:
                    - Input localization of the Windows Virtual Machine.
            windows_license_key:
                description:
                    - License key to be set to Windows Virtual Machine.
            user_name:
                description:
                    - Username to be used for set password to Windows Virtual Machine.
            root_password:
                description:
                    - Password to be set for username to Windows Virtual Machine.
            custom_script:
                description:
                    - A custom Sysprep definition in the format of a complete unattended installation answer file.
    cloud_init:
        description:
            - Dictionary with values for Unix-like Virtual Machine initialization using cloud init.
        type: dict
        suboptions:
            host_name:
                description:
                    - Hostname to be set to Virtual Machine when deployed.
            timezone:
                description:
                    - Timezone to be set to Virtual Machine when deployed.
            user_name:
                description:
                    - Username to be used to set password to Virtual Machine when deployed.
            root_password:
                description:
                    - Password to be set for user specified by C(user_name) parameter.
            authorized_ssh_keys:
                description:
                    - Use this SSH keys to login to Virtual Machine.
            regenerate_ssh_keys:
                description:
                    - If I(True) SSH keys will be regenerated on Virtual Machine.
                type: bool
            custom_script:
                description:
                    - Cloud-init script which will be executed on Virtual Machine when deployed.
                    - This is appended to the end of the cloud-init script generated by any other options.
                    - For further information, refer to cloud-init User-Data documentation.
            dns_servers:
                description:
                    - DNS servers to be configured on Virtual Machine, maximum of two, space-separated.
            dns_search:
                description:
                    - DNS search domains to be configured on Virtual Machine.
            nic_boot_protocol:
                description:
                    - Set boot protocol of the network interface of Virtual Machine.
                choices: ['none', 'dhcp', 'static']
            nic_ip_address:
                description:
                    - If boot protocol is static, set this IP address to network interface of Virtual Machine.
            nic_netmask:
                description:
                    - If boot protocol is static, set this netmask to network interface of Virtual Machine.
            nic_gateway:
                description:
                    - If boot protocol is static, set this gateway to network interface of Virtual Machine.
            nic_boot_protocol_v6:
                description:
                    - Set boot protocol of the network interface of Virtual Machine.
                choices: ['none', 'dhcp', 'static']
            nic_ip_address_v6:
                description:
                    - If boot protocol is static, set this IP address to network interface of Virtual Machine.
            nic_netmask_v6:
                description:
                    - If boot protocol is static, set this netmask to network interface of Virtual Machine.
            nic_gateway_v6:
                description:
                    - If boot protocol is static, set this gateway to network interface of Virtual Machine.
                    - For IPv6 addresses the value is an integer in the range of 0-128, which represents the subnet prefix.
            nic_name:
                description:
                    - Set name to network interface of Virtual Machine.
    cloud_init_nics:
        description:
            - List of dictionaries representing network interfaces to be setup by cloud init.
            - This option is used, when user needs to setup more network interfaces via cloud init.
            - If one network interface is enough, user should use C(cloud_init) I(nic_*) parameters. C(cloud_init) I(nic_*) parameters
              are merged with C(cloud_init_nics) parameters.
        type: list
        elements: dict
        suboptions:
            nic_boot_protocol:
                description:
                    - Set boot protocol of the network interface of Virtual Machine. Can be one of C(none), C(dhcp) or C(static).
            nic_ip_address:
                description:
                    - If boot protocol is static, set this IP address to network interface of Virtual Machine.
            nic_netmask:
                description:
                    - If boot protocol is static, set this netmask to network interface of Virtual Machine.
            nic_gateway:
                description:
                    - If boot protocol is static, set this gateway to network interface of Virtual Machine.
            nic_boot_protocol_v6:
                description:
                    - Set boot protocol of the network interface of Virtual Machine. Can be one of C(none), C(dhcp) or C(static).
            nic_ip_address_v6:
                description:
                    - If boot protocol is static, set this IP address to network interface of Virtual Machine.
            nic_netmask_v6:
                description:
                    - If boot protocol is static, set this netmask to network interface of Virtual Machine.
            nic_gateway_v6:
                description:
                    - If boot protocol is static, set this gateway to network interface of Virtual Machine.
                    - For IPv6 addresses the value is an integer in the range of 0-128, which represents the subnet prefix.
            nic_name:
                description:
                    - Set name to network interface of Virtual Machine.
    cloud_init_persist:
        description:
            - "If I(yes) the C(cloud_init) or C(sysprep) parameters will be saved for the virtual machine
               and the virtual machine won't be started as run-once."
        type: bool
        aliases: [ 'sysprep_persist' ]
        default: 'no'
    kernel_params_persist:
        description:
            - "If I(true) C(kernel_params), C(initrd_path) and C(kernel_path) will persist in virtual machine configuration,
               if I(False) it will be used for run once."
        type: bool
        default: false
    kernel_path:
        description:
            - Path to a kernel image used to boot the virtual machine.
            - Kernel image must be stored on either the ISO domain or on the host's storage.
        type: str
    initrd_path:
        description:
            - Path to an initial ramdisk to be used with the kernel specified by C(kernel_path) option.
            - Ramdisk image must be stored on either the ISO domain or on the host's storage.
        type: str
    kernel_params:
        description:
            - Kernel command line parameters (formatted as string) to be used with the kernel specified by C(kernel_path) option.
        type: str
    instance_type:
        description:
            - Name of virtual machine's hardware configuration.
            - By default no instance type is used.
        type: str
    description:
        description:
            - Description of the Virtual Machine.
        type: str
    comment:
        description:
            - Comment of the Virtual Machine.
        type: str
    timezone:
        description:
            - Sets time zone offset of the guest hardware clock.
            - For example C(Etc/GMT)
        type: str
    serial_policy:
        description:
            - Specify a serial number policy for the Virtual Machine.
            - Following options are supported.
            - C(vm) - Sets the Virtual Machine's UUID as its serial number.
            - C(host) - Sets the host's UUID as the Virtual Machine's serial number.
            - C(custom) - Allows you to specify a custom serial number in C(serial_policy_value).
        choices: ['vm', 'host', 'custom']
        type: str
    serial_policy_value:
        description:
            - Allows you to specify a custom serial number.
            - This parameter is used only when C(serial_policy) is I(custom).
        type: str
    vmware:
        description:
            - Dictionary of values to be used to connect to VMware and import
              a virtual machine to oVirt.
        type: dict
        suboptions:
            username:
                description:
                    - The username to authenticate against the VMware.
            password:
                description:
                    - The password to authenticate against the VMware.
            url:
                description:
                    - The URL to be passed to the I(virt-v2v) tool for conversion.
                    - For example I(vpx://wmware_user@vcenter-host/DataCenter/Cluster/esxi-host?no_verify=1)
            drivers_iso:
                description:
                    - The name of the ISO containing drivers that can be used during the I(virt-v2v) conversion process.
            sparse:
                description:
                    - Specifies the disk allocation policy of the resulting virtual machine. I(true) for sparse, I(false) for preallocated.
                type: bool
                default: true
            storage_domain:
                description:
                    - Specifies the target storage domain for converted disks. This is required parameter.
    xen:
        description:
            - Dictionary of values to be used to connect to XEN and import
              a virtual machine to oVirt.
        type: dict
        suboptions:
            url:
                description:
                    - The URL to be passed to the I(virt-v2v) tool for conversion.
                    - For example I(xen+ssh://root@zen.server). This is required parameter.
            drivers_iso:
                description:
                    - The name of the ISO containing drivers that can be used during the I(virt-v2v) conversion process.
            sparse:
                description:
                    - Specifies the disk allocation policy of the resulting virtual machine. I(true) for sparse, I(false) for preallocated.
                type: bool
                default: true
            storage_domain:
                description:
                    - Specifies the target storage domain for converted disks. This is required parameter.
    kvm:
        description:
            - Dictionary of values to be used to connect to kvm and import
              a virtual machine to oVirt.
        type: dict
        suboptions:
            name:
                description:
                    - The name of the KVM virtual machine.
            username:
                description:
                    - The username to authenticate against the KVM.
            password:
                description:
                    - The password to authenticate against the KVM.
            url:
                description:
                    - The URL to be passed to the I(virt-v2v) tool for conversion.
                    - For example I(qemu:///system). This is required parameter.
            drivers_iso:
                description:
                    - The name of the ISO containing drivers that can be used during the I(virt-v2v) conversion process.
            sparse:
                description:
                    - Specifies the disk allocation policy of the resulting virtual machine. I(true) for sparse, I(false) for preallocated.
                type: bool
                default: true
            storage_domain:
                description:
                    - Specifies the target storage domain for converted disks. This is required parameter.
    cpu_mode:
        description:
            - "CPU mode of the virtual machine. It can be some of the following: I(host_passthrough), I(host_model) or I(custom)."
            - "For I(host_passthrough) CPU type you need to set C(placement_policy) to I(pinned)."
            - "If no value is passed, default value is set by oVirt/RHV engine."
        type: str
    placement_policy:
        description:
            - "The configuration of the virtual machine's placement policy."
            - "If no value is passed, default value is set by oVirt/RHV engine."
            - "Placement policy can be one of the following values:"
        type: str
        suboptions:
            migratable:
                description:
                    - "Allow manual and automatic migration."
            pinned:
                description:
                    - "Do not allow migration."
            user_migratable:
                description:
                    - "Allow manual migration only."
    placement_policy_hosts:
        description:
            - "List of host names."
        type: list
        elements: str
    ticket:
        description:
            - "If I(true), in addition return I(remote_vv_file) inside I(vm) dictionary, which contains compatible
                content for remote-viewer application. Works only C(state) is I(running)."
        type: bool
    cpu_pinning:
        description:
            - "CPU Pinning topology to map virtual machine CPU to host CPU."
            - "CPU Pinning topology is a list of dictionary which can have following values:"
        type: list
        elements: dict
        suboptions:
            cpu:
                description:
                    - "Number of the host CPU."
            vcpu:
                description:
                    - "Number of the virtual machine CPU."
    soundcard_enabled:
        description:
            - "If I(true), the sound card is added to the virtual machine."
        type: bool
    smartcard_enabled:
        description:
            - "If I(true), use smart card authentication."
        type: bool
    io_threads:
        description:
            - "Number of IO threads used by virtual machine. I(0) means IO threading disabled."
        type: int
    ballooning_enabled:
        description:
            - "If I(true), use memory ballooning."
            - "Memory balloon is a guest device, which may be used to re-distribute / reclaim the host memory
               based on VM needs in a dynamic way. In this way it's possible to create memory over commitment states."
        type: bool
    numa_tune_mode:
        description:
            - "Set how the memory allocation for NUMA nodes of this VM is applied (relevant if NUMA nodes are set for this VM)."
            - "It can be one of the following: I(interleave), I(preferred) or I(strict)."
            - "If no value is passed, default value is set by oVirt/RHV engine."
        choices: ['interleave', 'preferred', 'strict']
        type: str
    numa_nodes:
        description:
            - "List of vNUMA Nodes to set for this VM and pin them to assigned host's physical NUMA node."
            - "Each vNUMA node is described by following dictionary:"
        type: list
        elements: dict
        suboptions:
            index:
                description:
                    - "The index of this NUMA node."
                required: True
            memory:
                description:
                    - "Memory size of the NUMA node in MiB."
                required: True
            cores:
                description:
                    - "List of VM CPU cores indexes to be included in this NUMA node."
                type: list
                required: True
            numa_node_pins:
                description:
                    - "List of physical NUMA node indexes to pin this virtual NUMA node to."
                type: list
    rng_device:
        description:
            - "Random number generator (RNG). You can choose of one the following devices I(urandom), I(random) or I(hwrng)."
            - "In order to select I(hwrng), you must have it enabled on cluster first."
            - "/dev/urandom is used for cluster version >= 4.1, and /dev/random for cluster version <= 4.0"
        type: str
    custom_properties:
        description:
            - "Properties sent to VDSM to configure various hooks."
            - "Custom properties is a list of dictionary which can have following values:"
        type: list
        elements: dict
        suboptions:
            name:
                description:
                    - "Name of the custom property. For example: I(hugepages), I(vhost), I(sap_agent), etc."
            regexp:
                description:
                    - "Regular expression to set for custom property."
            value:
                description:
                    - "Value to set for custom property."
    watchdog:
        description:
            - "Assign watchdog device for the virtual machine."
            - "Watchdogs is a dictionary which can have following values:"
        type: dict
        suboptions:
            model:
                description:
                    - "Model of the watchdog device. For example: I(i6300esb), I(diag288) or I(null)."
            action:
                description:
                    - "Watchdog action to be performed when watchdog is triggered. For example: I(none), I(reset), I(poweroff), I(pause) or I(dump)."
    graphical_console:
        description:
            - "Assign graphical console to the virtual machine."
        type: dict
        suboptions:
            headless_mode:
                description:
                    - If I(true) disable the graphics console for this virtual machine.
                type: bool
            protocol:
                description:
                    - Graphical protocol, a list of I(spice), I(vnc), or both.
                type: list
                elements: str
            disconnect_action:
                description:
                    - "Returns the action that will take place when the graphic console(SPICE only) is disconnected. The options are:"
                    - I(none) No action is taken.
                    - I(lock_screen) Locks the currently active user session.
                    - I(logout) Logs out the currently active user session.
                    - I(reboot) Initiates a graceful virtual machine reboot.
                    - I(shutdown) Initiates a graceful virtual machine shutdown.
                type: str
            keyboard_layout:
                description:
                    - The keyboard layout to use with this graphic console.
                    - This option is only available for the VNC console type.
                    - If no keyboard is enabled then it won't be reported.
                type: str
            monitors:
                description:
                    - The number of monitors opened for this graphic console.
                    - This option is only available for the SPICE protocol.
                    - Possible values are 1, 2 or 4.
                type: int
    exclusive:
        description:
            - "When C(state) is I(exported) this parameter indicates if the existing VM with the
               same name should be overwritten."
        type: bool
    export_domain:
        description:
            - "When C(state) is I(exported)this parameter specifies the name of the export storage domain."
        type: str
    export_ova:
        description:
            - Dictionary of values to be used to export VM as OVA.
        type: dict
        suboptions:
            host:
                description:
                    - The name of the destination host where the OVA has to be exported.
            directory:
                description:
                    - The name of the directory where the OVA has to be exported.
            filename:
                description:
                    - The name of the exported OVA file.
    force_migrate:
        description:
            - If I(true), the VM will migrate when I(placement_policy=user-migratable) but not when I(placement_policy=pinned).
        type: bool
    migrate:
        description:
            - "If I(true), the VM will migrate to any available host."
        type: bool
    next_run:
        description:
            - "If I(true), the update will not be applied to the VM immediately and will be only applied when virtual machine is restarted."
            - NOTE - If there are multiple next run configuration changes on the VM, the first change may get reverted if this option is not passed.
        type: bool
    snapshot_name:
        description:
            - "Snapshot to clone VM from."
            - "Snapshot with description specified should exist."
            - "You have to specify C(snapshot_vm) parameter with virtual machine name of this snapshot."
        type: str
    snapshot_vm:
        description:
            - "Source VM to clone VM from."
            - "VM should have snapshot specified by C(snapshot)."
            - "If C(snapshot_name) specified C(snapshot_vm) is required."
        type: str
    custom_emulated_machine:
        description:
            - "Sets the value of the custom_emulated_machine attribute."
        type: str

notes:
    - If VM is in I(UNASSIGNED) or I(UNKNOWN) state before any operation, the module will fail.
      If VM is in I(IMAGE_LOCKED) state before any operation, we try to wait for VM to be I(DOWN).
      If VM is in I(SAVING_STATE) state before any operation, we try to wait for VM to be I(SUSPENDED).
      If VM is in I(POWERING_DOWN) state before any operation, we try to wait for VM to be I(UP) or I(DOWN). VM can
      get into I(UP) state from I(POWERING_DOWN) state, when there is no ACPI or guest agent running inside VM, or
      if the shutdown operation fails.
      When user specify I(UP) C(state), we always wait to VM to be in I(UP) state in case VM is I(MIGRATING),
      I(REBOOTING), I(POWERING_UP), I(RESTORING_STATE), I(WAIT_FOR_LAUNCH). In other states we run start operation on VM.
      When user specify I(stopped) C(state), and If user pass C(force) parameter set to I(true) we forcibly stop the VM in
      any state. If user don't pass C(force) parameter, we always wait to VM to be in UP state in case VM is
      I(MIGRATING), I(REBOOTING), I(POWERING_UP), I(RESTORING_STATE), I(WAIT_FOR_LAUNCH). If VM is in I(PAUSED) or
      I(SUSPENDED) state, we start the VM. Then we gracefully shutdown the VM.
      When user specify I(suspended) C(state), we always wait to VM to be in UP state in case VM is I(MIGRATING),
      I(REBOOTING), I(POWERING_UP), I(RESTORING_STATE), I(WAIT_FOR_LAUNCH). If VM is in I(PAUSED) or I(DOWN) state,
      we start the VM. Then we suspend the VM.
      When user specify I(absent) C(state), we forcibly stop the VM in any state and remove it.
    - "If you update a VM parameter that requires a reboot, the oVirt engine always creates a new snapshot for the VM,
      and an Ansible playbook will report this as changed."
extends_documentation_fragment: ovirt.ovirt.ovirt
'''

EXAMPLES = '''
# Examples don't contain auth parameter for simplicity,
# look at ovirt_auth module to see how to reuse authentication:

- name: Creates a new Virtual Machine from template named 'rhel7_template'
  ovirt.ovirt.ovirt_vm:
    state: present
    name: myvm
    template: rhel7_template
    cluster: mycluster

- name: Register VM
  ovirt.ovirt.ovirt_vm:
    state: registered
    storage_domain: mystorage
    cluster: mycluster
    name: myvm

- name: Register VM using id
  ovirt.ovirt.ovirt_vm:
    state: registered
    storage_domain: mystorage
    cluster: mycluster
    id: 1111-1111-1111-1111

- name: Register VM, allowing partial import
  ovirt.ovirt.ovirt_vm:
    state: registered
    storage_domain: mystorage
    allow_partial_import: "True"
    cluster: mycluster
    id: 1111-1111-1111-1111

- name: Register VM with vnic profile mappings and reassign bad macs
  ovirt.ovirt.ovirt_vm:
    state: registered
    storage_domain: mystorage
    cluster: mycluster
    id: 1111-1111-1111-1111
    vnic_profile_mappings:
    - source_network_name: mynetwork
      source_profile_name: mynetwork
      target_profile_id: 3333-3333-3333-3333
    - source_network_name: mynetwork2
      source_profile_name: mynetwork2
      target_profile_id: 4444-4444-4444-4444
    reassign_bad_macs: "True"

- name: Register VM with mappings
  ovirt.ovirt.ovirt_vm:
    state: registered
    storage_domain: mystorage
    cluster: mycluster
    id: 1111-1111-1111-1111
    role_mappings:
      - source_name: Role_A
        dest_name: Role_B
    domain_mappings:
      - source_name: Domain_A
        dest_name: Domain_B
    lun_mappings:
      - source_storage_type: iscsi
        source_logical_unit_id: 1IET_000d0001
        source_logical_unit_port: 3260
        source_logical_unit_portal: 1
        source_logical_unit_address: 10.34.63.203
        source_logical_unit_target: iqn.2016-08-09.brq.str-01:omachace
        dest_storage_type: iscsi
        dest_logical_unit_id: 1IET_000d0002
        dest_logical_unit_port: 3260
        dest_logical_unit_portal: 1
        dest_logical_unit_address: 10.34.63.204
        dest_logical_unit_target: iqn.2016-08-09.brq.str-02:omachace
    affinity_group_mappings:
      - source_name: Affinity_A
        dest_name: Affinity_B
    affinity_label_mappings:
      - source_name: Label_A
        dest_name: Label_B
    cluster_mappings:
      - source_name: cluster_A
        dest_name: cluster_B

- name: Creates a stateless VM which will always use latest template version
  ovirt.ovirt.ovirt_vm:
    name: myvm
    template: rhel7
    cluster: mycluster
    use_latest_template_version: true

# Creates a new server rhel7 Virtual Machine from Blank template
# on brq01 cluster with 2GiB memory and 2 vcpu cores/sockets
# and attach bootable disk with name rhel7_disk and attach virtio NIC
- ovirt.ovirt.ovirt_vm:
    state: present
    cluster: brq01
    name: myvm
    memory: 2GiB
    cpu_cores: 2
    cpu_sockets: 2
    cpu_shares: 1024
    type: server
    operating_system: rhel_7x64
    disks:
      - name: rhel7_disk
        bootable: True
    nics:
      - name: nic1

# Change VM Name
- ovirt.ovirt.ovirt_vm:
    id: 00000000-0000-0000-0000-000000000000
    name: "new_vm_name"

- name: Run VM with cloud init
  ovirt.ovirt.ovirt_vm:
    name: rhel7
    template: rhel7
    cluster: Default
    memory: 1GiB
    high_availability: true
    high_availability_priority: 50  # Available from Ansible 2.5
    cloud_init:
      dns_servers: '8.8.8.8 8.8.4.4'
      nic_boot_protocol: static
      nic_ip_address: 10.34.60.86
      nic_netmask: 255.255.252.0
      nic_gateway: 10.34.63.254
      nic_name: eth1
      host_name: example.com
      custom_script: |
        write_files:
         - content: |
             Hello, world!
           path: /tmp/greeting.txt
           permissions: '0644'
      user_name: root
      root_password: super_password

- name: Run VM with cloud init, with multiple network interfaces
  ovirt.ovirt.ovirt_vm:
    name: rhel7_4
    template: rhel7
    cluster: mycluster
    cloud_init_nics:
    - nic_name: eth0
      nic_boot_protocol: dhcp
    - nic_name: eth1
      nic_boot_protocol: static
      nic_ip_address: 10.34.60.86
      nic_netmask: 255.255.252.0
      nic_gateway: 10.34.63.254
    # IP version 6 parameters are supported since ansible 2.9
    - nic_name: eth2
      nic_boot_protocol_v6: static
      nic_ip_address_v6: '2620:52:0:2282:b898:1f69:6512:36c5'
      nic_gateway_v6: '2620:52:0:2282:b898:1f69:6512:36c9'
      nic_netmask_v6: '120'
    - nic_name: eth3
      nic_boot_protocol_v6: dhcp

- name: Run VM with sysprep
  ovirt.ovirt.ovirt_vm:
    name: windows2012R2_AD
    template: windows2012R2
    cluster: Default
    memory: 3GiB
    high_availability: true
    sysprep:
      host_name: windowsad.example.com
      user_name: Administrator
      root_password: SuperPassword123

- name: Migrate/Run VM to/on host named 'host1'
  ovirt.ovirt.ovirt_vm:
    state: running
    name: myvm
    host: host1

- name: Migrate/Run VM to/on host named 'host1' on cluster 'cluster1'
  ovirt.ovirt.ovirt_vm:
    state: running
    name: myvm
    host: host1
    cluster: cluster1

- name: Migrate VM to any available host
  ovirt.ovirt.ovirt_vm:
    state: running
    name: myvm
    migrate: true

- name: Change VMs CD
  ovirt.ovirt.ovirt_vm:
    name: myvm
    cd_iso: drivers.iso

- name: Eject VMs CD
  ovirt.ovirt.ovirt_vm:
    name: myvm
    cd_iso: ''

- name: Boot VM from CD
  ovirt.ovirt.ovirt_vm:
    name: myvm
    cd_iso: centos7_x64.iso
    boot_devices:
        - cdrom

- name: Stop vm
  ovirt.ovirt.ovirt_vm:
    state: stopped
    name: myvm

- name: Upgrade memory to already created VM
  ovirt.ovirt.ovirt_vm:
    name: myvm
    memory: 4GiB

- name: Hot plug memory to already created and running VM (VM won't be restarted)
  ovirt.ovirt.ovirt_vm:
    name: myvm
    memory: 4GiB

# Create/update a VM to run with two vNUMA nodes and pin them to physical NUMA nodes as follows:
# vnuma index 0-> numa index 0, vnuma index 1-> numa index 1
- name: Create a VM to run with two vNUMA nodes
  ovirt.ovirt.ovirt_vm:
    name: myvm
    cluster: mycluster
    numa_tune_mode: "interleave"
    numa_nodes:
    - index: 0
      cores: [0]
      memory: 20
      numa_node_pins: [0]
    - index: 1
      cores: [1]
      memory: 30
      numa_node_pins: [1]

- name: Update an existing VM to run without previously created vNUMA nodes (i.e. remove all vNUMA nodes+NUMA pinning setting)
  ovirt.ovirt.ovirt_vm:
    name: myvm
    cluster: mycluster
    state: "present"
    numa_tune_mode: "interleave"
    numa_nodes:
    - index: -1

# When change on the VM needs restart of the VM, use next_run state,
# The VM will be updated and rebooted if there are any changes.
# If present state would be used, VM won't be restarted.
- ovirt.ovirt.ovirt_vm:
    state: next_run
    name: myvm
    boot_devices:
      - network

- name: Import virtual machine from VMware
  ovirt.ovirt.ovirt_vm:
    state: stopped
    cluster: mycluster
    name: vmware_win10
    timeout: 1800
    poll_interval: 30
    vmware:
      url: vpx://user@1.2.3.4/Folder1/Cluster1/2.3.4.5?no_verify=1
      name: windows10
      storage_domain: mynfs
      username: user
      password: password

- name: Create vm from template and create all disks on specific storage domain
  ovirt.ovirt.ovirt_vm:
    name: vm_test
    cluster: mycluster
    template: mytemplate
    storage_domain: mynfs
    nics:
    - name: nic1

- name: Remove VM, if VM is running it will be stopped
  ovirt.ovirt.ovirt_vm:
    state: absent
    name: myvm

# Defining a specific quota for a VM:
# Since Ansible 2.5
- ovirt.ovirt.ovirt_quotas_info:
    data_center: Default
    name: myquota
  register: ovirt_quotas
- ovirt.ovirt.ovirt_vm:
    name: myvm
    sso: False
    boot_menu: True
    bios_type: q35_ovmf
    usb_support: True
    serial_console: True
    quota_id: "{{ ovirt_quotas[0]['id'] }}"

- name: Create a VM that has the console configured for both Spice and VNC
  ovirt.ovirt.ovirt_vm:
    name: myvm
    template: mytemplate
    cluster: mycluster
    graphical_console:
      protocol:
        - spice
        - vnc

# Execute remote viewer to VM
- block:
  - name: Create a ticket for console for a running VM
    ovirt.ovirt.ovirt_vm:
      name: myvm
      ticket: true
      state: running
    register: myvm

  - name: Save ticket to file
    ansible.builtin.copy:
      content: "{{ myvm.vm.remote_vv_file }}"
      dest: ~/vvfile.vv

  - name: Run remote viewer with file
    ansible.builtin.command: remote-viewer ~/vvfile.vv

# Default value of host_device state is present
- name: Attach host devices to virtual machine
  ovirt.ovirt.ovirt_vm:
    name: myvm
    host: myhost
    placement_policy: pinned
    host_devices:
      - name: pci_0000_00_06_0
      - name: pci_0000_00_07_0
        state: absent
      - name: pci_0000_00_08_0
        state: present

- name: Add placement policy with multiple hosts
  ovirt.ovirt.ovirt_vm:
    name: myvm
    placement_policy: migratable
    placement_policy_hosts:
      - host1
      - host2

- name: Export the VM as OVA
  ovirt.ovirt.ovirt_vm:
    name: myvm
    state: exported
    cluster: mycluster
    export_ova:
        host: myhost
        filename: myvm.ova
        directory: /tmp/

- name: Clone VM from snapshot
  ovirt.ovirt.ovirt_vm:
    snapshot_vm: myvm
    snapshot_name: myvm_snap
    name: myvm_clone
    state: present

- name: Import external ova VM
  ovirt.ovirt.ovirt_vm:
    cluster: mycluster
    name: myvm
    host: myhost
    timeout: 1800
    poll_interval: 30
    kvm:
      name: myvm
      url: ova:///path/myvm.ova
      storage_domain: mystorage

- name: Cpu pinning of 0#12_1#13_2#14_3#15
  ovirt.ovirt.ovirt_vm:
    state: present
    cluster: mycluster
    name: myvm
    cpu_pinning:
      - cpu: 12
        vcpu: 0
      - cpu: 13
        vcpu: 1
      - cpu: 14
        vcpu: 2
      - cpu: 15
        vcpu: 3
'''


RETURN = '''
id:
    description: ID of the VM which is managed
    returned: On success if VM is found.
    type: str
    sample: 7de90f31-222c-436c-a1ca-7e655bd5b60c
vm:
    description: "Dictionary of all the VM attributes. VM attributes can be found on your oVirt/RHV instance
                  at following url: http://ovirt.github.io/ovirt-engine-api-model/master/#types/vm.
                  Additionally when user sent ticket=true, this module will return also remote_vv_file
                  parameter in vm dictionary, which contains remote-viewer compatible file to open virtual
                  machine console. Please note that this file contains sensible information."
    returned: On success if VM is found.
    type: dict
'''
import traceback

try:
    import ovirtsdk4.types as otypes
except ImportError:
    pass

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ovirt.ovirt.plugins.module_utils.ovirt import (
    BaseModule,
    check_params,
    check_sdk,
    convert_to_bytes,
    create_connection,
    equal,
    get_dict_of_struct,
    get_entity,
    get_link_name,
    get_id_by_name,
    ovirt_full_argument_spec,
    search_by_attributes,
    search_by_name,
    wait,
)


class VmsModule(BaseModule):

    def __init__(self, *args, **kwargs):
        super(VmsModule, self).__init__(*args, **kwargs)
        self._initialization = None
        self._is_new = False

    def __get_template_with_version(self):
        """
        oVirt/RHV in version 4.1 doesn't support search by template+version_number,
        so we need to list all templates with specific name and then iterate
        through it's version until we find the version we look for.
        """
        template = None
        templates_service = self._connection.system_service().templates_service()
        if self._is_new:
            if self.param('template'):
                clusters_service = self._connection.system_service().clusters_service()
                cluster = search_by_name(clusters_service, self.param('cluster'))
                data_center = self._connection.follow_link(cluster.data_center)
                templates = templates_service.list(
                    search='name=%s and datacenter=%s' % (self.param('template'), data_center.name)
                )
                if self.param('template_version'):
                    templates = [
                        t for t in templates
                        if t.version.version_number == self.param('template_version')
                    ]
                if not templates:
                    raise ValueError(
                        "Template with name '%s' and version '%s' in data center '%s' was not found" % (
                            self.param('template'),
                            self.param('template_version'),
                            data_center.name
                        )
                    )
                template = sorted(templates, key=lambda t: t.version.version_number, reverse=True)[0]
            else:
                # If template isn't specified and VM is about to be created specify default template:
                template = templates_service.template_service('00000000-0000-0000-0000-000000000000').get()
        else:
            templates = templates_service.list(
                search='vm.name=%s' % self.param('name')
            )
            if templates:
                template = templates[0]
                if self.param('template') is not None and self.param('template') != template.name:
                    raise ValueError("You can not change template of the Virtual Machine.")

        return template

    def __get_storage_domain_and_all_template_disks(self, template):

        if self.param('template') is None:
            return None

        if self.param('storage_domain') is None:
            return None

        disks = list()

        for att in self._connection.follow_link(template.disk_attachments):
            disks.append(
                otypes.DiskAttachment(
                    disk=otypes.Disk(
                        id=att.disk.id,
                        format=otypes.DiskFormat(self.param('disk_format')),
                        storage_domains=[
                            otypes.StorageDomain(
                                id=get_id_by_name(
                                    self._connection.system_service().storage_domains_service(),
                                    self.param('storage_domain')
                                )
                            )
                        ]
                    )
                )
            )

        return disks

    def __get_snapshot(self):

        if self.param('snapshot_vm') is None:
            return None

        if self.param('snapshot_name') is None:
            return None

        vms_service = self._connection.system_service().vms_service()
        vm_id = get_id_by_name(vms_service, self.param('snapshot_vm'))
        vm_service = vms_service.vm_service(vm_id)

        snaps_service = vm_service.snapshots_service()
        snaps = snaps_service.list()
        snap = next(
            (s for s in snaps if s.description == self.param('snapshot_name')),
            None
        )
        return snap

    def __get_placement_policy(self):
        hosts = None
        if self.param('placement_policy_hosts'):
            hosts = [otypes.Host(name=host) for host in self.param('placement_policy_hosts')]
        elif self.param('host'):
            hosts = [otypes.Host(name=self.param('host'))]
        if self.param('placement_policy'):
            return otypes.VmPlacementPolicy(
                affinity=otypes.VmAffinity(self.param('placement_policy')),
                hosts=hosts
            )
        return None

    def __get_cluster(self):
        if self.param('cluster') is not None:
            return self.param('cluster')
        elif self.param('snapshot_name') is not None and self.param('snapshot_vm') is not None:
            vms_service = self._connection.system_service().vms_service()
            vm = search_by_name(vms_service, self.param('snapshot_vm'))
            return self._connection.system_service().clusters_service().cluster_service(vm.cluster.id).get().name

    def build_entity(self):
        template = self.__get_template_with_version()
        cluster = self.__get_cluster()
        snapshot = self.__get_snapshot()
        placement_policy = self.__get_placement_policy()
        display = self.param('graphical_console') or dict()

        disk_attachments = self.__get_storage_domain_and_all_template_disks(template)

        return otypes.Vm(
            id=self.param('id'),
            name=self.param('name'),
            cluster=otypes.Cluster(
                name=cluster
            ) if cluster else None,
            disk_attachments=disk_attachments,
            template=otypes.Template(
                id=template.id,
            ) if template else None,
            use_latest_template_version=self.param('use_latest_template_version'),
            stateless=self.param('stateless') or self.param('use_latest_template_version'),
            delete_protected=self.param('delete_protected'),
            custom_emulated_machine=self.param('custom_emulated_machine'),
            bios=(
                otypes.Bios(
                    boot_menu=otypes.BootMenu(enabled=self.param('boot_menu')) if self.param('boot_menu') is not None else None,
                    type=otypes.BiosType[self.param('bios_type').upper()] if self.param('bios_type') is not None else None
                )
            ) if self.param('boot_menu') is not None or self.param('bios_type') is not None else None,
            console=(
                otypes.Console(enabled=self.param('serial_console'))
            ) if self.param('serial_console') is not None else None,
            usb=(
                otypes.Usb(enabled=self.param('usb_support'))
            ) if self.param('usb_support') is not None else None,
            sso=(
                otypes.Sso(
                    methods=[otypes.Method(id=otypes.SsoMethod.GUEST_AGENT)] if self.param('sso') else []
                )
            ) if self.param('sso') is not None else None,
            quota=otypes.Quota(id=self._module.params.get('quota_id')) if self.param('quota_id') is not None else None,
            high_availability=otypes.HighAvailability(
                enabled=self.param('high_availability'),
                priority=self.param('high_availability_priority'),
            ) if self.param('high_availability') is not None or self.param('high_availability_priority') else None,
            lease=otypes.StorageDomainLease(
                storage_domain=otypes.StorageDomain(
                    id=get_id_by_name(
                        service=self._connection.system_service().storage_domains_service(),
                        name=self.param('lease')
                    ) if self.param('lease') else None
                )
            ) if self.param('lease') is not None else None,
            cpu=otypes.Cpu(
                topology=otypes.CpuTopology(
                    cores=self.param('cpu_cores'),
                    sockets=self.param('cpu_sockets'),
                    threads=self.param('cpu_threads'),
                ) if any((
                    self.param('cpu_cores'),
                    self.param('cpu_sockets'),
                    self.param('cpu_threads')
                )) else None,
                cpu_tune=otypes.CpuTune(
                    vcpu_pins=[
                        otypes.VcpuPin(vcpu=int(pin['vcpu']), cpu_set=str(pin['cpu'])) for pin in self.param('cpu_pinning')
                    ],
                ) if self.param('cpu_pinning') else None,
                mode=otypes.CpuMode(self.param('cpu_mode')) if self.param('cpu_mode') else None,
            ) if any((
                self.param('cpu_cores'),
                self.param('cpu_sockets'),
                self.param('cpu_threads'),
                self.param('cpu_mode'),
                self.param('cpu_pinning')
            )) else None,
            cpu_shares=self.param('cpu_shares'),
            os=otypes.OperatingSystem(
                type=self.param('operating_system'),
                boot=otypes.Boot(
                    devices=[
                        otypes.BootDevice(dev) for dev in self.param('boot_devices')
                    ],
                ) if self.param('boot_devices') else None,
                cmdline=self.param('kernel_params') if self.param('kernel_params_persist') else None,
                initrd=self.param('initrd_path') if self.param('kernel_params_persist') else None,
                kernel=self.param('kernel_path') if self.param('kernel_params_persist') else None,
            ) if (
                self.param('operating_system') or self.param('boot_devices') or self.param('kernel_params_persist')
            ) else None,
            type=otypes.VmType(
                self.param('type')
            ) if self.param('type') else None,
            memory=convert_to_bytes(
                self.param('memory')
            ) if self.param('memory') else None,
            memory_policy=otypes.MemoryPolicy(
                guaranteed=convert_to_bytes(self.param('memory_guaranteed')),
                ballooning=self.param('ballooning_enabled'),
                max=convert_to_bytes(self.param('memory_max')),
            ) if any((
                self.param('memory_guaranteed'),
                self.param('ballooning_enabled') is not None,
                self.param('memory_max')
            )) else None,
            instance_type=otypes.InstanceType(
                id=get_id_by_name(
                    self._connection.system_service().instance_types_service(),
                    self.param('instance_type'),
                ),
            ) if self.param('instance_type') else None,
            custom_compatibility_version=otypes.Version(
                major=self._get_major(self.param('custom_compatibility_version')),
                minor=self._get_minor(self.param('custom_compatibility_version')),
            ) if self.param('custom_compatibility_version') is not None else None,
            description=self.param('description'),
            comment=self.param('comment'),
            time_zone=otypes.TimeZone(
                name=self.param('timezone'),
            ) if self.param('timezone') else None,
            serial_number=otypes.SerialNumber(
                policy=otypes.SerialNumberPolicy(self.param('serial_policy')),
                value=self.param('serial_policy_value'),
            ) if (
                self.param('serial_policy') is not None or
                self.param('serial_policy_value') is not None
            ) else None,
            placement_policy=placement_policy,
            soundcard_enabled=self.param('soundcard_enabled'),
            display=otypes.Display(
                smartcard_enabled=self.param('smartcard_enabled'),
                disconnect_action=display.get('disconnect_action'),
                keyboard_layout=display.get('keyboard_layout'),
                monitors=display.get('monitors'),
            ) if (
                self.param('smartcard_enabled') is not None or
                display.get('disconnect_action') is not None or
                display.get('keyboard_layout') is not None or
                display.get('monitors') is not None
            ) else None,
            io=otypes.Io(
                threads=self.param('io_threads'),
            ) if self.param('io_threads') is not None else None,
            numa_tune_mode=otypes.NumaTuneMode(
                self.param('numa_tune_mode')
            ) if self.param('numa_tune_mode') else None,
            rng_device=otypes.RngDevice(
                source=otypes.RngSource(self.param('rng_device')),
            ) if self.param('rng_device') else None,
            custom_properties=[
                otypes.CustomProperty(
                    name=cp.get('name'),
                    regexp=cp.get('regexp'),
                    value=str(cp.get('value')),
                ) for cp in self.param('custom_properties') if cp
            ] if self.param('custom_properties') is not None else None,
            initialization=self.get_initialization() if self.param('cloud_init_persist') else None,
            snapshots=[otypes.Snapshot(id=snapshot.id)] if snapshot is not None else None,
        )

    def _get_export_domain_service(self):
        provider_name = self._module.params['export_domain']
        export_sds_service = self._connection.system_service().storage_domains_service()
        export_sd_id = get_id_by_name(export_sds_service, provider_name)
        return export_sds_service.service(export_sd_id)

    def post_export_action(self, entity):
        self._service = self._get_export_domain_service().vms_service()

    def update_check(self, entity):
        res = self._update_check(entity)
        if entity.next_run_configuration_exists:
            res = res and self._update_check(self._service.service(entity.id).get(next_run=True))

        return res

    def _update_check(self, entity):
        def check_cpu_pinning():
            if self.param('cpu_pinning'):
                current = []
                if entity.cpu.cpu_tune:
                    current = [(str(pin.cpu_set), int(pin.vcpu)) for pin in entity.cpu.cpu_tune.vcpu_pins]
                passed = [(str(pin['cpu']), int(pin['vcpu'])) for pin in self.param('cpu_pinning')]
                return sorted(current) == sorted(passed)
            return True

        def check_custom_properties():
            if self.param('custom_properties'):
                current = []
                if entity.custom_properties:
                    current = [(cp.name, cp.regexp, str(cp.value)) for cp in entity.custom_properties]
                passed = [(cp.get('name'), cp.get('regexp'), str(cp.get('value'))) for cp in self.param('custom_properties') if cp]
                return sorted(current) == sorted(passed)
            return True

        def check_placement_policy():
            if self.param('placement_policy'):
                hosts = sorted(
                    map(lambda host: self._connection.follow_link(host).name,
                        entity.placement_policy.hosts if entity.placement_policy.hosts else [])
                )
                if self.param('placement_policy_hosts'):
                    return (
                        equal(self.param('placement_policy'), str(entity.placement_policy.affinity) if entity.placement_policy else None) and
                        equal(sorted(self.param('placement_policy_hosts')), hosts)
                    )
                return (
                    equal(self.param('placement_policy'), str(entity.placement_policy.affinity) if entity.placement_policy else None) and
                    equal([self.param('host')], hosts)
                )
            return True

        def check_host():
            if self.param('host') is not None:
                return self.param('host') in [self._connection.follow_link(host).name for host in getattr(entity.placement_policy, 'hosts', None) or []]
            return True

        def check_custom_compatibility_version():
            if self.param('custom_compatibility_version') is not None:
                return (self._get_minor(self.param('custom_compatibility_version')) == self._get_minor(entity.custom_compatibility_version) and
                        self._get_major(self.param('custom_compatibility_version')) == self._get_major(entity.custom_compatibility_version))
            return True

        cpu_mode = getattr(entity.cpu, 'mode')
        vm_display = entity.display
        provided_vm_display = self.param('graphical_console') or dict()
        return (
            check_cpu_pinning() and
            check_custom_properties() and
            check_host() and
            check_placement_policy() and
            check_custom_compatibility_version() and
            not self.param('cloud_init_persist') and
            not self.param('kernel_params_persist') and
            equal(self.param('cluster'), get_link_name(self._connection, entity.cluster)) and equal(convert_to_bytes(self.param('memory')), entity.memory) and
            equal(convert_to_bytes(self.param('memory_guaranteed')), entity.memory_policy.guaranteed) and
            equal(convert_to_bytes(self.param('memory_max')), entity.memory_policy.max) and
            equal(self.param('cpu_cores'), entity.cpu.topology.cores) and
            equal(self.param('cpu_sockets'), entity.cpu.topology.sockets) and
            equal(self.param('cpu_threads'), entity.cpu.topology.threads) and
            equal(self.param('cpu_mode'), str(cpu_mode) if cpu_mode else None) and
            equal(self.param('type'), str(entity.type)) and
            equal(self.param('name'), str(entity.name)) and
            equal(self.param('operating_system'), str(entity.os.type)) and
            equal(self.param('boot_menu'), entity.bios.boot_menu.enabled) and
            equal(self.param('bios_type'), entity.bios.type.value) and
            equal(self.param('soundcard_enabled'), entity.soundcard_enabled) and
            equal(self.param('smartcard_enabled'), getattr(vm_display, 'smartcard_enabled', False)) and
            equal(self.param('io_threads'), entity.io.threads) and
            equal(self.param('ballooning_enabled'), entity.memory_policy.ballooning) and
            equal(self.param('serial_console'), getattr(entity.console, 'enabled', None)) and
            equal(self.param('usb_support'), entity.usb.enabled) and
            equal(self.param('sso'), True if entity.sso.methods else False) and
            equal(self.param('quota_id'), getattr(entity.quota, 'id', None)) and
            equal(self.param('high_availability'), entity.high_availability.enabled) and
            equal(self.param('high_availability_priority'), entity.high_availability.priority) and
            equal(self.param('lease'), get_link_name(self._connection, getattr(entity.lease, 'storage_domain', None))) and
            equal(self.param('stateless'), entity.stateless) and
            equal(self.param('cpu_shares'), entity.cpu_shares) and
            equal(self.param('delete_protected'), entity.delete_protected) and
            equal(self.param('custom_emulated_machine'), entity.custom_emulated_machine) and
            equal(self.param('use_latest_template_version'), entity.use_latest_template_version) and
            equal(self.param('boot_devices'), [str(dev) for dev in getattr(entity.os.boot, 'devices', [])]) and
            equal(self.param('instance_type'), get_link_name(self._connection, entity.instance_type), ignore_case=True) and
            equal(self.param('description'), entity.description) and
            equal(self.param('comment'), entity.comment) and
            equal(self.param('timezone'), getattr(entity.time_zone, 'name', None)) and
            equal(self.param('serial_policy'), str(getattr(entity.serial_number, 'policy', None))) and
            equal(self.param('serial_policy_value'), getattr(entity.serial_number, 'value', None)) and
            equal(self.param('numa_tune_mode'), str(entity.numa_tune_mode)) and
            equal(self.param('rng_device'), str(entity.rng_device.source) if entity.rng_device else None) and
            equal(provided_vm_display.get('monitors'), getattr(vm_display, 'monitors', None)) and
            equal(provided_vm_display.get('keyboard_layout'), getattr(vm_display, 'keyboard_layout', None)) and
            equal(provided_vm_display.get('disconnect_action'), getattr(vm_display, 'disconnect_action', None), ignore_case=True)
        )

    def pre_create(self, entity):
        # Mark if entity exists before touching it:
        if entity is None:
            self._is_new = True

    def post_update(self, entity):
        self.post_present(entity.id)

    def post_present(self, entity_id):
        # After creation of the VM, attach disks and NICs:
        entity = self._service.service(entity_id).get()
        self.__attach_disks(entity)
        self.__attach_nics(entity)
        self._attach_cd(entity)
        self.changed = self.__attach_numa_nodes(entity)
        self.changed = self.__attach_watchdog(entity)
        self.changed = self.__attach_graphical_console(entity)
        self.changed = self.__attach_host_devices(entity)

    def pre_remove(self, entity):
        # Forcibly stop the VM, if it's not in DOWN state:
        if entity.status != otypes.VmStatus.DOWN:
            if not self._module.check_mode:
                self.changed = self.action(
                    action='stop',
                    action_condition=lambda vm: vm.status != otypes.VmStatus.DOWN,
                    wait_condition=lambda vm: vm.status == otypes.VmStatus.DOWN,
                )['changed']

    def __suspend_shutdown_common(self, vm_service):
        if vm_service.get().status in [
            otypes.VmStatus.MIGRATING,
            otypes.VmStatus.POWERING_UP,
            otypes.VmStatus.REBOOT_IN_PROGRESS,
            otypes.VmStatus.WAIT_FOR_LAUNCH,
            otypes.VmStatus.UP,
            otypes.VmStatus.RESTORING_STATE,
        ]:
            self._wait_for_UP(vm_service)

    def _pre_shutdown_action(self, entity):
        vm_service = self._service.vm_service(entity.id)
        self.__suspend_shutdown_common(vm_service)
        if entity.status in [otypes.VmStatus.SUSPENDED, otypes.VmStatus.PAUSED]:
            vm_service.start()
            self._wait_for_UP(vm_service)
        return vm_service.get()

    def _pre_suspend_action(self, entity):
        vm_service = self._service.vm_service(entity.id)
        self.__suspend_shutdown_common(vm_service)
        if entity.status in [otypes.VmStatus.PAUSED, otypes.VmStatus.DOWN]:
            vm_service.start()
            self._wait_for_UP(vm_service)
        return vm_service.get()

    def _post_start_action(self, entity):
        vm_service = self._service.service(entity.id)
        self._wait_for_UP(vm_service)
        self._attach_cd(vm_service.get())

    def __get_cds_from_sds(self, sds):
        for sd in sds:
            if sd.type == otypes.StorageDomainType.ISO:
                disks = sd.files
            elif sd.type == otypes.StorageDomainType.DATA:
                disks = sd.disks
            else:
                continue
            disks = list(filter(lambda x: (x.name == self.param('cd_iso') or x.id == self.param('cd_iso')) and
                                (sd.type == otypes.StorageDomainType.ISO or x.content_type == otypes.DiskContentType.ISO),
                                self._connection.follow_link(disks)))
            if disks:
                return disks

    def __get_cd_id(self):
        sds_service = self._connection.system_service().storage_domains_service()
        sds = sds_service.list(search='name="{0}"'.format(self.param('storage_domain') if self.param('storage_domain') else "*"))
        disks = self.__get_cds_from_sds(sds)
        if not disks:
            raise ValueError('Was not able to find disk with name or id "{0}".'.format(self.param('cd_iso')))
        if len(disks) > 1:
            raise ValueError('Found mutiple disks with same name "{0}" please use \
                disk ID in "cd_iso" to specify which disk should be used.'.format(self.param('cd_iso')))
        return disks[0].id

    def _attach_cd(self, entity):
        cd_iso_id = self.param('cd_iso')
        if cd_iso_id is not None:
            if cd_iso_id:
                cd_iso_id = self.__get_cd_id()
            vm_service = self._service.service(entity.id)
            current = vm_service.get().status == otypes.VmStatus.UP and self.param('state') == 'running'
            cdroms_service = vm_service.cdroms_service()
            cdrom_device = cdroms_service.list()[0]
            cdrom_service = cdroms_service.cdrom_service(cdrom_device.id)
            cdrom = cdrom_service.get(current=current)
            if getattr(cdrom.file, 'id', '') != cd_iso_id:
                if not self._module.check_mode:
                    cdrom_service.update(
                        cdrom=otypes.Cdrom(
                            file=otypes.File(id=cd_iso_id)
                        ),
                        current=current,
                    )
                self.changed = True

        return entity

    def _migrate_vm(self, entity):
        vm_host = self.param('host')
        vm_service = self._service.vm_service(entity.id)
        # In case VM is preparing to be UP, wait to be up, to migrate it:
        if entity.status == otypes.VmStatus.UP:
            if vm_host is not None:
                hosts_service = self._connection.system_service().hosts_service()
                clusters_service = self._connection.system_service().clusters_service()
                current_vm_host = hosts_service.host_service(entity.host.id).get().name
                if vm_host != current_vm_host:
                    if not self._module.check_mode:
                        vm_service.migrate(
                            cluster=search_by_name(clusters_service, self.param('cluster')),
                            host=otypes.Host(name=vm_host),
                            force=self.param('force_migrate')
                        )
                        self._wait_for_UP(vm_service)
                    self.changed = True
            elif self.param('migrate'):
                if not self._module.check_mode:
                    vm_service.migrate(force=self.param('force_migrate'))
                    self._wait_for_UP(vm_service)
                self.changed = True
        return entity

    def _wait_for_UP(self, vm_service):
        wait(
            service=vm_service,
            condition=lambda vm: vm.status == otypes.VmStatus.UP,
            wait=self.param('wait'),
            timeout=self.param('timeout'),
        )

    def _wait_for_vm_disks(self, vm_service):
        disks_service = self._connection.system_service().disks_service()
        for da in vm_service.disk_attachments_service().list():
            disk_service = disks_service.disk_service(da.disk.id)
            wait(
                service=disk_service,
                condition=lambda disk: disk.status == otypes.DiskStatus.OK if disk.storage_type == otypes.DiskStorageType.IMAGE else True,
                wait=self.param('wait'),
                timeout=self.param('timeout'),
            )

    def wait_for_down(self, vm):
        """
        This function will first wait for the status DOWN of the VM.
        Then it will find the active snapshot and wait until it's state is OK for
        stateless VMs and stateless snapshot is removed.
        """
        vm_service = self._service.vm_service(vm.id)
        wait(
            service=vm_service,
            condition=lambda vm: vm.status == otypes.VmStatus.DOWN,
            wait=self.param('wait'),
            timeout=self.param('timeout'),
        )
        if vm.stateless:
            snapshots_service = vm_service.snapshots_service()
            snapshots = snapshots_service.list()
            snap_active = [
                snap for snap in snapshots
                if snap.snapshot_type == otypes.SnapshotType.ACTIVE
            ][0]
            snap_stateless = [
                snap for snap in snapshots
                if snap.snapshot_type == otypes.SnapshotType.STATELESS
            ]
            # Stateless snapshot may be already removed:
            if snap_stateless:
                """
                We need to wait for Active snapshot ID, to be removed as it's current
                stateless snapshot. Then we need to wait for staless snapshot ID to
                be read, for use, because it will become active snapshot.
                """
                wait(
                    service=snapshots_service.snapshot_service(snap_active.id),
                    condition=lambda snap: snap is None,
                    wait=self.param('wait'),
                    timeout=self.param('timeout'),
                )
                wait(
                    service=snapshots_service.snapshot_service(snap_stateless[0].id),
                    condition=lambda snap: snap.snapshot_status == otypes.SnapshotStatus.OK,
                    wait=self.param('wait'),
                    timeout=self.param('timeout'),
                )
        return True

    def __attach_graphical_console(self, entity):
        graphical_console = self.param('graphical_console')
        if not graphical_console:
            return False

        vm_service = self._service.service(entity.id)
        gcs_service = vm_service.graphics_consoles_service()
        graphical_consoles = gcs_service.list()

        # Remove all graphical consoles if there are any:
        if bool(graphical_console.get('headless_mode')):
            if not self._module.check_mode:
                for gc in graphical_consoles:
                    gcs_service.console_service(gc.id).remove()
            return len(graphical_consoles) > 0

        # If there are not gc add any gc to be added:
        protocol = graphical_console.get('protocol')
        current_protocols = [str(gc.protocol) for gc in graphical_consoles]
        if not current_protocols:
            if not self._module.check_mode:
                for p in protocol:
                    gcs_service.add(
                        otypes.GraphicsConsole(
                            protocol=otypes.GraphicsType(p),
                        )
                    )
            return True

        # Update consoles:
        if sorted(protocol) != sorted(current_protocols):
            if not self._module.check_mode:
                for gc in graphical_consoles:
                    gcs_service.console_service(gc.id).remove()
                for p in protocol:
                    gcs_service.add(
                        otypes.GraphicsConsole(
                            protocol=otypes.GraphicsType(p),
                        )
                    )
            return True

    def __attach_disks(self, entity):
        if not self.param('disks'):
            return

        vm_service = self._service.service(entity.id)
        disks_service = self._connection.system_service().disks_service()
        disk_attachments_service = vm_service.disk_attachments_service()

        self._wait_for_vm_disks(vm_service)
        for disk in self.param('disks'):
            # If disk ID is not specified, find disk by name:
            disk_id = disk.get('id')
            if disk_id is None:
                disk_id = getattr(
                    search_by_name(
                        service=disks_service,
                        name=disk.get('name')
                    ),
                    'id',
                    None
                )

            # Attach disk to VM:
            disk_attachment = disk_attachments_service.attachment_service(disk_id)
            if get_entity(disk_attachment) is None:
                if not self._module.check_mode:
                    disk_attachments_service.add(
                        otypes.DiskAttachment(
                            disk=otypes.Disk(
                                id=disk_id,
                            ),
                            active=disk.get('activate', True),
                            interface=otypes.DiskInterface(
                                disk.get('interface', 'virtio')
                            ),
                            bootable=disk.get('bootable', False),
                        )
                    )
                self.changed = True

    def __get_vnic_profile_id(self, nic):
        """
        Return VNIC profile ID looked up by it's name, because there can be
        more VNIC profiles with same name, other criteria of filter is cluster.
        """
        vnics_service = self._connection.system_service().vnic_profiles_service()
        clusters_service = self._connection.system_service().clusters_service()
        cluster = search_by_name(clusters_service, self.param('cluster'))
        profiles = [
            profile for profile in vnics_service.list()
            if profile.name == nic.get('profile_name')
        ]
        cluster_networks = [
            net.id for net in self._connection.follow_link(cluster.networks)
        ]
        try:
            return next(
                profile.id for profile in profiles
                if profile.network.id in cluster_networks
            )
        except StopIteration:
            raise Exception(
                "Profile '%s' was not found in cluster '%s'" % (
                    nic.get('profile_name'),
                    self.param('cluster')
                )
            )

    def __get_numa_serialized(self, numa):
        return sorted([(x.index,
                        [y.index for y in x.cpu.cores] if x.cpu else [],
                        x.memory,
                        [y.index for y in x.numa_node_pins] if x.numa_node_pins else []
                        ) for x in numa], key=lambda x: x[0])

    def __attach_numa_nodes(self, entity):
        numa_nodes_service = self._service.service(entity.id).numa_nodes_service()
        existed_numa_nodes = numa_nodes_service.list()
        if len(self.param('numa_nodes')) > 0:
            # Remove all existing virtual numa nodes before adding new ones
            for current_numa_node in sorted(existed_numa_nodes, reverse=True, key=lambda x: x.index):
                numa_nodes_service.node_service(current_numa_node.id).remove()

        for numa_node in self.param('numa_nodes'):
            if numa_node is None or numa_node.get('index') is None or numa_node.get('cores') is None or numa_node.get('memory') is None:
                continue

            numa_nodes_service.add(
                otypes.VirtualNumaNode(
                    index=numa_node.get('index'),
                    memory=numa_node.get('memory'),
                    cpu=otypes.Cpu(
                        cores=[
                            otypes.Core(
                                index=core
                            ) for core in numa_node.get('cores')
                        ],
                    ),
                    numa_node_pins=[
                        otypes.NumaNodePin(
                            index=pin
                        ) for pin in numa_node.get('numa_node_pins')
                    ] if numa_node.get('numa_node_pins') is not None else None,
                )
            )
        return self.__get_numa_serialized(numa_nodes_service.list()) != self.__get_numa_serialized(existed_numa_nodes)

    def __attach_watchdog(self, entity):
        watchdogs_service = self._service.service(entity.id).watchdogs_service()
        watchdog = self.param('watchdog')
        if watchdog is not None:
            current_watchdog = next(iter(watchdogs_service.list()), None)
            if watchdog.get('model') is None and current_watchdog:
                watchdogs_service.watchdog_service(current_watchdog.id).remove()
                return True
            elif watchdog.get('model') is not None and current_watchdog is None:
                watchdogs_service.add(
                    otypes.Watchdog(
                        model=otypes.WatchdogModel(watchdog.get('model').lower()),
                        action=otypes.WatchdogAction(watchdog.get('action')),
                    )
                )
                return True
            elif current_watchdog is not None:
                if (
                    str(current_watchdog.model).lower() != watchdog.get('model').lower() or
                    str(current_watchdog.action).lower() != watchdog.get('action').lower()
                ):
                    watchdogs_service.watchdog_service(current_watchdog.id).update(
                        otypes.Watchdog(
                            model=otypes.WatchdogModel(watchdog.get('model')),
                            action=otypes.WatchdogAction(watchdog.get('action')),
                        )
                    )
                    return True
        return False

    def __attach_nics(self, entity):
        # Attach NICs to VM, if specified:
        nics_service = self._service.service(entity.id).nics_service()
        for nic in self.param('nics'):
            if search_by_name(nics_service, nic.get('name')) is None:
                if not self._module.check_mode:
                    nics_service.add(
                        otypes.Nic(
                            name=nic.get('name'),
                            interface=otypes.NicInterface(
                                nic.get('interface', 'virtio')
                            ),
                            vnic_profile=otypes.VnicProfile(
                                id=self.__get_vnic_profile_id(nic),
                            ) if nic.get('profile_name') else None,
                            mac=otypes.Mac(
                                address=nic.get('mac_address')
                            ) if nic.get('mac_address') else None,
                        )
                    )
                self.changed = True

    def get_initialization(self):
        if self._initialization is not None:
            return self._initialization

        sysprep = self.param('sysprep')
        cloud_init = self.param('cloud_init')
        cloud_init_nics = self.param('cloud_init_nics') or []
        if cloud_init is not None:
            cloud_init_nics.append(cloud_init)

        if cloud_init or cloud_init_nics:
            self._initialization = otypes.Initialization(
                nic_configurations=[
                    otypes.NicConfiguration(
                        boot_protocol=otypes.BootProtocol(
                            nic.pop('nic_boot_protocol').lower()
                        ) if nic.get('nic_boot_protocol') else None,
                        ipv6_boot_protocol=otypes.BootProtocol(
                            nic.pop('nic_boot_protocol_v6').lower()
                        ) if nic.get('nic_boot_protocol_v6') else None,
                        name=nic.pop('nic_name', None),
                        on_boot=True,
                        ip=otypes.Ip(
                            address=nic.pop('nic_ip_address', None),
                            netmask=nic.pop('nic_netmask', None),
                            gateway=nic.pop('nic_gateway', None),
                            version=otypes.IpVersion('v4')
                        ) if (
                            nic.get('nic_gateway') is not None or
                            nic.get('nic_netmask') is not None or
                            nic.get('nic_ip_address') is not None
                        ) else None,
                        ipv6=otypes.Ip(
                            address=nic.pop('nic_ip_address_v6', None),
                            netmask=nic.pop('nic_netmask_v6', None),
                            gateway=nic.pop('nic_gateway_v6', None),
                            version=otypes.IpVersion('v6')
                        ) if (
                            nic.get('nic_gateway_v6') is not None or
                            nic.get('nic_netmask_v6') is not None or
                            nic.get('nic_ip_address_v6') is not None
                        ) else None,
                    )
                    for nic in cloud_init_nics
                    if (
                        nic.get('nic_boot_protocol_v6') is not None or
                        nic.get('nic_ip_address_v6') is not None or
                        nic.get('nic_gateway_v6') is not None or
                        nic.get('nic_netmask_v6') is not None or
                        nic.get('nic_gateway') is not None or
                        nic.get('nic_netmask') is not None or
                        nic.get('nic_ip_address') is not None or
                        nic.get('nic_boot_protocol') is not None
                    )
                ] if cloud_init_nics else None,
                **cloud_init
            )
        elif sysprep:
            self._initialization = otypes.Initialization(
                **sysprep
            )
        return self._initialization

    def __attach_host_devices(self, entity):
        vm_service = self._service.service(entity.id)
        host_devices_service = vm_service.host_devices_service()
        host_devices = self.param('host_devices')
        updated = False
        if host_devices:
            device_names = [dev.name for dev in host_devices_service.list()]
            for device in host_devices:
                device_name = device.get('name')
                state = device.get('state', 'present')
                if state == 'absent' and device_name in device_names:
                    updated = True
                    if not self._module.check_mode:
                        device_id = get_id_by_name(host_devices_service, device.get('name'))
                        host_devices_service.device_service(device_id).remove()

                elif state == 'present' and device_name not in device_names:
                    updated = True
                    if not self._module.check_mode:
                        host_devices_service.add(
                            otypes.HostDevice(
                                name=device.get('name'),
                            )
                        )

        return updated


def _get_role_mappings(module):
    roleMappings = list()
    for roleMapping in module.params['role_mappings']:
        roleMappings.append(
            otypes.RegistrationRoleMapping(
                from_=otypes.Role(
                    name=roleMapping['source_name'],
                ) if roleMapping['source_name'] else None,
                to=otypes.Role(
                    name=roleMapping['dest_name'],
                ) if roleMapping['dest_name'] else None,
            )
        )
    return roleMappings


def _get_affinity_group_mappings(module):
    affinityGroupMappings = list()

    for affinityGroupMapping in module.params['affinity_group_mappings']:
        affinityGroupMappings.append(
            otypes.RegistrationAffinityGroupMapping(
                from_=otypes.AffinityGroup(
                    name=affinityGroupMapping['source_name'],
                ) if affinityGroupMapping['source_name'] else None,
                to=otypes.AffinityGroup(
                    name=affinityGroupMapping['dest_name'],
                ) if affinityGroupMapping['dest_name'] else None,
            )
        )
    return affinityGroupMappings


def _get_affinity_label_mappings(module):
    affinityLabelMappings = list()

    for affinityLabelMapping in module.params['affinity_label_mappings']:
        affinityLabelMappings.append(
            otypes.RegistrationAffinityLabelMapping(
                from_=otypes.AffinityLabel(
                    name=affinityLabelMapping['source_name'],
                ) if affinityLabelMapping['source_name'] else None,
                to=otypes.AffinityLabel(
                    name=affinityLabelMapping['dest_name'],
                ) if affinityLabelMapping['dest_name'] else None,
            )
        )
    return affinityLabelMappings


def _get_domain_mappings(module):
    domainMappings = list()

    for domainMapping in module.params['domain_mappings']:
        domainMappings.append(
            otypes.RegistrationDomainMapping(
                from_=otypes.Domain(
                    name=domainMapping['source_name'],
                ) if domainMapping['source_name'] else None,
                to=otypes.Domain(
                    name=domainMapping['dest_name'],
                ) if domainMapping['dest_name'] else None,
            )
        )
    return domainMappings


def _get_lun_mappings(module):
    lunMappings = list()
    for lunMapping in module.params['lun_mappings']:
        lunMappings.append(
            otypes.RegistrationLunMapping(
                from_=otypes.Disk(
                    lun_storage=otypes.HostStorage(
                        type=otypes.StorageType(lunMapping['source_storage_type'])
                        if (lunMapping['source_storage_type'] in
                            ['iscsi', 'fcp']) else None,
                        logical_units=[
                            otypes.LogicalUnit(
                                id=lunMapping['source_logical_unit_id'],
                            )
                        ],
                    ),
                ) if lunMapping['source_logical_unit_id'] else None,
                to=otypes.Disk(
                    lun_storage=otypes.HostStorage(
                        type=otypes.StorageType(lunMapping['dest_storage_type'])
                        if (lunMapping['dest_storage_type'] in
                            ['iscsi', 'fcp']) else None,
                        logical_units=[
                            otypes.LogicalUnit(
                                id=lunMapping.get('dest_logical_unit_id'),
                                port=lunMapping.get('dest_logical_unit_port'),
                                portal=lunMapping.get('dest_logical_unit_portal'),
                                address=lunMapping.get('dest_logical_unit_address'),
                                target=lunMapping.get('dest_logical_unit_target'),
                                password=lunMapping.get('dest_logical_unit_password'),
                                username=lunMapping.get('dest_logical_unit_username'),
                            )
                        ],
                    ),
                ) if lunMapping['dest_logical_unit_id'] else None,
            ),
        ),
    return lunMappings


def _get_cluster_mappings(module):
    clusterMappings = list()

    for clusterMapping in module.params['cluster_mappings']:
        clusterMappings.append(
            otypes.RegistrationClusterMapping(
                from_=otypes.Cluster(
                    name=clusterMapping['source_name'],
                ),
                to=otypes.Cluster(
                    name=clusterMapping['dest_name'],
                ) if clusterMapping['dest_name'] else None,
            )
        )
    return clusterMappings


def _get_vnic_profile_mappings(module):
    vnicProfileMappings = list()

    for vnicProfileMapping in module.params['vnic_profile_mappings']:
        vnicProfileMappings.append(
            otypes.VnicProfileMapping(
                source_network_name=vnicProfileMapping['source_network_name'],
                source_network_profile_name=vnicProfileMapping['source_profile_name'],
                target_vnic_profile=otypes.VnicProfile(
                    id=vnicProfileMapping['target_profile_id'],
                ) if vnicProfileMapping['target_profile_id'] else None,
            )
        )

    return vnicProfileMappings


def import_vm(module, connection):
    vms_service = connection.system_service().vms_service()
    if search_by_name(vms_service, module.params['name']) is not None:
        return False

    events_service = connection.system_service().events_service()
    last_event = events_service.list(max=1)[0]

    external_type = [
        tmp for tmp in ['kvm', 'xen', 'vmware']
        if module.params[tmp] is not None
    ][0]

    external_vm = module.params[external_type]
    imports_service = connection.system_service().external_vm_imports_service()
    imported_vm = imports_service.add(
        otypes.ExternalVmImport(
            vm=otypes.Vm(
                name=module.params['name']
            ),
            name=external_vm.get('name'),
            username=external_vm.get('username', 'test'),
            password=external_vm.get('password', 'test'),
            provider=otypes.ExternalVmProviderType(external_type),
            url=external_vm.get('url'),
            cluster=otypes.Cluster(
                name=module.params['cluster'],
            ) if module.params['cluster'] else None,
            storage_domain=otypes.StorageDomain(
                name=external_vm.get('storage_domain'),
            ) if external_vm.get('storage_domain') else None,
            sparse=external_vm.get('sparse', True),
            host=otypes.Host(
                name=module.params['host'],
            ) if module.params['host'] else None,
        )
    )

    # Wait until event with code 1152 for our VM don't appear:
    vms_service = connection.system_service().vms_service()
    wait(
        service=vms_service.vm_service(imported_vm.vm.id),
        condition=lambda vm: len(events_service.list(
            from_=int(last_event.id),
            search='type=1152 and vm.id=%s' % vm.id,
        )
        ) > 0 if vm is not None else False,
        fail_condition=lambda vm: vm is None,
        timeout=module.params['timeout'],
        poll_interval=module.params['poll_interval'],
    )
    return True


def control_state(vm, vms_service, module):
    if vm is None:
        return

    force = module.params['force']
    state = module.params['state']

    vm_service = vms_service.vm_service(vm.id)
    if vm.status == otypes.VmStatus.IMAGE_LOCKED:
        wait(
            service=vm_service,
            condition=lambda vm: vm.status == otypes.VmStatus.DOWN,
        )
    elif vm.status == otypes.VmStatus.SAVING_STATE:
        # Result state is SUSPENDED, we should wait to be suspended:
        wait(
            service=vm_service,
            condition=lambda vm: vm.status == otypes.VmStatus.SUSPENDED,
        )
    elif (
        vm.status == otypes.VmStatus.UNASSIGNED or
        vm.status == otypes.VmStatus.UNKNOWN
    ):
        # Invalid states:
        module.fail_json(msg="Not possible to control VM, if it's in '{0}' status".format(vm.status))
    elif vm.status == otypes.VmStatus.POWERING_DOWN:
        if (force and state == 'stopped') or state == 'absent':
            vm_service.stop()
            wait(
                service=vm_service,
                condition=lambda vm: vm.status == otypes.VmStatus.DOWN,
            )
        else:
            # If VM is powering down, wait to be DOWN or UP.
            # VM can end in UP state in case there is no GA
            # or ACPI on the VM or shutdown operation crashed:
            wait(
                service=vm_service,
                condition=lambda vm: vm.status in [otypes.VmStatus.DOWN, otypes.VmStatus.UP],
            )


def main():
    argument_spec = ovirt_full_argument_spec(
        state=dict(type='str', default='present', choices=[
            'absent', 'next_run', 'present', 'registered', 'running', 'stopped', 'suspended', 'exported', 'reboot'
        ]),
        name=dict(type='str'),
        id=dict(type='str'),
        cluster=dict(type='str'),
        allow_partial_import=dict(type='bool'),
        template=dict(type='str'),
        template_version=dict(type='int'),
        use_latest_template_version=dict(type='bool'),
        storage_domain=dict(type='str'),
        disk_format=dict(type='str', default='cow', choices=['cow', 'raw']),
        disks=dict(type='list', default=[], elements='dict'),
        memory=dict(type='str'),
        memory_guaranteed=dict(type='str'),
        memory_max=dict(type='str'),
        cpu_sockets=dict(type='int'),
        cpu_cores=dict(type='int'),
        cpu_shares=dict(type='int'),
        cpu_threads=dict(type='int'),
        type=dict(type='str', choices=['server', 'desktop', 'high_performance']),
        operating_system=dict(type='str'),
        cd_iso=dict(type='str'),
        boot_devices=dict(type='list', choices=['cdrom', 'hd', 'network'], elements='str'),
        vnic_profile_mappings=dict(default=[], type='list', elements='dict'),
        cluster_mappings=dict(default=[], type='list', elements='dict'),
        role_mappings=dict(default=[], type='list', elements='dict'),
        affinity_group_mappings=dict(default=[], type='list', elements='dict'),
        affinity_label_mappings=dict(default=[], type='list', elements='dict'),
        lun_mappings=dict(default=[], type='list', elements='dict'),
        domain_mappings=dict(default=[], type='list', elements='dict'),
        reassign_bad_macs=dict(default=None, type='bool'),
        boot_menu=dict(type='bool'),
        bios_type=dict(type='str', choices=['i440fx_sea_bios', 'q35_ovmf', 'q35_sea_bios', 'q35_secure_boot']),
        serial_console=dict(type='bool'),
        usb_support=dict(type='bool'),
        sso=dict(type='bool'),
        quota_id=dict(type='str'),
        high_availability=dict(type='bool'),
        high_availability_priority=dict(type='int'),
        lease=dict(type='str'),
        stateless=dict(type='bool'),
        delete_protected=dict(type='bool'),
        custom_emulated_machine=dict(type='str'),
        force=dict(type='bool', default=False),
        nics=dict(type='list', default=[], elements='dict'),
        cloud_init=dict(type='dict'),
        cloud_init_nics=dict(type='list', default=[], elements='dict'),
        cloud_init_persist=dict(type='bool', default=False, aliases=['sysprep_persist']),
        kernel_params_persist=dict(type='bool', default=False),
        sysprep=dict(type='dict'),
        host=dict(type='str'),
        clone=dict(type='bool', default=False),
        clone_permissions=dict(type='bool', default=False),
        kernel_path=dict(type='str'),
        initrd_path=dict(type='str'),
        kernel_params=dict(type='str'),
        instance_type=dict(type='str'),
        description=dict(type='str'),
        comment=dict(type='str'),
        timezone=dict(type='str'),
        serial_policy=dict(type='str', choices=['vm', 'host', 'custom']),
        serial_policy_value=dict(type='str'),
        vmware=dict(type='dict'),
        xen=dict(type='dict'),
        kvm=dict(type='dict'),
        cpu_mode=dict(type='str'),
        placement_policy=dict(type='str'),
        placement_policy_hosts=dict(type='list', elements='str'),
        custom_compatibility_version=dict(type='str'),
        ticket=dict(type='bool', default=None),
        cpu_pinning=dict(type='list', elements='dict'),
        soundcard_enabled=dict(type='bool', default=None),
        smartcard_enabled=dict(type='bool', default=None),
        io_threads=dict(type='int', default=None),
        ballooning_enabled=dict(type='bool', default=None),
        rng_device=dict(type='str'),
        numa_tune_mode=dict(type='str', choices=['interleave', 'preferred', 'strict']),
        numa_nodes=dict(type='list', default=[], elements='dict'),
        custom_properties=dict(type='list', elements='dict'),
        watchdog=dict(type='dict'),
        host_devices=dict(type='list', elements='dict'),
        graphical_console=dict(
            type='dict',
            options=dict(
                headless_mode=dict(type='bool'),
                protocol=dict(type='list', elements='str'),
                disconnect_action=dict(type='str'),
                keyboard_layout=dict(type='str'),
                monitors=dict(type='int'),
            )
        ),
        exclusive=dict(type='bool'),
        export_domain=dict(default=None),
        export_ova=dict(type='dict'),
        force_migrate=dict(type='bool'),
        migrate=dict(type='bool', default=None),
        next_run=dict(type='bool'),
        snapshot_name=dict(type='str'),
        snapshot_vm=dict(type='str'),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[['id', 'name']],
        required_if=[
            ('state', 'registered', ['storage_domain']),
        ],
        required_together=[['snapshot_name', 'snapshot_vm']]
    )

    check_sdk(module)
    check_params(module)

    try:
        state = module.params['state']
        auth = module.params.pop('auth')
        connection = create_connection(auth)
        vms_service = connection.system_service().vms_service()
        vms_module = VmsModule(
            connection=connection,
            module=module,
            service=vms_service,
        )
        vm = vms_module.search_entity(list_params={'all_content': True})

        control_state(vm, vms_service, module)
        if state in ('present', 'running', 'next_run'):
            if module.params['xen'] or module.params['kvm'] or module.params['vmware']:
                vms_module.changed = import_vm(module, connection)

            # Allow migrate vm when state present.
            # Migrate before update
            if vm:
                vms_module._migrate_vm(vm)

            # In case of wait=false and state=running, waits for VM to be created
            # In case VM don't exist, wait for VM DOWN state,
            # otherwise don't wait for any state, just update VM:
            ret = vms_module.create(
                entity=vm,
                result_state=otypes.VmStatus.DOWN if vm is None else None,
                update_params={'next_run': module.params['next_run']} if module.params['next_run'] is not None else None,
                clone=module.params['clone'],
                clone_permissions=module.params['clone_permissions'],
                _wait=True if not module.params['wait'] and state == 'running' else module.params['wait'],
            )
            # If VM is going to be created and check_mode is on, return now:
            if module.check_mode and ret.get('id') is None:
                module.exit_json(**ret)

            vms_module.post_present(ret['id'])
            # Run the VM if it was just created, else don't run it:
            if state == 'running':
                def kernel_persist_check():
                    return (module.params.get('kernel_params') or
                            module.params.get('initrd_path') or
                            module.params.get('kernel_path')
                            and not module.params.get('cloud_init_persist'))
                initialization = vms_module.get_initialization()
                ret = vms_module.action(
                    action='start',
                    post_action=vms_module._post_start_action,
                    action_condition=lambda vm: (
                        vm.status not in [
                            otypes.VmStatus.MIGRATING,
                            otypes.VmStatus.POWERING_UP,
                            otypes.VmStatus.REBOOT_IN_PROGRESS,
                            otypes.VmStatus.WAIT_FOR_LAUNCH,
                            otypes.VmStatus.UP,
                            otypes.VmStatus.RESTORING_STATE,
                        ]
                    ),
                    wait_condition=lambda vm: vm.status == otypes.VmStatus.UP,
                    # Start action kwargs:
                    use_cloud_init=True if not module.params.get('cloud_init_persist') and module.params.get('cloud_init') else None,
                    use_sysprep=True if not module.params.get('cloud_init_persist') and module.params.get('sysprep') else None,
                    vm=otypes.Vm(
                        placement_policy=otypes.VmPlacementPolicy(
                            hosts=[otypes.Host(name=module.params['host'])]
                        ) if module.params['host'] else None,
                        initialization=initialization,
                        os=otypes.OperatingSystem(
                            cmdline=module.params.get('kernel_params'),
                            initrd=module.params.get('initrd_path'),
                            kernel=module.params.get('kernel_path'),
                        ) if (kernel_persist_check()) else None,
                    ) if (
                        kernel_persist_check() or
                        module.params.get('host') or
                        initialization is not None
                        and not module.params.get('cloud_init_persist')
                    ) else None,
                )

                if module.params['ticket']:
                    vm_service = vms_service.vm_service(ret['id'])
                    graphics_consoles_service = vm_service.graphics_consoles_service()
                    graphics_console = graphics_consoles_service.list()[0]
                    console_service = graphics_consoles_service.console_service(graphics_console.id)
                    ticket = console_service.remote_viewer_connection_file()
                    if ticket:
                        ret['vm']['remote_vv_file'] = ticket

            if state == 'next_run':
                # Apply next run configuration, if needed:
                vm = vms_service.vm_service(ret['id']).get()
                if vm.next_run_configuration_exists:
                    ret = vms_module.action(
                        action='reboot',
                        entity=vm,
                        action_condition=lambda vm: vm.status == otypes.VmStatus.UP,
                        wait_condition=lambda vm: vm.status == otypes.VmStatus.UP,
                    )
            ret['changed'] = vms_module.changed
        elif state == 'stopped':
            if module.params['xen'] or module.params['kvm'] or module.params['vmware']:
                vms_module.changed = import_vm(module, connection)

            ret = vms_module.create(
                entity=vm,
                result_state=otypes.VmStatus.DOWN if vm is None else None,
                clone=module.params['clone'],
                clone_permissions=module.params['clone_permissions'],
            )
            if module.params['force']:
                ret = vms_module.action(
                    action='stop',
                    action_condition=lambda vm: vm.status != otypes.VmStatus.DOWN,
                    wait_condition=vms_module.wait_for_down,
                )
            else:
                ret = vms_module.action(
                    action='shutdown',
                    pre_action=vms_module._pre_shutdown_action,
                    action_condition=lambda vm: vm.status != otypes.VmStatus.DOWN,
                    wait_condition=vms_module.wait_for_down,
                )
            vms_module.post_present(ret['id'])
        elif state == 'suspended':
            ret = vms_module.create(
                entity=vm,
                result_state=otypes.VmStatus.DOWN if vm is None else None,
                clone=module.params['clone'],
                clone_permissions=module.params['clone_permissions'],
            )
            vms_module.post_present(ret['id'])
            ret = vms_module.action(
                action='suspend',
                pre_action=vms_module._pre_suspend_action,
                action_condition=lambda vm: vm.status != otypes.VmStatus.SUSPENDED,
                wait_condition=lambda vm: vm.status == otypes.VmStatus.SUSPENDED,
            )
        elif state == 'absent':
            ret = vms_module.remove()
        elif state == 'registered':
            storage_domains_service = connection.system_service().storage_domains_service()

            # Find the storage domain with unregistered VM:
            sd_id = get_id_by_name(storage_domains_service, module.params['storage_domain'])
            storage_domain_service = storage_domains_service.storage_domain_service(sd_id)
            vms_service = storage_domain_service.vms_service()

            # Find the unregistered VM we want to register:
            vms = vms_service.list(unregistered=True)
            vm = next(
                (vm for vm in vms if (vm.id == module.params['id'] or vm.name == module.params['name'])),
                None
            )
            changed = False
            if vm is None:
                vm = vms_module.search_entity()
                if vm is None:
                    raise ValueError(
                        "VM '%s(%s)' wasn't found." % (module.params['name'], module.params['id'])
                    )
            else:
                # Register the vm into the system:
                changed = True
                vm_service = vms_service.vm_service(vm.id)
                vm_service.register(
                    allow_partial_import=module.params['allow_partial_import'],
                    cluster=otypes.Cluster(
                        name=module.params['cluster']
                    ) if module.params['cluster'] else None,
                    vnic_profile_mappings=_get_vnic_profile_mappings(module)
                    if module.params['vnic_profile_mappings'] else None,
                    reassign_bad_macs=module.params['reassign_bad_macs']
                    if module.params['reassign_bad_macs'] is not None else None,
                    registration_configuration=otypes.RegistrationConfiguration(
                        cluster_mappings=_get_cluster_mappings(module),
                        role_mappings=_get_role_mappings(module),
                        domain_mappings=_get_domain_mappings(module),
                        lun_mappings=_get_lun_mappings(module),
                        affinity_group_mappings=_get_affinity_group_mappings(module),
                        affinity_label_mappings=_get_affinity_label_mappings(module),
                    ) if (module.params['cluster_mappings']
                          or module.params['role_mappings']
                          or module.params['domain_mappings']
                          or module.params['lun_mappings']
                          or module.params['affinity_group_mappings']
                          or module.params['affinity_label_mappings']) else None
                )

                if module.params['wait']:
                    vm = vms_module.wait_for_import()
                else:
                    # Fetch vm to initialize return.
                    vm = vm_service.get()
            ret = {
                'changed': changed,
                'id': vm.id,
                'vm': get_dict_of_struct(vm)
            }
        elif state == 'exported':
            if module.params['export_domain']:
                export_service = vms_module._get_export_domain_service()
                export_vm = search_by_attributes(export_service.vms_service(), id=vm.id)

                ret = vms_module.action(
                    entity=vm,
                    action='export',
                    action_condition=lambda t: export_vm is None or module.params['exclusive'],
                    wait_condition=lambda t: t is not None,
                    post_action=vms_module.post_export_action,
                    storage_domain=otypes.StorageDomain(id=export_service.get().id),
                    exclusive=module.params['exclusive'],
                )
            elif module.params['export_ova']:
                export_vm = module.params['export_ova']
                ret = vms_module.action(
                    entity=vm,
                    action='export_to_path_on_host',
                    host=otypes.Host(name=export_vm.get('host')),
                    directory=export_vm.get('directory'),
                    filename=export_vm.get('filename'),
                )
        elif state == 'reboot':
            ret = vms_module.action(
                action='reboot',
                entity=vm,
                action_condition=lambda vm: vm.status == otypes.VmStatus.UP,
                wait_condition=lambda vm: vm.status == otypes.VmStatus.UP,
            )

        module.exit_json(**ret)
    except Exception as e:
        module.fail_json(msg=str(e), exception=traceback.format_exc())
    finally:
        connection.close(logout=auth.get('token') is None)


if __name__ == "__main__":
    main()
