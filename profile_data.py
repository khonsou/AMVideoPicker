import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
cols = ['date','period','material_uri','title','impressions','clicks','conversions','ctr','cvr','pvr',
        'play_3s_rate','play_5s_rate','play_over_rate','play_duration_avg','video_duration',
        'keywords','people_tags','material_tags','product_name','product_cate','price_range']
df = pd.read_csv(OUT / 'video_daily.csv.gz', usecols=cols)
err = (df['ctr'] * df['cvr'] - df['pvr']).abs()
print('identity_error_counts', {str(x): int((err > x).sum()) for x in [1e-12,1e-9,1e-6,1e-4]})
show = df.loc[err.nlargest(12).index, ['date','material_uri','title','impressions','clicks','conversions','ctr','cvr','pvr']].copy()
show['identity_error'] = err.loc[show.index]
print('\nidentity_outliers\n', show.to_string(index=False))

agg = df.groupby('material_uri', sort=False).agg(
    title=('title','last'), days=('date','nunique'), impressions=('impressions','sum'),
    clicks=('clicks','sum'), conversions=('conversions','sum'),
    product_rows=('product_name', lambda s: int((s.fillna('')!='').sum())),
).reset_index()
agg['ipm'] = 1000 * agg['conversions'] / agg['impressions'].clip(lower=1)
agg['ctr_w'] = agg['clicks'] / agg['impressions'].clip(lower=1)
agg['cvr_w'] = agg['conversions'] / agg['clicks'].clip(lower=1)
print('\nmaterial_quantiles')
print(agg[['days','impressions','clicks','conversions','ipm','ctr_w','cvr_w']].quantile([0,.1,.25,.5,.75,.9,.95,.99,.999,1]).to_string())
print('\neligibility_counts')
for imp, conv, days in [(10000,1,1),(20000,5,2),(50000,10,3),(100000,20,5),(100000,30,7),(300000,50,7)]:
    mask=(agg.impressions>=imp)&(agg.conversions>=conv)&(agg.days>=days)
    print(imp,conv,days,int(mask.sum()))
print('\nperiod_totals')
print(df.groupby('period')[['impressions','clicks','conversions']].sum().to_string())
print('\nproduct_coverage_rows', float((df.product_name.fillna('')!='').mean()))
print('product_coverage_materials', float((agg.product_rows>0).mean()))
print('\ntop_product_categories')
print(df.loc[df.product_cate.fillna('')!='','product_cate'].value_counts().head(25).to_string())
print('\nduration_quantiles')
print(df.video_duration.quantile([0,.01,.1,.25,.5,.75,.9,.99,1]).to_string())
print('\nrate_quantiles')
print(df[['ctr','cvr','pvr','play_3s_rate','play_5s_rate','play_over_rate']].quantile([0,.01,.1,.5,.9,.95,.99,.999,1]).to_string())

agg.to_csv(OUT/'material_profile.csv', index=False, encoding='utf-8-sig')
