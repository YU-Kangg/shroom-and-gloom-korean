"""Explicitly export structural constraints from an inspected, owned game build.

Original prose is omitted. This does not approve changed translations or refresh
preserved.json. Normal builds use the committed schema and need no game files.
"""
import collections, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOKEN=re.compile(r'\[[A-Z][A-Z0-9_]*(?:=[^\]]+)?\]')
LINK=re.compile(r'<link=([\"\']?)(.*?)\1>',re.I)
CARD=re.compile(r'<link=[\"\']?mC[\"\']?>(.*?)</link>',re.I)
normalize=lambda text: re.sub(r'\s+','',text).lower()

def export():
    catalog=json.loads((ROOT/'.work/inventory/catalog.json').read_text('utf-8'))
    names={normalize(e['en']):e['key'] for e in catalog if e['table']=='Card Names'}
    result={}
    for e in catalog:
        key=e['table']+'/'+e['key']
        text=e['en'].replace('\\"','"')
        result[key]={
            'SourceHash':hashlib.sha256(e['en'].encode()).hexdigest(),
            'Tokens':dict(collections.Counter(TOKEN.findall(e['en']))),
            'Links':dict(collections.Counter(m[1] for m in LINK.findall(text))),
            'CardReferences':[names.get(normalize(n)) for n in CARD.findall(text)]
        }
    (ROOT/'source-schema.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Exported structural constraints for',len(result),'entries')
if __name__=='__main__': export()
