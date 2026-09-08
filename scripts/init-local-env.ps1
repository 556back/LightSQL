param(
    [string]$AdminEmail = 'admin@lightsql.example.com',
    [ValidateRange(1024, 65535)][int]$Port = 18000
)
$ErrorActionPreference = 'Stop'
if ($AdminEmail -notmatch '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$') {
    throw 'Please supply a valid administrator email address.'
}
$projectRoot = Split-Path -Parent $PSScriptRoot
$envDirectory = Join-Path $projectRoot '.local'
$envPath = Join-Path $envDirectory 'startup.env'
if (Test-Path -LiteralPath $envPath) {
    Write-Host "Existing configuration preserved: $envPath"
    exit 0
}
function New-RandomBytes {
    param([int]$Count)
    $bytes = New-Object byte[] $Count
    $generator = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    try { $generator.GetBytes($bytes) } finally { $generator.Dispose() }
    return ,$bytes
}
function New-HexSecret {
    return ([BitConverter]::ToString((New-RandomBytes 32))).Replace('-', '').ToLowerInvariant()
}
$encryptionKey = [Convert]::ToBase64String((New-RandomBytes 32)).Replace('+', '-').Replace('/', '_')
$lines = @(
    "LIGHTSQL_PORT=$Port",
    "FIRST_SUPERUSER=$AdminEmail",
    "FIRST_SUPERUSER_PASSWORD=$(New-HexSecret)",
    "POSTGRES_PASSWORD=$(New-HexSecret)",
    "SECRET_KEY=$(New-HexSecret)",
    "DATASOURCE_ENCRYPTION_KEY=$encryptionKey",
    'DATASOURCE_ALLOWED_HOSTS=[]',
    'MODEL_GATEWAY_ALLOWED_BASE_URLS=[]'
)
[IO.Directory]::CreateDirectory($envDirectory) | Out-Null
# CreateNew also protects against simultaneous initializations overwriting secrets.
$stream = [IO.File]::Open($envPath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write)
$writer = New-Object IO.StreamWriter($stream, (New-Object Text.UTF8Encoding($false)))
try { $writer.Write(($lines -join "`n") + "`n") } finally { $writer.Dispose() }
Write-Host "Created $envPath. Read the administrator password locally; keep this file private and backed up."
Write-Host "Open http://localhost:$Port after starting the services."
