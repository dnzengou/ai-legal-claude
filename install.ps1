# =============================================================================
# AI Legal Assistant — Windows PowerShell Installer
# 14 Skills · 5 Agents · PDF Reports
# =============================================================================
#Requires -Version 5.1
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Colors via Write-Host
# ---------------------------------------------------------------------------
function Write-Header {
    Write-Host ""
    Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Blue
    Write-Host "║                                                              ║" -ForegroundColor Blue
    Write-Host "║   AI Legal Assistant — Claude Code Skills                    ║" -ForegroundColor Blue
    Write-Host "║   14 Skills · 5 Agents · PDF Reports                        ║" -ForegroundColor Blue
    Write-Host "║                                                              ║" -ForegroundColor Blue
    Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Blue
    Write-Host ""
}

function Write-OK   { param($msg) Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn { param($msg) Write-Host "  ⚠ $msg" -ForegroundColor Yellow }
function Write-Fail { param($msg) Write-Host "  ✗ $msg" -ForegroundColor Red }
function Write-Step { param($msg) Write-Host $msg -ForegroundColor Cyan }

# ---------------------------------------------------------------------------
# Resolve source directory
# ---------------------------------------------------------------------------
Write-Header

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ((Test-Path "$ScriptDir\skills") -and (Test-Path "$ScriptDir\agents")) {
    $SourceDir = $ScriptDir
    Write-Host "Installing from local directory: $SourceDir" -ForegroundColor Green
} else {
    Write-Fail "skills/ and agents/ directories not found next to install.ps1"
    Write-Host "Run this script from the ai-legal-claude root directory." -ForegroundColor Yellow
    exit 1
}

# ---------------------------------------------------------------------------
# Target directories (Windows Claude Code locations)
# ---------------------------------------------------------------------------
$ClaudeDir   = "$env:USERPROFILE\.claude"
$SkillsDir   = "$ClaudeDir\skills"
$AgentsDir   = "$ClaudeDir\agents"

# ---------------------------------------------------------------------------
# Prerequisites check
# ---------------------------------------------------------------------------
Write-Step "Checking prerequisites..."

if (Get-Command claude -ErrorAction SilentlyContinue) {
    Write-OK "Claude Code found"
} else {
    Write-Warn "Claude Code CLI not found (skills will still be installed)"
}

if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyver = (python --version 2>&1).ToString()
    Write-OK "Python found: $pyver"
    $hasPython = $true
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pyver = (python3 --version 2>&1).ToString()
    Write-OK "Python found: $pyver"
    $hasPython = $true
} else {
    Write-Warn "Python not found — PDF reports will not be available"
    $hasPython = $false
}

# ---------------------------------------------------------------------------
# Create directories
# ---------------------------------------------------------------------------
Write-Step "Creating directories..."

