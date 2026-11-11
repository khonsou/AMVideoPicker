import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools'/'pydeps'))
import ijson

stats=defaultdict(float)
materials=defaultdict(set)
examples=[]
fields=['ad_star_show_cnt','natural_star_show_cnt','ad_interact_cnt','nature_interact_cnt']

def process(item):
    idx=item.get('object_index') or {}
    uri=item.get('material_uri') or ''
    for field in fields:
        try: value=float(idx.get(field) or 0)
        except (TypeError,ValueError): value=0
        stats[field+'_sum']+=value
        if value!=0:
            stats[field+'_nonzero_rows']+=1
            materials[field].add(uri)
    ctr=float(idx.get('ctr') or 0)
    component=float(idx.get('component_click_rate') or 0)
    stats['ctr_component_abs_diff']+=abs(ctr-component)
    stats['rows']+=1
    if len(examples)<12 and (float(idx.get('ad_star_show_cnt') or 0)!=0 or float(idx.get('natural_star_show_cnt') or 0)!=0):
        examples.append({'title':item.get('title'),'ad_star':idx.get('ad_star_show_cnt'),'natural_star':idx.get('natural_star_show_cnt'),'ad_interact':idx.get('ad_interact_cnt'),'nature_interact':idx.get('nature_interact_cnt')})

with (ROOT/'data'/'industry17_daily84.json').open('rb') as fh:
    for _,items in ijson.kvitems(fh,''):
        for item in items: process(item)
for path in sorted((ROOT/'data'/'industry17_deep').glob('*.json')):
    for item in json.loads(path.read_text(encoding='utf-8'))['items']: process(item)

result={
    'rows':int(stats['rows']),
    'ctr_component_mean_abs_diff':stats['ctr_component_abs_diff']/stats['rows'],
}
for field in fields:
    result[field]={
        'sum':stats[field+'_sum'],
        'nonzero_rows':int(stats[field+'_nonzero_rows']),
        'nonzero_materials':len(materials[field]),
        'nonzero_row_share':stats[field+'_nonzero_rows']/stats['rows'],
    }
result['examples']=examples
print(json.dumps(result,ensure_ascii=False,indent=2))
(ROOT/'outputs'/'traffic_field_audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
