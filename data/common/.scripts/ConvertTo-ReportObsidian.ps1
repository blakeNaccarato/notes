<#.SYNOPSIS
Generate a report from an Obsidian note.
#>

Param(
    # Markdown file to generate a report from.
    [Parameter(Mandatory, ValueFromPipeline)]$MarkdownFile
)
begin {
    Push-Location "$PSSCriptRoot/.."
    . '.scripts/LiteratureCommon.ps1'
    $ConvertMarkdown = @(
        '--to', 'markdown' # We won't know the content from the pipeline is Markdown
        '--wrap', 'preserve' # Keep the wrapping style of the input document
    )
    $ConvertDocx = @(
        '--standalone' # Don't produce a document fragment.
        '--from', 'markdown-auto_identifiers' # Avoids bookmark pollution around Markdown headers
        '--reference-doc', 'G:/My Drive/Blake/School/Grad/Documents/Templates/Office Templates/AMSL Monthly.dotx' # The template to export literature reviews to
    )
}
process {
    $MarkdownFile = Get-Item $MarkdownFile
    $MarkdownFile |
        Get-Content |
        & pandoc @ConvertMarkdown |
        prettier --parser markdown |
        pandoc @ConvertDocx --output "_exports/$($MarkdownFile.BaseName).docx"
}
