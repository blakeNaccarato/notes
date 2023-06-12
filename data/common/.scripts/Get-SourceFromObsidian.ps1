<#.SYNOPSIS
Open files and supplemental directories associated with a citekey from Obsidian.
#>

Param(
    # A Better BiBTeX citekey, also encoded in the filename of shared resources.
    [Parameter(Mandatory, ValueFromPipeline)][string]$Citekey
)
begin {
    Push-Location "$PSSCriptRoot/.."
    . '.scripts/LiteratureCommon.ps1'
}
process { Open-SharedItems $Citekey '_sources' }
clean { Pop-Location }
