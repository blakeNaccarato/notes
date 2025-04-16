set shell := ['pwsh', '-Command']
set dotenv-load

proj :=  '$Env:PATH = "$PWD;$PWD/scripts;$Env:PATH"; . dev.ps1; '
dev := proj + 'notes-dev'

default:
  {{proj}}

npm-build:
  npm run build

run-pytest:
  uv run watchfiles --ignore-permission-denied --filter python \
    'uv run pytest --instafail --testmon-forceselect --cov-append --cov-config pyproject.toml --cov-report xml --no-header --no-summary --disable-warnings --tb native --capture no --verbosity 3' \
    src tests
watch-templates:
  {{proj}} uv run watchfiles --ignore-permission-denied --grace-period 5 \
    'pwsh ./scripts/Format-Changes.ps1 -Verbose' \
    'data/local/vaults/personal/_Ω/scripts'
format-templates:
 {{proj}} scripts/Format-Changes.ps1 (Get-ChildItem 'data/local/vaults/personal/_Ω/scripts/*.js')

dvc-dag:
  {{proj}} (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'
sync-contrib:
  {{proj}} iuv -Sync -Update
sync-local-dev-configs:
  {{dev}} sync-local-dev-configs

vault :=  '$Env:PATH = "$(Get-Item ../../../..); $(Get-Item ../../../..)/scripts; $Env:PATH"; . dev.ps1; '
notes := vault + 'iuv -m notes' # ? Omit `;` allows `notes` module continuation w/ `.`
scripts := vault + '. notes.ps1;'

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
start-watch:
  {{scripts}} Start-PythonProcess watch-5b7151 notes.watch
