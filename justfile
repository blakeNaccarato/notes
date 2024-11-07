set shell := ['pwsh', '-Command']
set dotenv-load

devpy := 'notes_dev'

dev:
  . ./dev.ps1

dvc-dag: dev
  (iuv dvc dag --md) -Replace 'mermaid', '{mermaid}' | Set-Content 'docs/_static/dag.md'
  markdownlint-cli2 'docs/_static/dag.md'

sync-contrib: dev
  iuv -Sync -Update

sync-local-dev-configs: dev
  {{devpy}} sync-local-dev-configs
