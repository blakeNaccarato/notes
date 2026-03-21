#* Settings
set unstable
set working-directory :=\
  '..'

#* Imports
import 'common.just'

#* Shells
set shell :=\
  ['pwsh', '-NonInteractive', '-NoProfile', '-CommandWithArgs']
set script-interpreter :=\
  ['pwsh', '-NonInteractive', '-NoProfile']

#* 📒 Notes

notes :=\
  uvr + sp + quote(env("PROJECT_NAME"))

notes_pre :=\
  pre

# 📒 [DEFAULT] Run notes preamble
[group('📒 Notes')]
default:
  {{notes_pre}} $Env:PATH

# 📒 Run NPM build
[group('📒 Notes')]
npm-build:
  npm run build

# 📒 Run pytest
[group('📒 Notes')]
run-pytest:
  uv run pytest -m 'not slow' --instafail --testmon-forceselect --cov-append --cov-config pyproject.toml --cov-report xml --no-header --no-summary --disable-warnings --tb native --capture no --verbosity 3

# 📒 Run tests when Python sources or tests change
[group('📒 Notes')]
watch-src-and-tests:
  uv run watchfiles --ignore-permission-denied --filter python \
    'pwsh {{j}} proj::run-pytest' 'src' 'tests'

# 📒 Format Typescript template sources
[group('📒 Notes')]
format-templates:
  {{format_templates}}

# 📒 Recompile TypeScript template sources when they change
[group('📒 Notes')]
watch-templates:
  Start-Sleep 5
  {{format_templates}}
  {{notes_pre}} uv run watchfiles --ignore-permission-denied --target-type 'command' \
    'pwsh ./scripts/Watch-TemplateScripts.ps1' '{{compiled_templates}}'

# 📒 Show the directed acyclic graph (DAG) of the DVC pipeline
[group('📒 Notes')]
dvc-dag:
  {{notes_pre}} (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'

compiled_templates :=\
  'data/local/vaults/personal/_templater-scripts'
format_templates :=\
  notes_pre + sp + '(' \
    + 'Get-ChildItem' \
    + sp + compiled_templates \
    + sp + '-Filter *.js' \
  + ')' \
  + sp + '|' + sp + './scripts/Format-TemplateScript.ps1'

#* 📒 Vault

vault_to_proj :=\
  '../../../../'
vault_pre :=\
  '.' + sp + vault_to_proj + '/j.ps1' + ';' + sp \
  + '.' + sp + vault_to_proj + '/scripts/notes.ps1'

# 📒 Test vault
[no-cd, script, group('📒 Vault')]
vault:
  {{vault_pre}}
  Start-PythonProcess watch-5b7151 notes.watch

# 📒 Copy URI
[no-cd, script, group('📒 Vault')]
copy-uri vault_path note_path selection:
  {{vault_pre}}
  Get-ObsidianUri {{vault_path}} {{note_path}} {{selection}}

# 📒 Generate report
[no-cd, script, group('📒 Vault')]
generate-report path:
  {{vault_pre}}
  ConvertTo-ReportObsidian {{path}}

# 📒 Generate review
[no-cd, script, group('📒 Vault')]
generate-review path:
  {{vault_pre}}
  ConvertTo-ReviewObsidian {{path}}

# 📒 Open source
[no-cd, script, group('📒 Vault')]
open-source title:
  {{vault_pre}}
  Get-SourceFromObsidian {{title}}

# 📒 Preview
[no-cd, script, group('📒 Vault')]
preview path:
  {{notes}}.preview {{path}}

# 📒 Start watch
[no-cd, script, group('📒 Vault')]
start-watch:
  {{vault_pre}}
  Start-PythonProcess watch-5b7151 notes.watch
