<#
  Cindy Zhu Reel Factory - one-command installer for Windows.

  The editor pastes ONE line into PowerShell and does nothing else:

    irm https://raw.githubusercontent.com/badtimingmediaco/CindyPipeline/main/install.ps1 | iex

  It installs git, Node, Python and ffmpeg (skipping whatever is already there), the
  Claude Code CLI, capcut-cli, the Python packages, the Poppins font, and the plugin
  itself - then runs setup. Safe to re-run; everything is checked before it is installed.

  Deliberately NOT interactive. An editor should be able to start this and walk away.
#>

$ErrorActionPreference = 'Stop'
$script:Failed = @()
$script:Did    = @()

function Say  ($m) { Write-Host $m }
function Step ($m) { Write-Host "`n=== $m" -ForegroundColor Cyan }
function Ok   ($m) { Write-Host "  [ok]   $m" -ForegroundColor Green;  $script:Did    += $m }
function Have ($m) { Write-Host "  [have] $m" -ForegroundColor DarkGray }
function Bad  ($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red;    $script:Failed += $m }
function Note ($m) { Write-Host "  [note] $m" -ForegroundColor Yellow }

# winget installs land on PATH only for NEW processes. Re-read both scopes from the
# registry so the rest of this script can use what it just installed, without the editor
# having to close and reopen the terminal (which is exactly the step people forget).
function Sync-Path {
    $m = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $u = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = ($m, $u | Where-Object { $_ }) -join ';'
}

function Has ($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# Run a native .exe and return its REAL exit code.
#
# Windows PowerShell 5.1 turns every stderr line from a native command into an
# ErrorRecord, so with $ErrorActionPreference='Stop' a mere warning becomes a thrown
# exception - pip printing "WARNING: Ignoring invalid distribution" made a successful
# install report as failed. Silence all streams, drop to Continue for the call, and judge
# the result by $LASTEXITCODE, which is the only honest signal here.
function Run ([scriptblock]$block) {
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        $global:LASTEXITCODE = 0
        & $block *> $null
        return $LASTEXITCODE
    } catch {
        return 1
    } finally {
        $ErrorActionPreference = $prev
    }
}

function Install-WithWinget ($id, $cmd, $label) {
    if (Has $cmd) { Have "$label already installed"; return $true }
    Say "  installing $label ... (this one can take a few minutes)"
    Run { winget install --id $id -e --accept-source-agreements --accept-package-agreements `
                         --disable-interactivity --scope user } | Out-Null
    Sync-Path
    if (Has $cmd) { Ok "$label installed"; return $true }
    # --scope user is rejected by some packages; retry letting winget choose.
    Run { winget install --id $id -e --accept-source-agreements --accept-package-agreements `
                         --disable-interactivity } | Out-Null
    Sync-Path
    if (Has $cmd) { Ok "$label installed"; return $true }
    Bad "$label could not be installed automatically"
    return $false
}

Say ""
Say "  CINDY ZHU REEL FACTORY - INSTALLER"
Say "  ==================================="
Say "  This installs everything needed to build reels on this machine."
Say "  It takes a few minutes and asks you nothing. Leave it running."
Say ""

# ---------------------------------------------------------------- 0. right machine?
Step "Checking this machine"

if ($env:OS -ne 'Windows_NT') { Bad "This installer is for Windows."; return }
Ok "Windows"

if (-not (Has 'winget')) {
    Bad "winget is missing - it ships with Windows 10 1809+ and Windows 11."
    Note "Update 'App Installer' from the Microsoft Store, then re-run this."
    return
}
Ok "winget available"

$capcut = Test-Path "$env:LOCALAPPDATA\CapCut\CapCut.exe"
if ($capcut) { Ok "CapCut desktop found" }
else {
    Note "CapCut desktop not found. Install it from capcut.com before building a reel."
    Note "Continuing - everything else can still be set up now."
}

# ---------------------------------------------------------------- 1. the toolchain
Step "Installing the toolchain (skipping anything already present)"

Install-WithWinget 'Git.Git'           'git'    'git'     | Out-Null
Install-WithWinget 'OpenJS.NodeJS.LTS' 'node'   'Node.js' | Out-Null
Install-WithWinget 'Gyan.FFmpeg'       'ffmpeg' 'ffmpeg'  | Out-Null

if (Has 'python') { Have "Python already installed" }
else {
    Install-WithWinget 'Python.Python.3.12' 'python' 'Python 3.12' | Out-Null
}

# ---------------------------------------------------------------- 2. packages
Step "Installing packages"

if (Has 'npm') {
    foreach ($pkg in @(@('capcut-cli','capcut'), @('@anthropic-ai/claude-code','claude'))) {
        if (Has $pkg[1]) { Have "$($pkg[0]) already installed" }
        else {
            Say "  installing $($pkg[0]) ..."
            Run { npm install -g $pkg[0] --silent } | Out-Null
            Sync-Path
            if (Has $pkg[1]) { Ok "$($pkg[0]) installed" } else { Bad "$($pkg[0]) failed" }
        }
    }
} else { Bad "npm unavailable - Node did not install, so capcut-cli and the Claude CLI cannot" }

if (Has 'python') {
    Say "  installing faster-whisper and pillow ... (the big one, be patient)"
    $rc = Run { python -m pip install --quiet faster-whisper pillow }
    # Verify by IMPORTING, not by trusting the exit code - a package can install and still
    # be unusable if its native deps did not land.
    $imp = Run { python -c "import faster_whisper, PIL" }
    if ($imp -eq 0) { Ok "faster-whisper + pillow installed and importable" }
    else { Bad "faster-whisper / pillow did not install (pip exit $rc)" }
} else { Bad "python unavailable - the pipeline scripts cannot run" }

