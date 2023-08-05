#!powershell

# Copyright: (c) 2017, Red Hat, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

#AnsibleRequires -CSharpUtil Ansible.Basic

Set-StrictMode -Version 2
$ConfirmPreference = "None"

$spec = @{
    options = @{
        database_path = @{ type = 'path' }
        dns_domain_name = @{ type = 'str' }
        domain_admin_password = @{ type = 'str'; required = $true; no_log = $true }
        domain_admin_user = @{ type = 'str'; required = $true }
        domain_log_path = @{ type = 'path' }  # TODO: Add alias for log_path once log_path has been deprecated.
        install_dns = @{ type = 'bool' }
        install_media_path = @{ type = 'path' }
        local_admin_password = @{ type = 'str'; no_log = $true }
        log_path = @{
            type = 'str'
            removed_at_date = [DateTime]::ParseExact("2022-07-01", "yyyy-MM-dd", $null)
            removed_from_collection = 'ansible.windows'
        }
        read_only = @{ type = 'bool'; default = $false }
        site_name = @{ type = 'str' }
        state = @{ type = 'str'; required = $true; choices = 'domain_controller', 'member_server' }
        sysvol_path = @{ type = 'path' }
        safe_mode_password = @{ type = 'str'; no_log = $true }
    }
    required_if = @(
        , @('state', 'domain_controller', @('dns_domain_name', 'safe_mode_password'))
        , @('state', 'member_server', @(, 'local_admin_password'))
    )
    supports_check_mode = $true
}
$module = [Ansible.Basic.AnsibleModule]::Create($args, $spec)

$database_path = $module.Params.database_path
$dns_domain_name = $module.Params.dns_domain_name
$domain_admin_password = $module.Params.domain_admin_password
$domain_admin_user = $module.Params.domain_admin_user
$domain_log_path = $module.Params.domain_log_path
$install_dns = $module.Params.install_dns
$install_media_path = $module.Params.install_media_path
$local_admin_password = $module.Params.local_admin_password
$read_only = $module.Params.read_only
$site_name = $module.Params.site_name
$state = $module.Params.state
$sysvol_path = $module.Params.sysvol_path
$safe_mode_password = $module.Params.safe_mode_password

# Used by Write-DebugLog - is deprecated.
Set-Variable -Name log_path -Scope Global -Value $module.Params.log_path

$module.Result.reboot_required = $false

# Set of features required for a domain controller
$dc_required_features = @("AD-Domain-Services", "RSAT-ADDS")

Function Write-DebugLog {
    Param(
        [string]$msg
    )

    $DebugPreference = "Continue"
    $ErrorActionPreference = "Continue"
    $date_str = Get-Date -Format u
    $msg = "$date_str $msg"

    Write-Debug $msg
    $log_path = Get-Variable -Name log_path -Scope Global -ValueOnly -ErrorAction SilentlyContinue
    if ($log_path) {
        Add-Content -LiteralPath $log_path -Value $msg
    }
}

Function Get-MissingFeature {
    Param(
        [string[]]$required_features
    )
    Write-DebugLog "Checking for missing Windows features..."

    $features = @(Get-WindowsFeature $required_features)
    # Check for $required_features that are not in $features
    $unavailable_features = @(Compare-Object -ReferenceObject $required_features -DifferenceObject ($features | Select-Object -ExpandProperty Name) -PassThru)

    if ($unavailable_features) {
        Throw "The following features required for a domain controller are unavailable: $($unavailable_features -join ',')"
    }

    $missing_features = @($features | Where-Object InstallState -ne Installed)

    return , $missing_features # comma needed to force array type output
}

Function Install-FeatureInstallation {
    Param(
        [string[]]$required_features,
        [Object]$module
    )
    # Ensure required features are installed

    Write-DebugLog "Ensuring required Windows features are installed..."
    $feature_result = Install-WindowsFeature $required_features
    $module.Result.reboot_required = $feature_result.RestartNeeded

    If (-not $feature_result.Success) {
        $module.FailJson("Error installing AD-Domain-Services, RSAT-ADDS, and RSAT-AD-AdminCenter features: {0}" -f ($feature_result | Out-String))
    }
}

# return the domain we're a DC for, or null if not a DC
Function Get-DomainControllerDomain {
    Write-DebugLog "Checking for domain controller role and domain name"

    $sys_cim = Get-CIMInstance Win32_ComputerSystem

    $is_dc = $sys_cim.DomainRole -in (4, 5) # backup/primary DC
    # this will be our workgroup or joined-domain if we're not a DC
    $domain = $sys_cim.Domain

    Switch ($is_dc) {
        $true { return $domain }
        Default { return $null }
    }
}

Function New-Credential {
    Param(
        [string] $cred_user,
        [string] $cred_password
    )

    $cred = New-Object System.Management.Automation.PSCredential($cred_user, $($cred_password | ConvertTo-SecureString -AsPlainText -Force))

    Return $cred
}

Function Get-OperationMasterRole {
    $assigned_roles = @((Get-ADDomainController -Server localhost).OperationMasterRoles)

    Return , $assigned_roles # no, the comma's not a typo- allows us to return an empty array
}

