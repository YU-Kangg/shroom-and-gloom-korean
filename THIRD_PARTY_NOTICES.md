# Third-party notices and source

The game is not included. Library binaries are unmodified files from the official
[BepInEx Unity IL2CPP x64 build 755](https://builds.bepinex.dev/projects/bepinex_be/755/BepInEx-Unity.IL2CPP-win-x64-6.0.0-be.755%2B3fab71a.zip).
The loader ZIP SHA-256 is `3616d6a67f5f595973ec4aa7bd7edaf7f799d5bb9926f7146a6dcc7b4abf478f`.

| Component | License / source |
|---|---|
| BepInEx 6.0.0-be.755 | LGPL 2.1; [source commit](https://github.com/BepInEx/BepInEx/tree/3fab71a1914132a1ce3a545caf3192da603f2258) |
| UnityDoorstop 4.5.0 | LGPL 2.1; [source](https://github.com/NeighTools/UnityDoorstop/tree/v4.5.0) |
| Il2CppInterop 1.5.1-ci.829 | LGPL 3; [source commit](https://github.com/BepInEx/Il2CppInterop/tree/6d9007c18cc8440830379c5e1d5714085e7ec577) |
| .NET runtime 6.0.7 | MIT and third-party notices; [source](https://github.com/dotnet/runtime/tree/v6.0.7) |
| Jua | SIL OFL 1.1; [font source and credits](https://github.com/google/fonts/tree/main/ofl/jua) |
| Noto Sans KR | SIL OFL 1.1; [font source and credits](https://github.com/google/fonts/tree/main/ofl/notosanskr) |
| Demo Korean translations / TMP serialization template | CC BY-NC-SA 4.0; [oatone-textcat and contributors](https://github.com/oatone-textcat/shroom-and-gloom-demo-korean/tree/5f5e1001d9ed34c43334ea5bf97c847db2246e5b) |

Full library license texts, copyright holders, source revisions and checksums are
recorded in `licenses/` and `licenses/dependencies.json`. This covers HarmonyX,
AsmResolver, AssetRipper.CIL, AssetRipper.Primitives, Cpp2IL/LibCpp2IL/StableNameDotNet/
WasmDisassembler, Disarm, Capstone.NET, Capstone, Iced, Mono.Cecil, MonoMod,
SemanticVersioning and Dobby. Dobby's native binary does not expose a source revision;
its unmodified binary comes from the pinned official loader package.

The install ZIP includes matching BepInEx, Doorstop and Il2CppInterop source archives
under `ShroomKorean-docs/third-party-sources/`. Their library files can be replaced
by locally rebuilt versions. This patch imposes no additional restrictions on
modification or reverse engineering needed to debug modifications to those libraries.
Third-party sources are separate from the noncommercial translation material.

The font atlas and glyph data were rebuilt from the included OFL fonts. The original
font's glyphs and atlas from the demo patch were replaced. Its serialization template
remains credited under CC BY-NC-SA 4.0. The original game's Latin fonts are not distributed.
