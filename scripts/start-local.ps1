param(
    [ValidateSet('start', 'stop', 'restart', 'status', 'logs', 'reset-admin')]
    [string]$Action = 'start',
    [string]$ProjectName,
    [switch]$ResetData,
    [switch]$NoBuild
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$configPath = Join-Path $projectRoot '.local\startup.env'
$composePath = Join-Path $projectRoot 'compose.local.yml'

if (-not $ProjectName) {
    $ProjectName = 'lightsql-local'
    if (Test-Path -LiteralPath $configPath) {
        $projectLine = Select-String -Path $configPath -Pattern '^LIGHTSQL_PROJECT_NAME=(.+)$' | Select-Object -First 1
        if ($projectLine) { $ProjectName = $projectLine.Matches[0].Groups[1].Value }
    }
}

function Invoke-Compose {
    param([string[]]$Arguments)
    & docker compose -p $ProjectName --env-file $configPath -f $composePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Docker Compose failed with exit code $LASTEXITCODE. See the command output above."
    }
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw 'Docker was not found. Install Docker Desktop, start the Linux engine, and run this script again.'
}

if (-not (Test-Path -LiteralPath $configPath)) {
    Write-Host 'No local configuration found. Creating .local\startup.env with random secrets.'
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot 'init-local-env.ps1') -ProjectName $ProjectName
    if ($LASTEXITCODE -ne 0) { throw 'Could not create .local\startup.env.' }
}

if ($Action -eq 'status') {
    Invoke-Compose @('ps', '-a')
    exit 0
}

if ($Action -eq 'logs') {
    Invoke-Compose @('logs', '--tail', '100', 'backend', 'catalog-worker', 'query-worker', 'integration-worker')
    exit 0
}

if ($Action -eq 'reset-admin') {
    Invoke-Compose @('up', '-d', '--wait', '--wait-timeout', '180', 'db', 'backend')
    Invoke-Compose @('run', '--rm', '--no-deps', '-e', 'RESET_FIRST_SUPERUSER_PASSWORD=true', 'backend', 'python', 'app/initial_data.py')
    Write-Host 'Administrator password reset from FIRST_SUPERUSER_PASSWORD in .local\startup.env.'
    exit 0
}

if ($Action -eq 'stop') {
    Invoke-Compose @('stop')
    Write-Host 'LightSQL stopped. Database data and configuration were kept.'
    exit 0
}

if ($Action -eq 'restart') {
    Invoke-Compose @('stop')
}

if ($ResetData) {
    Write-Warning "Removing the $ProjectName containers and metadata volume. This deletes local LightSQL users, topics, and settings."
    Invoke-Compose @('down', '--volumes', '--remove-orphans')
}

Invoke-Compose @('config', '--quiet')
$upArguments = @('up', '-d', '--wait', '--wait-timeout', '180')
if (-not $NoBuild) { $upArguments += '--build' }
try {
    Invoke-Compose $upArguments
} catch {
    Write-Error $_
    Write-Host ''
    Write-Host 'If this is an old local database whose password is unknown, run:'
    Write-Host ".\scripts\start-local.ps1 -ResetData"
    throw
}

$port = 18000
$portLine = Select-String -Path $configPath -Pattern '^LIGHTSQL_PORT=(.+)$' | Select-Object -First 1
if ($portLine) { $port = [int]$portLine.Matches[0].Groups[1].Value }
$healthUrl = "http://127.0.0.1:$port/api/v1/utils/health-check/"
try {
    $health = Invoke-RestMethod -Uri $healthUrl -TimeoutSec 15
    Write-Host "LightSQL is ready: http://localhost:$port"
    Write-Host "Health check: $healthUrl => $health"
    Write-Host "Administrator and all local passwords are configured in .local\startup.env"
} catch {
    Write-Warning "Containers started, but the health check is not ready yet: $healthUrl"
    Write-Host "Inspect logs with: .\scripts\start-local.ps1 -Action logs"
}