Try {
    # ensure target OS support; < 2012 doesn't have cmdlet support for DC promotion
    If (-not (Get-Command Install-WindowsFeature -ErrorAction SilentlyContinue)) {
        $module.FailJson("win_domain_controller requires at least Windows Server 2012")
    }

    # short-circuit "member server" check, since we don't need feature checks for this...

    $current_dc_domain = Get-DomainControllerDomain

    If ($state -eq "member_server" -and -not $current_dc_domain) {
        $module.ExitJson()
    }

    # all other operations will require the AD-DS and RSAT-ADDS features...

    $missing_features = Get-MissingFeature $dc_required_features

    If ($missing_features.Count -gt 0) {
        Write-DebugLog ("Missing Windows features ({0}), need to install" -f ($missing_features -join ", "))
        $module.Result.changed = $true # we need to install features
        If ($module.CheckMode) {
            # bail out here- we can't proceed without knowing the features are installed
            Write-DebugLog "check-mode, exiting early"
            $module.ExitJson()
        }

        Install-FeatureInstallation $dc_required_features $module | Out-Null
    }

    $domain_admin_cred = New-Credential -cred_user $domain_admin_user -cred_password $domain_admin_password

    switch ($state) {
        domain_controller {
            # ensure that domain admin user is in UPN or down-level domain format (prevent hang from https://support.microsoft.com/en-us/kb/2737935)
            If (-not $domain_admin_user.Contains("\") -and -not $domain_admin_user.Contains("@")) {
                $module.FailJson("domain_admin_user must be in domain\user or user@domain.com format")
            }

            If ($current_dc_domain) {
                # FUTURE: implement managed Remove/Add to change domains?

                If ($current_dc_domain -ne $dns_domain_name) {
                    $module.FailJson("$(hostname) is a domain controller for domain $current_dc_domain; changing DC domains is not implemented")
                }
            }

            # need to promote to DC
            If (-not $current_dc_domain) {
                Write-DebugLog "Not currently a domain controller; needs promotion"
                $module.Result.changed = $true
                If ($module.CheckMode) {
                    Write-DebugLog "check-mode, exiting early"
                    $module.ExitJson()
                }

                $module.Result.reboot_required = $true

                $safe_mode_secure = $safe_mode_password | ConvertTo-SecureString -AsPlainText -Force
                Write-DebugLog "Installing domain controller..."
                $install_params = @{
                    DomainName = $dns_domain_name
                    Credential = $domain_admin_cred
                    SafeModeAdministratorPassword = $safe_mode_secure
                }
                if ($database_path) {
                    $install_params.DatabasePath = $database_path
                }
                if ($domain_log_path) {
                    $install_params.LogPath = $domain_log_path
                }
                if ($sysvol_path) {
                    $install_params.SysvolPath = $sysvol_path
                }
                if ($install_media_path) {
                    $install_params.InstallationMediaPath = $install_media_path
                }
                if ($read_only) {
                    # while this is a switch value, if we set on $false site_name is required
                    # https://github.com/ansible/ansible/issues/35858
                    $install_params.ReadOnlyReplica = $true
                }
                if ($site_name) {
                    $install_params.SiteName = $site_name
                }
                if ($null -ne $install_dns) {
                    $install_params.InstallDns = $install_dns
                }
                try {
                    $null = Install-ADDSDomainController -NoRebootOnCompletion -Force @install_params
                }
                catch [Microsoft.DirectoryServices.Deployment.DCPromoExecutionException] {
                    # ExitCode 15 == 'Role change is in progress or this computer needs to be restarted.'
                    # DCPromo exit codes details can be found at
                    # https://docs.microsoft.com/en-us/windows-server/identity/ad-ds/deploy/troubleshooting-domain-controller-deployment
                    if ($_.Exception.ExitCode -eq 15) {
                        $module.Result.reboot_required = $true
                    }
                    else {
                        $module.FailJson("Failed to install ADDSDomainController with DCPromo: $($_.Exception.Message)", $_)
                    }
                }

                Write-DebugLog "Installation complete, trying to start the Netlogon service"
                # The Netlogon service is set to auto start but is not started. This is
                # required for Ansible to connect back to the host and reboot in a
                # later task. Even if this fails Ansible can still connect but only
                # with ansible_winrm_transport=basic so we just display a warning if
                # this fails.
                try {
                    Start-Service -Name Netlogon
                }
                catch {
                    Write-DebugLog "Failed to start the Netlogon service: $($_.Exception.Message)"
                    $msg = -join @(
                        "Failed to start the Netlogon service after promoting the host, Ansible may be unable to "
                        "connect until the host is manually rebooting: $($_.Exception.Message)"
                    )
                    $module.Warn($msg)
                }

                Write-DebugLog "Domain Controller setup completed, needs reboot..."
            }
        }
        member_server {
            # at this point we already know we're a DC and shouldn't be...
            Write-DebugLog "Need to uninstall domain controller..."
            $module.Result.changed = $true

            Write-DebugLog "Checking for operation master roles assigned to this DC..."

            $assigned_roles = Get-OperationMasterRole

            # FUTURE: figure out a sane way to hand off roles automatically (designated recipient server, randomly look one up?)
            If ($assigned_roles.Count -gt 0) {
                $msg = -join @(
                    "This domain controller has operation master role(s) ({0}) assigned; they must be moved to other "
                    "DCs before demotion (see Move-ADDirectoryServerOperationMasterRole)" -f ($assigned_roles -join ", ")
                )
                $module.FailJson($msg)
            }

            If ($module.CheckMode) {
                Write-DebugLog "check-mode, exiting early"
                $module.ExitJson()
            }

            $module.Result.reboot_required = $true

            $local_admin_secure = $local_admin_password | ConvertTo-SecureString -AsPlainText -Force

            Write-DebugLog "Uninstalling domain controller..."
            Uninstall-ADDSDomainController -NoRebootOnCompletion -LocalAdministratorPassword $local_admin_secure -Credential $domain_admin_cred
            Write-DebugLog "Uninstallation complete, needs reboot..."
        }
        default { throw ("invalid state {0}" -f $state) }
    }

    $module.ExitJson()
}
Catch {
    $excep = $_

    Write-DebugLog "Exception: $($excep | out-string)"

    Throw
}
