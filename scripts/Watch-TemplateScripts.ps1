<#.SYNOPSIS
Watch changed files.#>
. dev.ps1
$VerbosePreference = 'Continue'
Write-Verbose 'START PROBLEM MATCHER'
$TemplateDir = 'data/local/vaults/personal/_templater-scripts'
$TemplateTypes = 'types.js'
if (Test-Path ($Types = "$TemplateDir/$TemplateTypes")) {
    Remove-Item $Types
}
if (!$TemplateDir -or !$TemplateTypes) {
    Write-Debug 'Template directory or types environment variables not set'
    Write-Verbose 'STOP PROBLEM MATCHER'
    return
}
if (!$Env:WATCHFILES_CHANGES -or ($Env:WATCHFILES_CHANGES -eq '[]')) {
    Write-Debug 'No changes'
    Write-Verbose 'STOP PROBLEM MATCHER'
    return
}
$Paths = @(
    $Env:WATCHFILES_CHANGES | ConvertFrom-Json | ForEach-Object { $_[1] } |
        Where-Object { (Split-Path -Leaf $_) -ne $TemplateTypes }
)
if (!$Paths.Count) {
    Write-Debug 'No changes other than types'
    Write-Verbose 'STOP PROBLEM MATCHER'
    return
}
$Paths | Format-TemplateScript.ps1
Write-Debug 'Formatted template scripts'
Write-Verbose 'STOP PROBLEM MATCHER'
