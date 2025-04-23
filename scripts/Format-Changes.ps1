<#.SYNOPSIS
Format changed files.#>
[CmdletBinding()]
Param(
    [string[]]$Paths = (
        ("{ ""Changes"": $Env:WATCHFILES_CHANGES }" | ConvertFrom-Json).Changes |
            ForEach-Object { $_[1] }
    )
)
if (!$Paths.Count) {
    Write-Verbose 'No changes to format'
    return
}
Write-Verbose 'START PROBLEM MATCHER'
$TemplateDir = Split-Path -Parent $Paths[0]
$TypesName = 'types.js'
$Types = "$TemplateDir/$TypesName"
$Types = if (Test-Path $Types) { Remove-Item $Types }
$Paths | Where-Object { (Split-Path -Leaf $_) -ne $TypesName } | ForEach-Object {
    $Content = (prettier $_) | Out-String
    $NewContent = $Content -Replace '(?m)^"use strict";[\r\n]+' -Replace '(?m)^Object\.defineProperty\(exports, "__esModule", \{ value: true \}\);[\r\n]+'
    if ($NewContent -ne $Content) { $NewContent | Out-File $_ -NoNewline }
}
Write-Verbose 'END PROBLEM MATCHER'