# ---------------------------------------------------------------- 3. git over https
Step "Configuring git for plugin installs"

# Claude Code clones plugins over git@github.com: even for a PUBLIC repo. Without a
# GitHub SSH key that fails with "Host key verification failed" and the install dies.
# Rewriting to HTTPS needs no credentials at all and does not disturb repos already
# cloned over SSH.
if (Has 'git') {
    $existing = ''
    if ((Run { git config --global --get 'url.https://github.com/.insteadOf' }) -eq 0) {
        $ErrorActionPreference = 'Continue'
        $existing = (git config --global --get 'url.https://github.com/.insteadOf')
        $ErrorActionPreference = 'Stop'
    }
    if ($existing) { Have "https rewrite already set" }
    else {
        Run { git config --global 'url.https://github.com/.insteadOf' 'git@github.com:' } | Out-Null
        Ok "git will use HTTPS for github.com"
    }
} else { Bad "git unavailable" }

# ---------------------------------------------------------------- 4. the plugin
Step "Installing the Reel Factory plugin"

if (Has 'claude') {
    Run { claude plugin marketplace add badtimingmediaco/CindyPipeline } | Out-Null
    # Refresh the marketplace, then install AND update.
    #
    # 'plugin install' is a no-op when the plugin is already present, so re-running this
    # installer would never pick up a new version - an editor would sit on whatever they
    # first installed forever. 'marketplace update' re-reads the repo and 'plugin update'
    # (which needs the FULLY QUALIFIED name@marketplace - the bare name reports "not
    # found") pulls the new version. Running both makes this line work for a first install
    # and for an upgrade, which is what people will actually paste.
    Run { claude plugin marketplace update cindy-reel-factory } | Out-Null
    Run { claude plugin install reel-factory@cindy-reel-factory } | Out-Null
    Run { claude plugin update  reel-factory@cindy-reel-factory } | Out-Null
    Ok "marketplace added and plugin up to date"
} else { Bad "the claude CLI is not available, so the plugin cannot be installed" }

# Newest cached version wins - an upgrade leaves the old version dir in place beside it.
$script:PluginDir = Get-ChildItem "$env:USERPROFILE\.claude\plugins\cache\cindy-reel-factory\reel-factory" `
                      -Directory -ErrorAction SilentlyContinue |
                    Sort-Object { try { [version]$_.Name } catch { [version]'0.0.0' } } |
                    Select-Object -Last 1
if ($script:PluginDir) { Ok "plugin v$($script:PluginDir.Name) ready" }
else { Bad "plugin install failed - nothing in the plugin cache" }

# ---------------------------------------------------------------- 5. fonts
Step "Installing fonts"

# Poppins is OFL-licensed, so it ships with the kit and installs per-user: copy the file
# and register it under HKCU. No admin rights needed, and it is exactly where the doctor
# looks. MADE Awelier is licensed personal-use and is NOT redistributed - see below.
$fontSrc = $null
if ($script:PluginDir) { $fontSrc = Join-Path $script:PluginDir.FullName 'kit\fonts' }

if ($fontSrc -and (Test-Path $fontSrc)) {
    $dst = "$env:LOCALAPPDATA\Microsoft\Windows\Fonts"
    New-Item -ItemType Directory -Force $dst | Out-Null
    $key = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
    $n = 0
    foreach ($f in Get-ChildItem $fontSrc -Include *.ttf, *.otf -Recurse) {
        $target = Join-Path $dst $f.Name
        if (-not (Test-Path $target)) { Copy-Item $f.FullName $target }
        $name = "$($f.BaseName) (TrueType)"
        if (-not (Get-ItemProperty -Path $key -Name $name -ErrorAction SilentlyContinue)) {
            New-ItemProperty -Path $key -Name $name -Value $target -PropertyType String -Force | Out-Null
        }
        $n++
    }
    if ($n) { Ok "$n font file(s) registered (Poppins)" }
} else { Note "Poppins not found in the kit - install it from Google Fonts if setup flags it" }

$awelier = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\Windows\Fonts", "$env:WINDIR\Fonts" `
             -Filter '*welier*' -ErrorAction SilentlyContinue | Select-Object -First 1
if ($awelier) { Ok "MADE Awelier already installed" }
else {
    Note "MADE Awelier is NOT installed, and cannot be shipped here (personal-use licence)."
    Note "Download it, right-click the .ttf files and choose Install. Its family name must"
    Note "read 'MADE Awelier PERSONAL USE' - that is the exact name CapCut needs."
}

# ---------------------------------------------------------------- done
Say ""
Say "  ==================================="
if ($script:Failed.Count) {
    Write-Host "  FINISHED WITH $($script:Failed.Count) PROBLEM(S)" -ForegroundColor Red
    foreach ($f in $script:Failed) { Write-Host "    - $f" -ForegroundColor Red }
    Say ""
    Say "  Close this window, open a NEW PowerShell, and run this installer again -"
    Say "  most failures here are just PATH not having caught up yet."
} else {
    Write-Host "  ALL DONE" -ForegroundColor Green
}
Say ""
Say "  NEXT - two things, in this order:"
Say ""
Say "    1. Open a NEW terminal and run:   claude"
Say "       Then type:                     /reel-factory:reel-setup"
Say ""
Say "       That builds your pipeline folder, finds your CapCut drafts folder and"
Say "       places the house template. It will tell you if anything is still missing."
Say ""
Say "    2. Open CZ_TEMPLATE in CapCut once, while online."
Say "       CapCut downloads its own fonts and the torn-paper effect at that moment."
Say "       Nobody can automate this part. Then close CapCut."
Say ""
Say "  Then drop a video in 01_intake and tell Claude:  run it <name>"
Say ""
