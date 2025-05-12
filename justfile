set dotenv-load

set shell :=\
  ['pwsh', '-NonInteractive', '-NoProfile', '-CommandWithArgs']

sp :=\
  ' '
proj :=\
  '$Env:PATH = "$PWD;$PWD/scripts;$Env:PATH"; . dev.ps1;'
dev :=\
  proj + sp + 'notes-dev'

compiled_templates :=\
  'data/local/vaults/personal/__Ω'
format_templates :=\
  proj + sp + '(' + 'Get-ChildItem' + sp + compiled_templates + sp + '-Filter *.js' + ')' \
  + sp + '|' + sp + 'Format-TemplateScript.ps1'

default:
  {{proj}}

npm-build:
  npm run build

run-pytest:
  uv run watchfiles --ignore-permission-denied --filter python \
    'uv run pytest --instafail --testmon-forceselect --cov-append --cov-config pyproject.toml --cov-report xml --no-header --no-summary --disable-warnings --tb native --capture no --verbosity 3' \
    src tests
format-templates:
  {{format_templates}}
watch-templates:
  Start-Sleep 5
  {{format_templates}}
  {{proj}} uv run watchfiles --ignore-permission-denied --target-type 'command' \
    'pwsh ./scripts/Watch-TemplateScripts.ps1' '{{compiled_templates}}'

dvc-dag:
  {{proj}} (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'
sync-contrib:
  {{proj}} iuv -Sync
sync-local-dev-configs:
  {{dev}} sync-local-dev-configs

vault :=\
  '. dev.ps1;'
notes :=\
  vault + sp + 'iuv -m notes' # ? Omit `;` allows `notes` module continuation w/ `.`
scripts :=\
  vault + sp + '. notes.ps1;'

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
