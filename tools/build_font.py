"""Build a static TextMeshPro SDF font from OFL Jua, without Unity Editor.

The upstream fan patch is used solely as a TMP/Shader serialization template.
Its original glyph data and atlas are replaced completely. No game asset input.
"""
from pathlib import Path
import json
import freetype
import numpy as np
from scipy.ndimage import distance_transform_edt
from PIL import Image
from fontTools.ttLib import TTFont
import UnityPy

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'assets/shroom-korean-jua'
FONT=ROOT/'assets/fonts/Jua-Regular.ttf'
SIZE=48
PAD=7
SUPERSAMPLE=3

def build():
    cmap=TTFont(FONT).getBestCmap()
    codes=sorted(set(c for c in cmap if 32<=c<=0xFFFF and (c<0x0250 or 0x2000<=c<=0x206f or 0x3000<=c<=0x318f or 0xac00<=c<=0xd7a3)) | set(range(0xac00,0xd7a4)))
    side=8192 if len(codes)>4500 else 4096
    canvas=Image.new('L',(side,side),0)
    face=freetype.Face(str(FONT))
    face.set_pixel_sizes(0,SIZE*SUPERSAMPLE)
    fallback=freetype.Face(str(ROOT/'assets/fonts/NotoSansKR.ttf'))
    fallback.set_var_design_coords([650])
    fallback.set_pixel_sizes(0,SIZE*SUPERSAMPLE)
    glyphs=[]
    chars=[]
    seen={}
    x=y=PAD+1
    row_height=0
    for code in codes:
        active=face if code in cmap else fallback
        gid=active.get_char_index(code)+(0 if active is face else 100000)
        if gid in seen:
            chars.append(dict(m_ElementType=1,m_Unicode=code,m_GlyphIndex=gid,m_Scale=1.0))
            continue
        active.load_char(chr(code),freetype.FT_LOAD_RENDER|freetype.FT_LOAD_NO_HINTING)
        g=active.glyph
        w=int(np.ceil(g.bitmap.width/SUPERSAMPLE))
        h=int(np.ceil(g.bitmap.rows/SUPERSAMPLE))
        if x+w+PAD>=side:
            x=PAD+1
            y+=row_height+2*PAD+2
            row_height=0
        if y+h+PAD>=side: raise RuntimeError('Atlas overflow')
        metrics=dict(m_Width=g.metrics.width/64/SUPERSAMPLE,m_Height=g.metrics.height/64/SUPERSAMPLE,
            m_HorizontalBearingX=g.metrics.horiBearingX/64/SUPERSAMPLE,m_HorizontalBearingY=g.metrics.horiBearingY/64/SUPERSAMPLE,
            m_HorizontalAdvance=g.advance.x/64/SUPERSAMPLE)
        if w and h:
            raw=np.array(g.bitmap.buffer,dtype=np.uint8).reshape(g.bitmap.rows,g.bitmap.pitch)[:,:g.bitmap.width]
            mask=np.zeros(((h+2*PAD)*SUPERSAMPLE,(w+2*PAD)*SUPERSAMPLE),dtype=bool)
            mask[PAD*SUPERSAMPLE:PAD*SUPERSAMPLE+raw.shape[0],PAD*SUPERSAMPLE:PAD*SUPERSAMPLE+raw.shape[1]]=raw>=128
            signed=distance_transform_edt(mask)-distance_transform_edt(~mask)
            sdf=np.clip(127.5+signed*(127.5/(PAD*SUPERSAMPLE)),0,255).astype(np.uint8)
            tile=Image.fromarray(sdf).resize((w+2*PAD,h+2*PAD),Image.Resampling.LANCZOS)
            # Unity texture coordinates start at bottom left.
            canvas.paste(tile,(x-PAD,side-y-h-PAD))
        glyphs.append(dict(m_Index=gid,m_Metrics=metrics,m_GlyphRect=dict(m_X=x,m_Y=y,m_Width=w,m_Height=h),m_Scale=1.0,m_AtlasIndex=0,m_ClassDefinitionType=0))
        chars.append(dict(m_ElementType=1,m_Unicode=code,m_GlyphIndex=gid,m_Scale=1.0))
        seen[gid]=True
        x+=w+2*PAD+2
        row_height=max(row_height,h)
    env=UnityPy.load(str(ROOT/'.work/upstream-package/hakgyoansimnadeuri'))
    for obj in env.objects:
        if obj.type.name=='Texture2D':
            tex=obj.read()
            rgba=Image.new('RGBA',canvas.size,(255,255,255,255))
            rgba.putalpha(canvas)
            tex.set_image(rgba,target_format=1)
            tex.m_Name='Jua Korean SDF Atlas'
            tex.save()
        elif obj.type.name=='MonoBehaviour':
            tree=obj.read_typetree()
            tree['m_Name']='Shroom Korean Hand SDF'
            tree['hashCode']=0
            tree['materialHashCode']=0
            tree['m_SourceFontFileGUID']=''
            tree['m_AtlasWidth']=tree['m_AtlasHeight']=side
            tree['m_AtlasPadding']=PAD
            tree['m_AtlasPopulationMode']=0
            tree['m_GlyphTable']=glyphs
            tree['m_CharacterTable']=chars
            tree['m_UsedGlyphRects']=[]
            tree['m_FreeGlyphRects']=[]
            tree['m_glyphInfoList']=[]
            tree['m_KerningTable']={'kerningPairs':[]}
            tree['m_FontFeatureTable']={'m_GlyphPairAdjustmentRecords':[]}
            info=tree['m_FaceInfo']
            info.update(m_FamilyName='Shroom Korean Hand',m_StyleName='Regular',m_PointSize=SIZE,m_Scale=1.0,
                m_UnitsPerEM=face.units_per_EM,m_LineHeight=SIZE*1.16,m_AscentLine=SIZE*.88,
                m_CapLine=SIZE*.72,m_MeanLine=SIZE*.52,m_Baseline=0.0,m_DescentLine=-SIZE*.20,
                m_SuperscriptOffset=SIZE*.88,m_SubscriptOffset=-SIZE*.2,
                m_UnderlineOffset=-SIZE*.1,m_UnderlineThickness=1.5,m_StrikethroughOffset=SIZE*.3,m_TabWidth=SIZE*.5)
            obj.save_typetree(tree)
        elif obj.type.name=='Material':
            tree=obj.read_typetree()
            tree['m_Name']='Jua Korean SDF Material'
            floats=dict(tree['m_SavedProperties']['m_Floats'])
            floats.update(_TextureWidth=float(side),_TextureHeight=float(side),_GradientScale=float(PAD+1),_WeightNormal=0.0,_WeightBold=0.0)
            tree['m_SavedProperties']['m_Floats']=list(floats.items())
            obj.save_typetree(tree)
        elif obj.type.name=='AssetBundle':
            tree=obj.read_typetree()
            tree['m_Name']=tree['m_AssetBundleName']='shroom-korean-jua'
            tree['m_Container']=[('assets/jua-korean-sdf.asset',value) for key,value in tree['m_Container']]
            obj.save_typetree(tree)
    DEST.write_bytes(env.file.save(packer='lz4'))
    report=dict(font='Jua Regular with Noto Sans KR for missing syllables',glyphs=len(glyphs),characters=len(chars),atlas=side,point_size=SIZE,
        hangul_syllables=sum(0xac00<=c<=0xd7a3 for c in codes),bytes=DEST.stat().st_size)
    (ROOT/'.work/font-build.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(report)
    check=UnityPy.load(str(DEST))
    font=next(o.read_typetree() for o in check.objects if o.type.name=='MonoBehaviour')
    assert len(font['m_CharacterTable'])==len(codes)

if __name__=='__main__': build()
