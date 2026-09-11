import json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.work/inventory'
legacy = {}
legacy_path=ROOT / '.work/upstream/_1Final_Translations.txt'
for line in (legacy_path.read_text('utf-8-sig').splitlines() if legacy_path.exists() else []):
    if line.startswith(('#', 'sr:', 'r:')): continue
    pair = re.split(r'(?<!\\)=', line, maxsplit=1)
    if len(pair) == 2:
        legacy[pair[0].replace('\\=', '=').replace('\\n', '\n')] = pair[1].replace('\\=', '=').replace('\\n', '\n')
entries=[]
for path in sorted(OUT.glob('*_en.json')):
    table=path.stem[:-3]
    keys={e['m_Id']:e['m_Key'] for e in json.loads((OUT/(table+' Shared Data.json')).read_text('utf-8'))['m_Entries']}
    for e in json.loads(path.read_text('utf-8'))['m_TableData']:
        en=e['m_Localized']
        if not en: continue
        entries.append(dict(table=table, id=str(e['m_Id']), key=keys.get(e['m_Id']) or '@'+str(e['m_Id']), en=en, ko=legacy.get(en, '')))
(OUT/'catalog.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
for table in sorted({e['table'] for e in entries}):
    group=[e for e in entries if e['table']==table]
    print(table,len(group),'exact matches',sum(bool(e['ko']) for e in group))
    (OUT/(table+'.txt')).write_text('\n'.join(str(i)+'\t'+json.dumps(e,ensure_ascii=False) for i,e in enumerate(entries) if e['table']==table),encoding='utf-8')
import UnityPy
env=UnityPy.load(str(ROOT/'.work/upstream-package/hakgyoansimnadeuri'))
for o in env.objects:
    t=o.read_typetree()
    print(o.path_id,o.type.name,t.get('m_Name'),list(t)[:35])
    (OUT/('font-'+str(o.path_id)+'.json')).write_text(json.dumps(t,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
