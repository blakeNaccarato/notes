<#.SYNOPSIS
Format template scripts.#>
Param([Parameter(Mandatory, ValueFromPipeline)][string]$Path)
Begin { . dev.ps1 }
Process {
    $Content = (prettier $Path) | Out-String
    $NewContent = $Content -Replace '(?m)^"use strict";[\r\n]+' -Replace '(?m)^Object\.defineProperty\(exports, "__esModule", \{ value: true \}\);[\r\n]+'
    if ($NewContent -ne $Content) { $NewContent | Out-File $_ -NoNewline }
}
