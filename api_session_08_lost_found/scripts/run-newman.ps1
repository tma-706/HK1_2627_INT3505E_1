$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot

try {
    New-Item -ItemType Directory -Path ".\reports" -Force | Out-Null

    $newmanCommand = Get-Command newman -ErrorAction SilentlyContinue
    if ($null -eq $newmanCommand) {
        $npmPrefix = (& npm config get prefix).Trim()
        $newmanCandidate = Join-Path $npmPrefix "newman.cmd"
        if (-not (Test-Path -LiteralPath $newmanCandidate)) {
            throw "Newman was not found. Install it with: npm install -g newman"
        }
        $newmanExecutable = $newmanCandidate
    }
    else {
        $newmanExecutable = $newmanCommand.Source
    }

    & $newmanExecutable run ".\postman\lost-found.postman_collection.json" `
        -e ".\postman\local.postman_environment.json" `
        -r "cli,junit" `
        --reporter-junit-export ".\reports\newman-junit.xml"

    if ($LASTEXITCODE -ne 0) {
        throw "Newman failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
