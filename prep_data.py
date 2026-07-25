import pandas as pd, json, ast
from collections import Counter

CAND = pd.read_csv('/home/claude/engine/data/enriched_discovery_v5.csv', engine='python').fillna('')
F = pd.read_csv('/mnt/user-data/uploads/all_feedback.csv')
F['date'] = pd.to_datetime(F.date, format='mixed', utc=True, errors='coerce')
date_map = dict(zip(F.uid, F.date))

def parse_list(v):
    s=str(v).strip()
    if not s or s in ('[]','nan'): return []
    try:
        out=ast.literal_eval(s)
        return [str(x) for x in out] if isinstance(out,list) else [str(out)]
    except Exception:
        return [x.strip().strip("'\"") for x in s.strip('[]').split(',') if x.strip()]

CAND['cats'] = CAND.categories_mentioned.apply(parse_list)
CAND['date'] = CAND.uid.map(date_map).astype(str).str.slice(0,10)
CAND['discovery'] = CAND.discovery_relevant.astype(str).str.lower() == 'true'

THEME_GROUP = {
 'discovery_awareness':'DISCOVERABILITY','assortment_gap':'DISCOVERABILITY','search_findability':'DISCOVERABILITY',
 'trust_quality':'TRUST','returns_support':'TRUST','quality_trust':'TRUST',
 'delivery_ops':'EXPERIENCE','app_ux':'EXPERIENCE','price_value':'EXPERIENCE','habit_convenience':'EXPERIENCE',
 'other':'UNCLASSIFIED',
}
THEME_LABEL = {
 'discovery_awareness':'Awareness','assortment_gap':'Assortment gap','search_findability':'Findability',
 'trust_quality':'Trust & quality','returns_support':'Returns & support','quality_trust':'Trust & quality',
 'delivery_ops':'Delivery','app_ux':'App experience','price_value':'Price & value','habit_convenience':'Habit & convenience',
 'other':'Unclassified',
}
CAND['group'] = CAND.primary_theme.map(THEME_GROUP).fillna('UNCLASSIFIED')

def vc(s): return [{"name":str(k),"value":int(v)} for k,v in Counter(s).most_common()]

disc = CAND[CAND.discovery]
bl = disc.new_category_barrier.value_counts()
barrier_mix = [
  {"name":"awareness","label":"Awareness","value":int(bl.get('awareness',0))},
  {"name":"assortment","label":"Assortment","value":int(bl.get('assortment',0))},
  {"name":"trust","label":"Trust / Confidence","value":int(bl.get('trust',0))},
  {"name":"other","label":"Other","value":int(bl.get('none',0)+bl.get('findability',0)+bl.get('price',0))},
]

disc_cats = Counter(); [disc_cats.update(x) for x in disc.cats]
disc_cats_ranked = [{"name":k,"value":int(v)} for k,v in disc_cats.most_common() if k not in ('other',)]

cat_c = Counter(); [cat_c.update(x) for x in CAND.cats]
non_grocery = [{"name":k,"value":int(v)} for k,v in cat_c.most_common() if k not in ('grocery_staples','snacks_beverages','other')]

matrix=[]
for p in ['blinkit','zepto','bigbasket']:
    g = CAND[CAND.platform==p]
    row = {"platform":p, "total":int(len(g))}
    for grp in ['DISCOVERABILITY','TRUST','EXPERIENCE']:
        row[grp] = int((g.group==grp).sum())
    row['discovery'] = int(g.discovery.sum())
    row['trust_pct'] = round(100*(g.primary_theme.isin(['trust_quality','quality_trust'])).mean(),1)
    row['neg_pct'] = round(100*(g.sentiment=='negative').mean(),1)
    matrix.append(row)

windows=[]
for s,g in F.groupby('source'):
    windows.append(dict(source=s, n=int(len(g)), start=str(g.date.min())[:10], end=str(g.date.max())[:10],
                         days=int((g.date.max()-g.date.min()).days)))
windows = sorted(windows, key=lambda x:-x['n'])

rows=[]
for r in CAND.itertuples(index=False):
    rows.append(dict(
        uid=r.uid, platform=r.platform, source=r.source, rating=float(r.rating) if str(r.rating).strip() not in ('','nan') else 0.0,
        text=str(r.text)[:380], date=r.date,
        sentiment=r.sentiment or 'unknown', theme=r.primary_theme, secondary=r.secondary_theme,
        group=r.group, categories=[c for c in r.cats if c and c!='other'],
        discovery=bool(r.discovery), barrier_label=r.new_category_barrier or 'none',
        segment=r.segment_signal or 'unknown', jtbd=str(r.jtbd)[:300],
        quote=str(r.representative_quote)[:280], reasoning=str(r.reasoning)[:500],
        retrieval_families=str(r.retrieval_families).split('|') if r.retrieval_families else [],
        retrieval_stages=str(r.retrieval_stages).split('|') if r.retrieval_stages else [],
    ))

data = dict(
 meta=dict(
   corpus=3776, retrieved=int(len(CAND)),
   retrieval_pct=round(100*len(CAND)/3776,1),
   discovery=int(disc.shape[0]),
   discovery_pct_of_retrieved=round(100*len(disc)/len(CAND),2),
   discovery_pct_of_corpus=round(100*len(disc)/3776,2),
   avg_rating=round(float(pd.to_numeric(CAND.rating, errors='coerce').fillna(0).mean()),2),
   blinkit=int((CAND.platform=='blinkit').sum()),
   date_min=str(F.date.min())[:10], date_max=str(F.date.max())[:10],
   recall_known=38, recall_total=47,
 ),
 windows=windows, matrix=matrix,
 theme=vc(CAND[CAND.primary_theme!='other'].primary_theme), sentiment=vc(CAND.sentiment),
 platform=vc(CAND.platform), source=vc(CAND.source),
 categories=non_grocery,
 barrier_mix=barrier_mix, disc_categories=disc_cats_ranked,
 rows=rows,
)
open('data.json','w').write(json.dumps(data, separators=(',',':')))
import os
print('size', round(os.path.getsize('data.json')/1e6,2), 'MB')
print(json.dumps(data['meta'], indent=1))
print('barrier_mix', barrier_mix)
