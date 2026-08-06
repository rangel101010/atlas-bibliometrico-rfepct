#!/usr/bin/env python3
"""Atualiza o Atlas a partir da OpenAlex e separa correspondências ambíguas."""
from __future__ import annotations
import json, os, re, time, unicodedata
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
CAMPI=json.loads((ROOT/'data/campi.json').read_text(encoding='utf-8'))
API='https://api.openalex.org/works'
YEARS=set(range(2021,2026))

def norm(s):
    s=unicodedata.normalize('NFKD',s or '').encode('ascii','ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+',' ',s).strip()

def get(params):
    key=os.getenv('OPENALEX_API_KEY','').strip()
    if key: params['api_key']=key
    params['mailto']=os.getenv('OPENALEX_MAILTO','rangel.f.pacheco@gmail.com')
    req=Request(API+'?'+urlencode(params),headers={'User-Agent':'Atlas-RFEPCT/1.0'})
    with urlopen(req,timeout=60) as r: return json.load(r)

def raw_affiliations(work):
    vals=[]
    for a in work.get('authorships',[]):
        for x in a.get('raw_affiliation_strings') or []: vals.append(x)
        for i in a.get('institutions') or []: vals.append(i.get('display_name',''))
    return list(dict.fromkeys(x for x in vals if x))

def match(work,campus):
    hay=' | '.join(map(norm,raw_affiliations(work)))
    aliases=[norm(a) for a in campus['aliases']]
    exact=any(a and a in hay for a in aliases)
    # campus + rede no mesmo texto é evidência auxiliar, mas permanece em revisão.
    token=norm(campus['name'].split('—')[-1])
    loose=token in hay and any(k in hay for k in ('instituto federal',' if '))
    return 'confirmed' if exact else ('review' if loose else None)

def abstract(inv):
    if not inv:return ''
    out=[]
    for word,positions in inv.items():
        for p in positions: out.append((p,word))
    return ' '.join(w for _,w in sorted(out))

def compact(w,c,status):
    countries={i.get('country_code') for a in w.get('authorships',[]) for i in a.get('institutions',[]) if i.get('country_code')}
    return {'id':w['id'].rsplit('/',1)[-1],'doi':w.get('doi'),'title':w.get('display_name') or 'Sem título','year':w.get('publication_year'),'campus_id':c['id'],'campus':c['name'],'profile':c['profile'],'citations':w.get('cited_by_count',0),'open_access':bool((w.get('open_access') or {}).get('is_oa')),'international':len(countries)>1,'countries':sorted(countries),'authors':'; '.join(a.get('author',{}).get('display_name','') for a in w.get('authorships',[])),'source':((w.get('primary_location') or {}).get('source') or {}).get('display_name',''),'url':w.get('doi') or w.get('id'),'type':w.get('type'),'status':status,'affiliations':raw_affiliations(w),'abstract':abstract(w.get('abstract_inverted_index'))}

def main():
    confirmed={}; review={}
    for c in CAMPI:
        # A busca textual amplia a recuperação; a afiliação bruta decide a inclusão.
        for alias in c['aliases']:
            cursor='*'
            for _ in range(20):
                data=get({'search':alias,'filter':'from_publication_date:2021-01-01,to_publication_date:2025-12-31','per-page':100,'cursor':cursor,'select':'id,doi,display_name,publication_year,cited_by_count,open_access,authorships,primary_location,type,abstract_inverted_index'})
                for w in data.get('results',[]):
                    if w.get('publication_year') not in YEARS: continue
                    status=match(w,c)
                    if not status: continue
                    item=compact(w,c,status); key=(item['id'],c['id'])
                    (confirmed if status=='confirmed' else review)[key]=item
                nxt=(data.get('meta') or {}).get('next_cursor')
                if not nxt or not data.get('results'): break
                cursor=nxt; time.sleep(.12)
            time.sleep(.15)
    # Se o mesmo trabalho casar com dois campi, conserva ambos para revisão humana.
    by_work={}
    for k,v in confirmed.items(): by_work.setdefault(v['id'],[]).append(k)
    for wid,keys in by_work.items():
        if len(keys)>1:
            for k in keys: review[k]=confirmed.pop(k)
    out={'updated_at':datetime.now(timezone.utc).isoformat(),'works':sorted(confirmed.values(),key=lambda x:(-x['year'],x['campus'])),'review':sorted(review.values(),key=lambda x:(-x['year'],x['campus'])),'meta':{'source':'OpenAlex','period':'2021-2025','confirmed':len(confirmed),'in_review':len(review),'method':'Correspondência conservadora por variantes de afiliação; deduplicação por OpenAlex ID e campus.'}}
    (ROOT/'data/works.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f"Confirmados: {len(confirmed)} | Em revisão: {len(review)}")

if __name__=='__main__': main()
