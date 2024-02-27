<#.SYNOPSIS
Generate a data model for CSL JSON library export from Better BiBTeX.""".
#>

$CodegenProduceModel = @(
    '--collapse-root-models'
    '--encoding', 'utf-8'
    '--enum-field-as-literal', 'all'
    '--input-file-type', 'json'
    '--target-python-version', '3.11'
)
Get-Content '_zotero/libraries.json' |
    datamodel-codegen @CodegenProduceModel > '.scripts/_csl_models.py'
