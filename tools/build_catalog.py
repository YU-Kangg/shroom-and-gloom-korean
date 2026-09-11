"""Build with Python's standard library; no game assets or translation service."""
from pathlib import Path
import json,re,collections,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from export_schema import TOKEN,LINK,CARD,normalize
ROOT=Path(__file__).resolve().parents[1]

def unique_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise ValueError('Duplicate JSON key: '+key)
        result[key]=value
    return result

def read_json(path):
    return json.loads(path.read_text('utf-8'),object_pairs_hook=unique_object)

def build():
    schema=read_json(ROOT/'source-schema.json')
    translated={}
    preserved=read_json(ROOT/'preserved.json')
    for path in sorted((ROOT/'translations').glob('*.json')):
        if path.name=='upstream.json': continue
        for key,value in read_json(path).items():
            translated[path.stem+'/'+key]=value
    output={}
    pending=[]
    errors=[]
    preserved_count=0
    for key,entry in schema.items():
        if key in preserved:
            if preserved[key]['SourceHash']!=entry['SourceHash']:
                errors.append((key,'preserved source changed; review required'))
            elif key in translated:
                errors.append((key,'both translated and preserved'))
            else: preserved_count+=1
            continue
        ko=translated.get(key,'')
        if not isinstance(ko,str) or not ko.strip():
            pending.append(key)
            continue
        if dict(collections.Counter(TOKEN.findall(ko)))!=entry['Tokens']:
            errors.append((key,'placeholder mismatch'))
        clean=ko.replace('\\"','"')
        if dict(collections.Counter(m[1] for m in LINK.findall(clean)))!=entry['Links']:
            errors.append((key,'tooltip link ID mismatch'))
        references=CARD.findall(clean)
        if len(references)!=len(entry['CardReferences']):
            errors.append((key,'card reference count mismatch'))
        for name,reference in zip(references,entry['CardReferences']):
            if reference and normalize(name)!=normalize(translated.get('Card Names/'+reference,'')):
                errors.append((key,'card preview name mismatch: '+reference))
        if '\ufffd' in ko: errors.append((key,'replacement character'))
        output[key]={'SourceHash':entry['SourceHash'],'Text':ko}
    for key in sorted((set(translated)|set(preserved))-set(schema)):
        errors.append((key,'unknown key'))
    dest=ROOT/'artifacts'
    dest.mkdir(exist_ok=True)
    summary={'source_entries':len(schema),'translated':len(output),'preserved':preserved_count,
        'missing':len(pending),'validation_errors':len(errors),'all_scenarios_playtested':False}
    (dest/'coverage.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (dest/'validation-errors.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(summary)
    for error in errors: print(error)
    if pending: print('Missing:',pending)
    if errors or pending: return 1
    (dest/'translations.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0

if __name__=='__main__': sys.exit(build())
