<#.SYNOPSIS
Copy files and supplemental directories associated with citekeys to exports.
#>

begin {
    Push-Location "$PSSCriptRoot/.."
    . '.scripts/LiteratureCommon.ps1'
}
process {
    (Get-Clipboard) -Split ', ' | Copy-SharedItems -Sources '_sources/zotero'
}
clean { Pop-Location }
