<#.SYNOPSIS
Update a pinned dependency to the latest commit pin.
#>

Param(
    # Dependency to update.
    [string]$Dependency,
)

git submodule update --init --remote --merge $Dependency
git add --all
git commit -m "Update $Dependency pinned commit"
git submodule deinit --force $Dependency
git add --all
git commit --amend --no-edit
