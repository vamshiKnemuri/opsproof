$ErrorActionPreference = "Stop"
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command py -ErrorAction SilentlyContinue }
if (-not $python) { throw "Install Python 3.10+ or add it to PATH." }
& $python.Source -m opsproof setup
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $python.Source -m opsproof demo --backend kind
exit $LASTEXITCODE
