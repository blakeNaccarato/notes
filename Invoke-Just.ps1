<#.SYNOPSIS
Invoke `just`.#>
[CmdletBinding(PositionalBinding = $False)]
Param(
    [switch]$Sync,
    [switch]$Update,
    [switch]$Low,
    [switch]$High,
    [switch]$Build,
    [switch]$Force,
    [switch]$CI,
    [switch]$Locked,
    [switch]$Devcontainer,
    [string]$PythonVersion = (Test-Path '.python-version') ? (Get-Content '.python-version') : '3.11',
    [string]$PylanceVersion = (Test-Path '.pylance-version') ? (Get-Content '.pylance-version') : '2024.6.1',
    [Parameter(ValueFromPipeline, ValueFromRemainingArguments)][string[]]$Run
)
Begin {
    . $PSScriptRoot/dev.ps1

    $CI = (New-Switch $Env:SYNC_ENV_DISABLE_CI (New-Switch $Env:CI))
    $Locked = New-Switch $CI $Locked
    $InvokeUvArgs = @{
        Sync           = $Sync
        Update         = $Update
        Low            = $Low
        High           = $High
        Build          = $Build
        Force          = $Force
        CI             = $CI
        Locked         = $Locked
        Devcontainer   = (New-Switch $Env:SYNC_ENV_DISABLE_DEVCONTAINER (New-Switch $Env:DEVCONTAINER))
        PythonVersion  = $PythonVersion
        PylanceVersion = $PylanceVersion
    }
}
Process { Invoke-Just @InvokeUvArgs @Run }