$Dirs = @(
    "$SkillsDir\legal\scripts",
    "$SkillsDir\legal\templates",
    $AgentsDir
)
foreach ($dir in $Dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-OK "Directories ready"

# ---------------------------------------------------------------------------
# Install main skill orchestrator
# ---------------------------------------------------------------------------
Write-Step "Installing skills..."
$InstallCount = 0

$OrchestratorSrc = "$SourceDir\legal\SKILL.md"
if (Test-Path $OrchestratorSrc) {
    Copy-Item $OrchestratorSrc "$SkillsDir\legal\SKILL.md" -Force
    Write-OK "legal (orchestrator)"
    $InstallCount++
} else {
    Write-Warn "legal/SKILL.md not found"
}

# ---------------------------------------------------------------------------
# Install 14 sub-skills
# ---------------------------------------------------------------------------
$Skills = @(
    'legal-review',
    'legal-risks',
    'legal-compare',
    'legal-plain',
    'legal-negotiate',
    'legal-missing',
    'legal-batch',
    'legal-nda',
    'legal-terms',
    'legal-privacy',
    'legal-agreement',
    'legal-compliance',
    'legal-freelancer',
    'legal-report-pdf'
)

foreach ($skill in $Skills) {
    $src = "$SourceDir\skills\$skill\SKILL.md"
    if (Test-Path $src) {
        $dest = "$SkillsDir\$skill"
        if (-not (Test-Path $dest)) {
            New-Item -ItemType Directory -Path $dest -Force | Out-Null
        }
        Copy-Item $src "$dest\SKILL.md" -Force
        Write-OK $skill
        $InstallCount++
    } else {
        Write-Warn "$skill (not found)"
    }
}

# ---------------------------------------------------------------------------
# Install 5 agents
# ---------------------------------------------------------------------------
Write-Step "Installing agents..."
$AgentCount = 0

$Agents = @(
    'legal-clauses',
    'legal-risks',
    'legal-compliance',
    'legal-terms',
    'legal-recommendations'
)

foreach ($agent in $Agents) {
    $src = "$SourceDir\agents\$agent.md"
    if (Test-Path $src) {
        Copy-Item $src "$AgentsDir\$agent.md" -Force
        Write-OK $agent
        $AgentCount++
    } else {
        Write-Warn "$agent (not found)"
    }
}

# ---------------------------------------------------------------------------
# Install scripts
# ---------------------------------------------------------------------------
Write-Step "Installing scripts..."
$ScriptCount = 0

$Scripts = Get-ChildItem "$SourceDir\scripts\*.py" -ErrorAction SilentlyContinue
foreach ($script in $Scripts) {
    Copy-Item $script.FullName "$SkillsDir\legal\scripts\$($script.Name)" -Force
    Write-OK $script.Name
    $ScriptCount++
}

# ---------------------------------------------------------------------------
# Install templates
# ---------------------------------------------------------------------------
Write-Step "Installing templates..."
$TemplateCount = 0

$Templates = Get-ChildItem "$SourceDir\templates\*.md" -ErrorAction SilentlyContinue
foreach ($tmpl in $Templates) {
    Copy-Item $tmpl.FullName "$SkillsDir\legal\templates\$($tmpl.Name)" -Force
    Write-OK $tmpl.Name
    $TemplateCount++
}

# ---------------------------------------------------------------------------
# Check reportlab
# ---------------------------------------------------------------------------
if ($hasPython) {
    Write-Step "Checking Python dependencies..."
    $hasReportlab = $false
    try {
        python -c "import reportlab" 2>$null
        $hasReportlab = $true
    } catch {}

    if (-not $hasReportlab) {
        try {
            python3 -c "import reportlab" 2>$null
            $hasReportlab = $true
        } catch {}
    }

    if ($hasReportlab) {
        Write-OK "reportlab installed"
    } else {
        Write-Warn "reportlab not installed"
        Write-Host "      Install with: pip install reportlab" -ForegroundColor Cyan
    }
}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Installation Complete!                                      ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "  Skills:    $InstallCount installed  →  $SkillsDir" -ForegroundColor Cyan
Write-Host "  Agents:    $AgentCount installed  →  $AgentsDir" -ForegroundColor Cyan
Write-Host "  Scripts:   $ScriptCount installed  →  $SkillsDir\legal\scripts" -ForegroundColor Cyan
Write-Host "  Templates: $TemplateCount installed  →  $SkillsDir\legal\templates" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command Reference:" -ForegroundColor Blue
Write-Host ""
Write-Host "  /legal review <file>          Full contract review (5 parallel agents)" -ForegroundColor Cyan
Write-Host "  /legal batch <f1> <f2> ...    Review multiple contracts at once" -ForegroundColor Cyan
Write-Host "  /legal risks <file>           Deep risk analysis" -ForegroundColor Cyan
Write-Host "  /legal compare <f1> <f2>      Side-by-side comparison" -ForegroundColor Cyan
Write-Host "  /legal plain <file>           Plain English translation" -ForegroundColor Cyan
Write-Host "  /legal negotiate <file>       Counter-proposal generator" -ForegroundColor Cyan
Write-Host "  /legal missing <file>         Missing protections finder" -ForegroundColor Cyan
Write-Host "  /legal nda <description>      Generate custom NDA" -ForegroundColor Cyan
Write-Host "  /legal terms <url>            Generate terms of service" -ForegroundColor Cyan
Write-Host "  /legal privacy <url>          Generate privacy policy" -ForegroundColor Cyan
Write-Host "  /legal agreement <type>       Generate business agreements" -ForegroundColor Cyan
Write-Host "  /legal freelancer <file>      Freelancer contract review" -ForegroundColor Cyan
Write-Host "  /legal compliance <url>       Compliance gap analysis" -ForegroundColor Cyan
Write-Host "  /legal report-pdf             Professional PDF report" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Tip: Start with /legal review <file> for a full contract analysis!" -ForegroundColor Yellow
Write-Host ""
