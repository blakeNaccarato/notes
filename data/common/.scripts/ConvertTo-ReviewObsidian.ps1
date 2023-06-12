<#.SYNOPSIS
Generate a literature review from an Obsidian note.
#>

Param(
    # Markdown file to generate a literature review from.
    [Parameter(Mandatory, ValueFromPipeline)]$MarkdownFile
)
begin {
    Push-Location "$PSSCriptRoot/.."
    . '.scripts/LiteratureCommon.ps1'
    $ConvertLinksReferenceStyle = @(
        '--to', 'markdown' # We won't know the content from the pipeline is Markdown
        '--reference-links' # Move links to the bottom of the document so the next step processes placeholders into live Zotero links
        '--wrap', 'preserve' # Keep the wrapping style of the input document
    )
    $DocxWithCitations = @(
        '--standalone' # Don't produce a document fragment.
        '--from', 'markdown-auto_identifiers' # Avoids bookmark pollution around Markdown headers
        '--reference-doc', 'G:/My Drive/Blake/School/Grad/Documents/Templates/Office Templates/AMSL Monthly.dotx' # The template to export literature reviews to
        # Lua filter and metadata passed to it
        '--lua-filter', '.scripts/zotero.lua' # Needs to be the one downloaded from the tutorial page https://retorque.re/zotero-better-bibtex/exporting/pandoc/#from-markdown-to-zotero-live-citations
        '--metadata', 'zotero_csl_style:.scripts/international-journal-of-heat-and-mass-transfer.csl' # Must also be installed in Zotero
        '--metadata', 'zotero_library:3' # Corresponds to "Nucleate pool boiling [3]"
    )
}
process {
    $MarkdownFile = Get-Item $MarkdownFile
    $MarkdownFile |
        Get-Content |
        & pandoc @ConvertLinksReferenceStyle |
        prettier --parser markdown |
        pandoc @DocxWithCitations --output "_exports/$($MarkdownFile.BaseName).docx"
}
clean { Pop-Location }
