"""Read-only inventory; extracted game data stays in ignored .work."""
from pathlib import Path
import json
import UnityPy

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT.parent
OUT = ROOT / '.work' / 'inventory'
OUT.mkdir(parents=True, exist_ok=True)

for path in sorted((GAME / 'Shroom and Gloom_Data/StreamingAssets/aa/StandaloneWindows64').glob('*.bundle')):
    if 'english' not in path.name and 'shared' not in path.name:
        continue
    env = UnityPy.load(str(path))
    for obj in env.objects:
        if obj.type.name != 'MonoBehaviour':
            continue
        tree = obj.read_typetree()
        name = tree.get('m_Name', str(obj.path_id))
        print(path.name, obj.path_id, name, list(tree))
        (OUT / (name + '.json')).write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding='utf-8')

env = UnityPy.load(str(GAME / 'Shroom and Gloom_Data/resources.assets'))
fonts = []
for obj in env.objects:
    if obj.type.name == 'Font':
        data = obj.read()
        fonts.append({'name': data.m_Name, 'id': obj.path_id, 'size': len(data.m_FontData)})
        if data.m_FontData:
            (OUT / (data.m_Name.replace('/', '_') + '.ttf')).write_bytes(bytes(data.m_FontData))
    elif obj.type.name == 'MonoBehaviour':
        try:
            tree = obj.read_typetree()
            if 'm_CharacterTable' in tree or 'm_glyphInfoList' in tree:
                fonts.append({'name': tree.get('m_Name'), 'id': obj.path_id, 'face': tree.get('m_FaceInfo', tree.get('m_fontInfo'))})
        except Exception:
            pass
(OUT / 'fonts.json').write_text(json.dumps(fonts, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(fonts, ensure_ascii=False, indent=2))
