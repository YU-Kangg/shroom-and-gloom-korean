"""Create install/source ZIPs from explicit allowlists, never from the game tree."""
from pathlib import Path,PurePosixPath
import hashlib,json,sys,zipfile,urllib.request
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_catalog
VERSION='v0.1.0-beta.1'
LOADER_HASH='3616d6a67f5f595973ec4aa7bd7edaf7f799d5bb9926f7146a6dcc7b4abf478f'
DOCS=['README.md','BUILDING.md','GLOSSARY.md','TESTING.md','RELEASE_NOTES.md','THIRD_PARTY_NOTICES.md','LICENSE']
SOURCE_DIRS=['src','translations','assets','licenses','packaging']
SOURCE_TOOLS=['build.ps1','bootstrap-tools.ps1','build_catalog.py','export_schema.py','package_release.py',
 'build_font.py','inspect_assets.py','catalog.py','GrammarChecks/Program.cs','GrammarChecks/GrammarChecks.csproj']
def sha(data): return hashlib.sha256(data).hexdigest()
def put(z,name,data,manifest):
    if name in manifest: raise ValueError('Duplicate package path: '+name)
    if '..' in PurePosixPath(name).parts or PurePosixPath(name).is_absolute(): raise ValueError(name)
    info=zipfile.ZipInfo(name,(2026,9,11,0,0,0))
    info.compress_type=zipfile.ZIP_DEFLATED
    z.writestr(info,data)
    manifest[name]=sha(data)
def package():
    if build_catalog.build(): raise RuntimeError('Catalog validation failed')
    loader=ROOT/'.work/bepinex-755.zip'
    if sha(loader.read_bytes())!=LOADER_HASH: raise RuntimeError('Unexpected loader ZIP')
    dependencies=json.loads((ROOT/'licenses/dependencies.json').read_text('utf-8'))
    if len(dependencies)!=16: raise RuntimeError('Incomplete license inventory')
    source_archives=[]
    for dep in dependencies:
        if sha((ROOT/'licenses'/(dep['name']+'.txt')).read_bytes())!=dep['license_sha256']:
            raise RuntimeError('License checksum mismatch: '+dep['name'])
        if 'source_url' in dep:
            path=ROOT/'.work/third-party-sources'/(dep['name']+'-source.zip')
            if not path.exists():
                path.parent.mkdir(parents=True,exist_ok=True)
                path.write_bytes(urllib.request.urlopen(dep['source_url'],timeout=60).read())
            if sha(path.read_bytes())!=dep['source_sha256']: raise RuntimeError('Source checksum mismatch')
            source_archives.append(path)
    dest=ROOT/'dist'
    dest.mkdir(exist_ok=True)
    install=dest/f'ShroomAndGloom-Korean-{VERSION}-win-x64.zip'
    files={}
    with zipfile.ZipFile(install,'w') as output,zipfile.ZipFile(loader) as upstream:
        for entry in upstream.infolist():
            name=entry.filename.replace('\\','/')
            if entry.is_dir(): continue
            allowed=name in ('winhttp.dll','doorstop_config.ini','.doorstop_version') or name.startswith(('dotnet/','BepInEx/core/'))
            if not allowed: continue
            if 'XUnity' in name: raise RuntimeError('Unexpected legacy plugin')
            put(output,name,upstream.read(entry),files)
        for local,name in [
          ('src/ShroomKorean/bin/Release/net6.0/ShroomKorean.dll','BepInEx/plugins/ShroomKorean/ShroomKorean.dll'),
          ('artifacts/translations.json','BepInEx/plugins/ShroomKorean/translations.json'),
          ('assets/shroom-korean-jua','BepInEx/plugins/ShroomKorean/shroom-korean-jua'),
          ('packaging/BepInEx.cfg','BepInEx/config/BepInEx.cfg')]:
            put(output,name,(ROOT/local).read_bytes(),files)
        for name in DOCS: put(output,'ShroomKorean-docs/'+name,(ROOT/name).read_bytes(),files)
        for path in sorted((ROOT/'licenses').glob('*')):
            if path.is_file(): put(output,'ShroomKorean-docs/licenses/'+path.name,path.read_bytes(),files)
        for path in source_archives: put(output,'ShroomKorean-docs/third-party-sources/'+path.name,path.read_bytes(),files)
        put(output,'ShroomKorean-docs/coverage.json',(ROOT/'artifacts/coverage.json').read_bytes(),files)
        put(output,'ShroomKorean-docs/files.sha256.json',json.dumps(files,indent=2).encode()+b'\n',files)
    with zipfile.ZipFile(install) as check:
        if check.testzip(): raise RuntimeError('ZIP CRC validation failed')
        forbidden=('GameAssembly.dll','Assembly-CSharp.dll','global-metadata.dat','Player.log','LogOutput.log')
        for name in check.namelist():
            if PurePosixPath(name).name in forbidden or any(x in name for x in ('/interop/','/unity-libs/','/cache/','/saves/')):
                raise RuntimeError('Forbidden distribution file: '+name)
    source=dest/f'ShroomAndGloom-Korean-{VERSION}-source.zip'
    source_files={}
    with zipfile.ZipFile(source,'w') as output:
        for name in DOCS+['.gitignore','source-schema.json','preserved.json']:
            put(output,name,(ROOT/name).read_bytes(),source_files)
        for folder in SOURCE_DIRS:
            for path in sorted((ROOT/folder).rglob('*')):
                if path.is_file() and not any(p in ('bin','obj','__pycache__') for p in path.relative_to(ROOT).parts):
                    put(output,path.relative_to(ROOT).as_posix(),path.read_bytes(),source_files)
        for name in SOURCE_TOOLS: put(output,'tools/'+name,(ROOT/'tools'/name).read_bytes(),source_files)
    hashes={path.name:sha(path.read_bytes()) for path in (install,source)}
    (dest/'SHA256SUMS.txt').write_text(''.join(value+'  '+name+'\n' for name,value in hashes.items()),encoding='utf-8')
    report={'version':VERSION,'install_files':len(files),'source_files':len(source_files),'sha256':hashes,
       'excluded_game_assets':True,'excluded_logs_saves_identifiers':True}
    (dest/'package-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    for path in (install,source): print(path.name,path.stat().st_size,'bytes')
    print('CRC, loader hash, dependency licenses and distribution allowlist: PASS')
if __name__=='__main__': package()
