<#.SYNOPSIS
Notes tools.#>

function Update-Libraries {
    <#.SYNOPSIS
    Update JSON libraries.#>
    Get-ChildItem -Filter '_zotero/library*.json' |
        Get-Content -Raw -Encoding 'utf-8' |
        ConvertFrom-Json |
        ConvertTo-Json -Depth 100 | # https://stackoverflow.com/q/53583677/20430423
        prettier --parser 'json' > '_zotero/libraries.json'
}

function Open-SharedItems {
    <#.SYNOPSIS
    Open files and supplemental directories associated with a shared identifier.#>

    Param (
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
    Copy files and supplemental directories associated with a shared identifier.#>

    Param (
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

function ConvertFrom-Obsidian {
    <#.SYNOPSIS
    Convert from an Obsidian literature review to a Word document.#>

    Param (
        # Microsoft Word template.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Template,
        # Markdown file to generate a literature review from.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Path
    )
    Begin {
        $Template = (Get-Item $Template) -Replace '\\', '/'
        $PandocArgs = @(
            # NB: Don't produce a document fragment.
            '--standalone'
            # NB: Avoid bookmark pollution around Markdown headers
            '--from', 'markdown-auto_identifiers'
            # NB: Keep the wrapping style of the input document
            '--wrap', 'preserve'
            # NB: The template to export literature reviews to
            '--reference-doc', "$((Get-Item $Template) -Replace '\\', '/')"
            '--filter', 'pandoc-crossref'
            # NB: Update periodically to https://retorque.re/zotero-better-bibtex/exporting/zotero.lua
            '--lua-filter', "$((Get-Item "$PSScriptRoot/zotero.lua") -Replace '\\', '/')"
            # NB: Style must also be installed in Zotero
            '--metadata', 'zotero_csl_style:international-journal-of-heat-and-mass-transfer'
        )
        $NoSq = '[^]]' # NB: Non-zero match without a closing bracket
        $NoPr = '[^)]' # NB: Non-zero match without a closing paren
        $MarkdownLink = "\[($NoSq+)\]\(($NoPr+)\)" # NB: To be converted to Pandoc style
        $PandocCitation = "@$NoSq+" # NB: Not including outer square brackets
        # NB: Also matches lists of citations
        $Citation = "(?:(?:$MarkdownLink|$PandocCitation);?\s?)"
        $CitationRef = "\{#c:\s?($Citation+)\}"
    }
    Process {
        $File = Get-Item $Path
        $Content = Get-Content $File -Raw
        $FrontMatter, $Content = ((Get-Content $File -Raw) -Split '---\n\n')
        $FrontMatter = "$FrontMatter---`n"
        # NB: Library 3 associated with nucleate pool boiling
        $Library = (
            $FrontMatter -Split '\n' -Match '^.*library:.+$'
        ) ? $null : '--metadata', 'zotero_library:3'
        # NB: Keep only the `## Review` section
        $ReviewHeading = '## Review\n'
        $NextHeading = '##\n'
        $Content = (($Content -Split $ReviewHeading)[1] -Split $NextHeading)[0]
        # NB: Remove callouts
        $Content = ($Content -Split '\n\n' | Select-String -Pattern '^[^>].+') -Join "`n`n"
        # NB: Find citations
        if (
            $CitationRefs = ($Content | Select-String -AllMatches -Pattern $CitationRef)
        ) {
            $CitationRefs.Matches | ForEach-Object {
                # NB: Replace inner semicolon-delimited citations for this citation
                $Citations = "[$($_.Groups[1].Value -Replace $MarkdownLink, '@$1')]"
                # NB: Replace this citation with Pandoc's citation syntax
                $Content = $Content -Replace [regex]::Escape($_.Value), $Citations
            }
        }
        # NB: Join frontmatter back into the content and convert with Pandoc
        $Output = "_exports/$($File.BaseName).docx"
        "$FrontMatter`n$Content" |
            pandoc @PandocArgs $Library --output $Output
        Invoke-Item $Output
    }
}

function Get-ObsidianUri {
    <#.SYNOPSIS
    Get URI to open Obsidian, optionally to a specific vault, file, and heading.#>
    Param ([string]$Vault, [string]$File, [string]$Heading)
    function escape { Param ($s)[uri]::EscapeDataString($s) }
    $v = ($Vault) ? "open?vault=$(escape($(Split-Path $Vault -Leaf)))" : ''
    $f = ($v -and $File) ? "&file=$(escape($File))" : ''
    $h = ($f -and $Heading) ? "%23$(escape($Heading))" : ''
    Set-Clipboard "obsidian://$v$f$h"
}

function Get-SourcesFromClipboard {
    <#.SYNOPSIS
    Open files and supplemental directories associated with citekeys from the clipboard.#>
    (Get-Clipboard) -Split ', ' | Open-SharedItems -Sources '_sources/zotero'
}

function Get-SourceFromObsidian {
    <#.SYNOPSIS
    Open files and supplemental directories associated with a citekey from Obsidian.#>
    Param (
        # A Better BiBTeX citekey, also encoded in the filename of shared resources.
        [Parameter(Mandatory, ValueFromPipeline)][string]$Citekey
    )
    Process { Open-SharedItems $Citekey '_sources/zotero' }
}

function ConvertTo-ReportObsidian {
    <#.SYNOPSIS
    Generate a report from an Obsidian note.#>

    Param (
        # Markdown file to generate a literature review from.
        [Parameter(Mandatory, ValueFromPipeline)]$Path
    )
    Process {
        $ConvertFromObsidianArgs = @{
            Template = "$PSScriptRoot/report.dotx"
            Path     = $Path
        }
        ConvertFrom-Obsidian @ConvertFromObsidianArgs
    }

}

function ConvertTo-ReviewObsidian {
    <#.SYNOPSIS
    Generate a literature review from an Obsidian note.#>
    Param (
        # Markdown file to generate a literature review from.
        [Parameter(Mandatory, ValueFromPipeline)]$Path
    )
    Process {
        $ConvertFromObsidianArgs = @{
            Template = "$PSScriptRoot/review.dotx"
            Path     = $Path
        }
        ConvertFrom-Obsidian @ConvertFromObsidianArgs
    }
}

function Copy-SourcesFromClipboard {
    <#.SYNOPSIS
    Copy files and supplemental directories associated with citekeys to exports.#>
    (Get-Clipboard) -Split ', ' | Copy-SharedItems -Sources '_sources/zotero'
}
