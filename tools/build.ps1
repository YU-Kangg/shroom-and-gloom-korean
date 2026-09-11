param([string]$BepInExRoot='', [switch]$Package)
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
if (!$BepInExRoot) { $BepInExRoot=Join-Path (Split-Path $root -Parent) 'BepInEx' }
$BepInExRoot=[IO.Path]::GetFullPath($BepInExRoot)
if (!(Test-Path "$BepInExRoot/interop/Unity.Localization.dll")) { throw 'Run BepInEx once in your owned game to generate current interop assemblies, then pass -BepInExRoot.' }
$python=Join-Path $root '.work/python/python.exe'
$dotnet=Join-Path $root '.work/dotnet/dotnet.exe'
if (!(Test-Path $python) -or !(Test-Path $dotnet)) { throw 'Run tools/bootstrap-tools.ps1 first.' }
$env:DOTNET_CLI_HOME=Join-Path $root '.work/dotnet-home'
$env:DOTNET_CLI_TELEMETRY_OPTOUT='1'
$env:NUGET_PACKAGES=Join-Path $root '.work/nuget'
& $python "$PSScriptRoot/build_catalog.py"
if ($LASTEXITCODE) { throw 'Translation validation failed' }
& $dotnet run --project "$PSScriptRoot/GrammarChecks"
if ($LASTEXITCODE) { throw 'Grammar tests failed' }
& $dotnet build "$root/src/ShroomKorean/ShroomKorean.csproj" -c Release "-p:BepInExRoot=$BepInExRoot"
if ($LASTEXITCODE) { throw 'Plugin build failed' }
if ($Package) {
 & $python "$PSScriptRoot/package_release.py"
 if ($LASTEXITCODE) { throw 'Package validation failed' }
}
