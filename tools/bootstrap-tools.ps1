$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$work=Join-Path $root '.work'
New-Item -ItemType Directory -Force $work | Out-Null
$packages=@(
 @{Name='python';Url='https://www.python.org/ftp/python/3.12.10/python-3.12.10-embed-amd64.zip';Hash='4acbed6dd1c744b0376e3b1cf57ce906f9dc9e95e68824584c8099a63025a3c3'},
 @{Name='dotnet';Url='https://builds.dotnet.microsoft.com/dotnet/Sdk/8.0.425/dotnet-sdk-8.0.425-win-x64.zip';Hash='cd6eb1df826dd168108e2c427673f9d627b7e0631963eeedf0fa7aef0913c53f'},
 @{Name='bepinex-755';Url='https://builds.bepinex.dev/projects/bepinex_be/755/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.755%2B3fab71a.zip';Hash='3616d6a67f5f595973ec4aa7bd7edaf7f799d5bb9926f7146a6dcc7b4abf478f'}
)
foreach ($package in $packages) {
 $zip=Join-Path $work ($package.Name+'.zip')
 if (!(Test-Path -LiteralPath $zip)) { Invoke-WebRequest -UseBasicParsing $package.Url -OutFile $zip }
 if ((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash -ne $package.Hash) { throw "Checksum mismatch: $zip" }
 $dest=Join-Path $work $package.Name
 if (!(Test-Path -LiteralPath $dest)) { Expand-Archive -LiteralPath $zip -DestinationPath $dest }
}
Write-Output 'Pinned portable build tools are ready in .work. No game files were modified.'
