<#.SYNOPSIS
Open files and supplemental directories associated with citekeys from the clipboard.
#>

begin {
    Push-Location "$PSSCriptRoot/.."
    . '.scripts/LiteratureCommon.ps1'
}
process {
    (Get-Clipboard) -Split ', ' | Open-SharedItems -Sources '_sources/zotero'
}
clean { Pop-Location }
