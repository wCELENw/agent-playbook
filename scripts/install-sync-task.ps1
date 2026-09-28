# Registers (or re-registers) the scheduled task that runs sync_playbook.py daily at 09:00 and at logon.
# Idempotent, no admin rights. Run: powershell -ExecutionPolicy Bypass -File scripts\install-sync-task.ps1
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$py = (Get-Command pyw, py -ErrorAction SilentlyContinue | Select-Object -First 1).Source  # pyw: no console window
$user = [Security.Principal.WindowsIdentity]::GetCurrent().Name  # not USERDOMAIN: over SSH it is WORKGROUP

$action = New-ScheduledTaskAction -Execute $py -Argument "`"$repo\scripts\sync_playbook.py`"" -WorkingDirectory $repo
$triggers = @(
    (New-ScheduledTaskTrigger -Daily -At '09:00'),
    (New-ScheduledTaskTrigger -AtLogOn -User $user)
)
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -Hidden
$principal = New-ScheduledTaskPrincipal -UserId $user -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName 'agent-playbook-sync' -Action $action -Trigger $triggers `
    -Settings $settings -Principal $principal -Force | Out-Null
Get-ScheduledTask -TaskName 'agent-playbook-sync' | Select-Object TaskName, State, @{n='Action'; e={"$($_.Actions.Execute) $($_.Actions.Arguments)"}}
