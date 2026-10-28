# Rebuild workspace-only skill discovery links after moving this directory.
$ErrorActionPreference = 'Stop'
$kdRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$kdSkillRoot = Join-Path $kdRoot 'skills'
$kdDiscovery = Join-Path $kdRoot '.agents\skills'
if (-not (Test-Path -LiteralPath (Join-Path $kdRoot 'source\README.md'))) {
    throw "Cannot locate KD knowledge base: $kdRoot"
}
New-Item -ItemType Directory -Path $kdDiscovery -Force | Out-Null
foreach ($kdSkill in Get-ChildItem -LiteralPath $kdSkillRoot -Directory) {
    if (-not (Test-Path -LiteralPath (Join-Path $kdSkill.FullName 'SKILL.md'))) { continue }
    $kdLinkPath = Join-Path $kdDiscovery $kdSkill.Name
    $kdExisting = Get-Item -LiteralPath $kdLinkPath -Force -ErrorAction SilentlyContinue
    if ($null -ne $kdExisting) {
        $kdExistingTarget = @($kdExisting.Target)
        if ($kdExisting.LinkType -eq 'Junction' -and $kdExistingTarget.Count -eq 1 -and
            [IO.Path]::GetFullPath($kdExistingTarget[0]) -eq $kdSkill.FullName) {
            Write-Output "OK: $($kdSkill.Name)"
            continue
        }
        # Never delete a directory or replace an unrelated link automatically.
        throw "Existing discovery path has a different target. Review it before replacing: $kdLinkPath"
    }
    New-Item -ItemType Junction -Path $kdLinkPath -Target $kdSkill.FullName | Out-Null
    Write-Output "Linked: $($kdSkill.Name)"
}
