<#.SYNOPSIS
Common logic for literature scripts.
#>

function Update-Libraries {
    <#.SYNOPSIS
    Update JSON libraries.
    #>
    Get-ChildItem -Filter '_zotero/library*.json' |
        Get-Content -Raw -Encoding 'utf-8' |
        ConvertFrom-Json |
        ConvertTo-Json -Depth 100 | # https://stackoverflow.com/q/53583677/20430423
        prettier --parser 'json' > '_zotero/libraries.json'
}

function Open-SharedItems {
    <#.SYNOPSIS
    Open files and supplemental directories associated with a shared identifier.
    #>

    Param(
        # An identifier shared by multiple resources.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Identifier,

        # Path to the directory containing the source files.
        [Parameter(Mandatory)][string]$Sources
    )
    begin { Push-Location $Sources }
    process {
        Get-ChildItem "$Identifier.pdf" | Invoke-Item
        Get-ChildItem -Directory -Filter $Identifier | Invoke-Item
    }
    clean { Pop-Location }
}

function Copy-SharedItems {
    <#.SYNOPSIS
    Copy files and supplemental directories associated with a shared identifier.
    #>

    Param(
        # An identifier shared by multiple resources.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Identifier,

        # Path to the directory containing the source files.
        [Parameter(Mandatory)][string]$Sources
    )
    begin { Push-Location $Sources }
    process {
        $CopiesDir = '../_exports/copies'
        New-Item -ErrorAction SilentlyContinue -ItemType Directory -Path $CopiesDir
        Get-ChildItem "$Identifier.pdf" | Copy-Item -Destination $CopiesDir
        Get-ChildItem -Directory -Filter $Identifier |
            Copy-Item -Recurse -Destination "$CopiesDir/$Identifier"
    }
    clean { Pop-Location }
}
