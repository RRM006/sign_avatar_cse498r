# Canonical k400 desktop validation. No copying, installing, downloading or git mutation.
# Run with -RunTests only when the owner is ready to execute the local test suite.
param([switch]$RunTests)
$ErrorActionPreference = 'Stop'
$projectFolder = [IO.DirectoryInfo]$PSScriptRoot
while (-not (Test-Path -LiteralPath (Join-Path $projectFolder.FullName 'pyproject.toml'))) {
    $projectFolder = $projectFolder.Parent
    if ($null -eq $projectFolder) { throw 'Cannot find project pyproject.toml' }
}
Set-Location -LiteralPath $projectFolder.FullName
$env:UV_NO_SYNC = '1'
$env:UV_OFFLINE = '1'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:PYTHONIOENCODING = 'utf-8'
$required = @(
    'versions/k400/data/SPLIT_LOCK.json',
    'versions/k400/processed/vocab/vocab_modelB_gloss_input.json',
    'versions/k400/outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/run.json',
    'versions/k400/outputs/runs/gloss2motion_gloss_kaggle400_20261023T135437Z/seed42/ckpt_best.pt',
    'shared/models/vrm/Base_Female.vrm'
)
foreach ($relativeFile in $required) {
    if (-not (Test-Path -LiteralPath (Join-Path $projectFolder.FullName $relativeFile) -PathType Leaf)) {
        throw "Required canonical file missing: $relativeFile"
    }
}
git status --short
if ($LASTEXITCODE -ne 0) { throw "Read-only git status failed" }
if ($RunTests) {
    uv run pytest -q
    if ($LASTEXITCODE -ne 0) { throw "Tests failed; save the full output" }
} else {
    Write-Host "Tests: not run. Pass -RunTests to execute them."
}
Write-Host "Model/demo commands: versions/RUN_AND_SHOW.md"
Write-Host "Historical final evaluation is locked. Do not rerun notebook 07."
