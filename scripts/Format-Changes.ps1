<#.SYNOPSIS
Format changed files.#>
[CmdletBinding()]
Param(
    [string[]]$Paths = (
        ("{ ""Changes"": $Env:WATCHFILES_CHANGES }" | ConvertFrom-Json).Changes |
            ForEach-Object { $_[1] }
    )
)
Write-Verbose 'START PROBLEM MATCHER'
$Paths | ForEach-Object {
    $Content = (prettier $_) | Out-String
    $NewContent = $Content -Replace '(?m)^"use strict";[\r\n]+' -Replace '(?m)^Object\.defineProperty\(exports, "__esModule", \{ value: true \}\);[\r\n]+'
    if ($NewContent -ne $Content) { $NewContent | Out-File $_ -NoNewline }
}
Remove-Item 'data/local/vaults/personal/_Ω/scripts/templater.js'
Write-Verbose 'END PROBLEM MATCHER'
