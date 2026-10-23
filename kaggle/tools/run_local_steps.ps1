# run_local_steps.ps1 - kaggle400 desktop steps (owner-approved in chat, 2026-10-23).
#
# Run from anywhere (it moves to the project root itself):
#   powershell -ExecutionPolicy Bypass -File D:\sign_avatar_cse498r\kaggle\tools\run_local_steps.ps1
#
# What it does, in order (it STOPS at the first failure and never pushes to GitHub):
#   1. checks: project root, git, uv, free disk space; shows the git state
#   2. re-runs the 400-clip selection into a temp folder and checks it is identical (determinism)
#   3. copies the 400 videos into kaggle\data\train|val|test\videos and checks SHA-256 of every copy
#      (originals are only read; size + modification time compared before/after); writes SPLIT_LOCK.json
#   4. runs kaggle\src\verify_split.py --require-videos (all leakage / file checks)
#   5. runs all tests (uv run pytest)
#   6. makes ONE local git commit (no push) - videos, features, checkpoints, zips and credentials are refused
#   7. builds the upload zip for the PRIVATE Kaggle dataset from that clean commit and re-checks it
# Everything printed is also saved in kaggle\work\run_local_steps_<time>.log (gitignored).
# This file is plain ASCII on purpose (Windows PowerShell 5.1 reads files without a BOM as ANSI).

param([switch]$SkipPackage)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $root
New-Item -ItemType Directory -Force -Path (Join-Path $root "kaggle\work") | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$log = Join-Path $root "kaggle\work\run_local_steps_$stamp.log"
$results = New-Object System.Collections.ArrayList
$t0 = Get-Date

function Say([string]$text) {
    Write-Host $text
    Add-Content -Path $log -Value $text -Encoding UTF8
}

function Run-Native([string]$exe, [string[]]$argList) {
    # Runs a program, shows and logs every output line, returns its exit code.
    Say ("> " + $exe + " " + ($argList -join " "))
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    & $exe @argList 2>&1 | ForEach-Object {
        $line = "$_"
        Write-Host $line
        Add-Content -Path $log -Value $line -Encoding UTF8
    }
    $code = $LASTEXITCODE
    $ErrorActionPreference = $old
    return $code
}

function Record([string]$step, [bool]$ok, [string]$detail) {
    $null = $results.Add([pscustomobject]@{ Step = $step; Result = $(if ($ok) { "PASS" } else { "FAIL" }); Detail = $detail })
    Say ""
    Say ("==> " + $step + ": " + $(if ($ok) { "PASS" } else { "FAIL" }) + "  " + $detail)
    Say ""
}

function Finish([bool]$allOk) {
    $mins = [math]::Round(((Get-Date) - $t0).TotalMinutes, 1)
    Say "=================== RUN_LOCAL_STEPS SUMMARY ==================="
    foreach ($r in $results) { Say (("{0,-4}  {1,-34}  {2}" -f $r.Result, $r.Step, $r.Detail)) }
    Say ("Total time: " + $mins + " min.   Log file: " + $log)
    if ($allOk) {
        Say "ALL STEPS PASSED. Nothing was pushed to GitHub."
    } else {
        Say "STOPPED AT THE FIRST FAILURE (steps after it did not run). Nothing was pushed to GitHub."
    }
    Say "Please copy everything from 'RUN_LOCAL_STEPS SUMMARY' up (or the whole window) and paste it to Claude."
    Say "=============================================================="
    if ($allOk) { exit 0 } else { exit 1 }
}

Say ("run_local_steps.ps1 started " + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + " in " + $root)

# ---- Step 1: pre-checks -------------------------------------------------------------------------
Say "----- Step 1/7: pre-checks"
$py = Get-Content (Join-Path $root "pyproject.toml") -Raw
if ($py -notmatch 'name = "bdsl"') { Record "1 pre-checks" $false "not the project root (no bdsl pyproject.toml)"; Finish $false }
foreach ($tool in @("git", "uv")) {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { Record "1 pre-checks" $false "$tool not found on PATH"; Finish $false }
}
$drive = (Split-Path -Qualifier $root).TrimEnd(":")
$freeGB = [math]::Round((Get-PSDrive -Name $drive).Free / 1GB, 1)
Say ("Free space on " + $drive + ": " + $freeGB + " GB (needed: about 12 GB = 5.9 GB copies + 5.9 GB zip)")
$need = @("kaggle\data\subset_manifest.csv", "kaggle\data\train\train_manifest.csv", "kaggle\data\val\val_manifest.csv",
          "kaggle\data\test\test_manifest.csv", "kaggle\src\k400_run.py", "kaggle\src\verify_split.py",
          "work\manifests\manifest_v1.csv", "work\splits\S1_v0.csv", "dataset\initial_dataset\SIGN_LANGUAGE_DATA")
$missing = @($need | Where-Object { -not (Test-Path (Join-Path $root $_)) })
$null = Run-Native "git" @("--version")
$null = Run-Native "uv" @("--version")
$null = Run-Native "git" @("rev-parse", "--abbrev-ref", "HEAD")
$null = Run-Native "git" @("log", "--oneline", "-3")
Say "git status before this script (new kaggle files from Claude are expected here):"
$null = Run-Native "git" @("status", "--short")
if ($missing.Count -gt 0) { Record "1 pre-checks" $false ("missing: " + ($missing -join ", ")); Finish $false }
if ($freeGB -lt 13) { Record "1 pre-checks" $false ("only " + $freeGB + " GB free on " + $drive + ":"); Finish $false }
Record "1 pre-checks" $true ("git + uv found; " + $freeGB + " GB free")

