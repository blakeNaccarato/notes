#Requires AutoHotkey v2.0

; Ctrl+Shift+V
^+v:: Run "wt pwsh ./Get-SourcesFromClipboard.ps1"

; Ctrl+Alt+Shift+V
^!+v:: Run "wt pwsh ./Copy-SourcesFromClipboard.ps1"
