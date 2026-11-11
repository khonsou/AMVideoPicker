import json
from pathlib import Path

root = Path('/Users/linan/Desktop/投放视频原始数据')
target = 'v0200fg10000d6fav6fog65kebsgu9m0'

print('Python JSON inspection')
try:
    import ijson
    print('ijson_available', True)
except Exception as exc:
    print('ijson_available', False, type(exc).__name__)

for day in ['20260811', '20260812', '20260829', '20260915', '20261015', '20261102']:
    path = root / 'data' / 'industry17_deep' / f'{day}.json'
    payload = json.loads(path.read_text(encoding='utf-8'))
    matches = [x for x in payload['items'] if x.get('material_uri') == target]
    if matches:
        x = matches[0]
        idx = x['object_index']
        imp = int(float(idx['show_cnt']))
        clicks = imp * float(idx.get('ctr') or 0)
        conversions_from_cvr = clicks * float(idx.get('cvr') or 0)
        conversions_from_pvr = imp * float(idx.get('pvr') or 0)
        print(day, 'deep', {'impressions': imp, 'clicks_est': clicks, 'conversions_cvr_est': conversions_from_cvr, 'conversions_pvr_est': conversions_from_pvr, 'title': x['title']})
    else:
        print(day, 'target_not_in_deep_file')

# Check the conversion identity on the latest incremental file without modifying raw data.
path = root / 'data' / 'industry17_deep' / '20261102.json'
items = json.loads(path.read_text(encoding='utf-8'))['items']
errors = []
nonzero = 0
for x in items:
    idx = x.get('object_index') or {}
    imp = int(float(idx.get('show_cnt') or 0))
    ctr = float(idx.get('ctr') or 0)
    cvr = float(idx.get('cvr') or 0)
    pvr = float(idx.get('pvr') or 0)
    if imp and (ctr or cvr or pvr):
        nonzero += 1
        errors.append(abs(ctr * cvr - pvr))
print('latest_deep_rows', len(items), 'rows_with_funnel_metrics', nonzero)
print('ctr_cvr_minus_pvr_max_abs', max(errors) if errors else None)
print('ctr_cvr_minus_pvr_mean_abs', sum(errors)/len(errors) if errors else None)
