set shell := ['pwsh', '-Command']
set dotenv-load

proj :=  '$Env:PATH = "$PWD;$PWD/scripts;$Env:PATH"; . dev.ps1;'
dev := '{{proj}} notes-dev'

default:
  {{proj}}

dvc-dag:
  {{proj}} (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'
sync-contrib:
  {{proj}} iuv -Sync -Update
sync-local-dev-configs:
  {{dev}} sync-local-dev-configs

vault :=  '$Env:PATH = "$(Get-Item ../../../..);$(Get-Item ../../../..)/scripts; $Env:PATH"; . dev.ps1;'
notes := vault + ' iuv -m notes'
scripts := vault + ' notes.ps1;'

[no-cd]
copy-uri vault_path note_path selection:
  {{scripts}} Get-ObsidianUri {{vault_path}} {{note_path}} {{selection}}
[no-cd]
generate-report path:
  {{scripts}} ConvertTo-ReportObsidian {{path}}
[no-cd]
generate-review path:
  {{scripts}} ConvertTo-ReviewObsidian {{path}}
[no-cd]
open-source title:
  {{scripts}} Get-SourceFromObsidian {{title}}
[no-cd]
preview path:
  {{notes}}.preview {{path}}
[no-cd]
watch:
  {{notes}}.watch
