<#.SYNOPSIS
Format template scripts.#>
param([Parameter(ValueFromPipeline)][string[]]$Path)
begin { . ./j.ps1 }
process {
    $Content = (prettier $Path) | Out-String
    $NewContent = $Content -replace
        '(?m)^"use strict";[\r\n]+' -replace
        '(?m)^Object\.defineProperty\(exports, "__esModule", \{ value: true \}\);[\r\n]+' -replace
        '(?m)^// @ts-nocheck[\r\n]+'
    if ($NewContent -ne $Content) { $NewContent | Out-File $_ -NoNewline }
}