# ---- Step 2: selection is deterministic ---------------------------------------------------------
Say "----- Step 2/7: re-run the selection and compare (about 1 minute)"
$c = Run-Native "uv" @("run", "python", "kaggle/src/k400_run.py", "select", "--check")
Record "2 selection reproducible" ($c -eq 0) "same 400 clips and manifests on this PC"
if ($c -ne 0) { Finish $false }

# ---- Step 3: copy + verify the 400 videos --------------------------------------------------------
Say "----- Step 3/7: copy the 400 videos and check SHA-256 (about 3-10 minutes, 5.9 GB)"
$c = Run-Native "uv" @("run", "python", "kaggle/src/k400_run.py", "copy-videos", "--confirm")
Record "3 copy 400 videos + SHA-256" ($c -eq 0) "kaggle\data\COPY_VERIFICATION.csv, SPLIT_LOCK.json"
if ($c -ne 0) { Finish $false }

# ---- Step 4: leakage + file checks ---------------------------------------------------------------
Say "----- Step 4/7: verify_split.py --require-videos (about 1-2 minutes)"
$c = Run-Native "uv" @("run", "python", "kaggle/src/verify_split.py", "--require-videos")
Record "4 verify_split (10 checks)" ($c -eq 0) "PASS/FAIL list above"
if ($c -ne 0) { Finish $false }

# ---- Step 5: all tests ---------------------------------------------------------------------------
Say "----- Step 5/7: all tests (about 1-2 minutes)"
$c = Run-Native "uv" @("run", "pytest", "-q")
Record "5 tests (uv run pytest)" ($c -eq 0) "see the 'passed' line above"
if ($c -ne 0) { Finish $false }

# ---- Step 6: one local commit, no push -----------------------------------------------------------
Say "----- Step 6/7: local git commit (NO push)"
$paths = @("src", "configs", "tests", "kaggle", "pyproject.toml", ".gitignore", "agent_docs", "CLAUDE.md",
           "dataset/initial_dataset/DATASET_WORK_LOG.md")
$small = @("kaggle/data/README_DATA.md", "kaggle/data/subset_manifest.csv", "kaggle/data/SPLIT_REPORT.md",
           "kaggle/data/SPLIT_SUMMARY.png", "kaggle/data/SPLIT_LOCK.json", "kaggle/data/SELECTION_META.json",
           "kaggle/data/COPY_VERIFICATION.csv", "kaggle/data/train/train_manifest.csv",
           "kaggle/data/val/val_manifest.csv", "kaggle/data/test/test_manifest.csv")
$c1 = Run-Native "git" @(@("add", "-A", "--") + $paths)
$c2 = Run-Native "git" @(@("add", "-f", "--") + $small)
$staged = @(& git diff --cached --name-only)
$bad = @($staged | Where-Object { $_ -match '\.(mp4|npz|pt|pth|ckpt|zip)$' -or $_ -match 'kaggle\.json' -or $_ -match '(^|/)work/' -or $_ -match '\.venv' })
if ($c1 -ne 0 -or $c2 -ne 0 -or $bad.Count -gt 0) {
    $null = Run-Native "git" @("reset", "-q")
    Record "6 local commit" $false ("refused, forbidden files staged: " + ($bad -join ", "))
    Finish $false
}
Say ("Files in this commit: " + $staged.Count)
foreach ($f in $staged) { Say ("   " + $f) }
if ($staged.Count -gt 0) {
    $c = Run-Native "git" @("commit", "-q", "-F", "kaggle/tools/commit_message.txt")
    if ($c -ne 0) { Record "6 local commit" $false "git commit failed"; Finish $false }
} else {
    Say "Nothing new to commit (already committed earlier)."
}
$null = Run-Native "git" @("log", "--oneline", "-2")
$dirty = @(& git status --porcelain -- src configs kaggle tests pyproject.toml uv.lock)
if ($dirty.Count -gt 0) {
    foreach ($f in $dirty) { Say ("   not committed: " + $f) }
    Record "6 local commit" $false "code paths still have uncommitted changes (the package needs a clean commit)"
    Finish $false
}
$commit = (& git rev-parse HEAD)
Record "6 local commit (no push)" $true ("commit " + $commit.Substring(0, 8) + "; code paths clean; NOT pushed")

# ---- Step 7: upload package ----------------------------------------------------------------------
if ($SkipPackage) {
    Record "7 upload package" $true "skipped (-SkipPackage)"
    Finish $true
}
Say "----- Step 7/7: build and re-check the upload zip (about 5-15 minutes)"
$c = Run-Native "uv" @("run", "python", "kaggle/src/k400_run.py", "package")
if ($c -ne 0) { Record "7 upload package" $false "package build failed"; Finish $false }
$zip = Get-ChildItem (Join-Path $root "kaggle\work\upload") -Filter "bdsl-k400-*.zip" | Sort-Object LastWriteTime | Select-Object -Last 1
$c = Run-Native "uv" @("run", "python", "kaggle/src/k400_run.py", "verify-package", $zip.FullName)
$sizeGB = [math]::Round($zip.Length / 1GB, 2)
Say ("Upload file: " + $zip.FullName)
Say ("Upload size: " + $sizeGB + " GB (" + $zip.Length + " bytes)")
Record "7 upload package + check" ($c -eq 0) ($zip.Name + ", " + $sizeGB + " GB")
Finish ($c -eq 0)
