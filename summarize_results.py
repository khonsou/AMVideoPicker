import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
scores = pd.read_csv(OUT / 'video_scores_all.csv', low_memory=False)
priority = scores[scores.priority_flag].copy()
priority = priority[priority.category != '其他及待复核3C']

cols = ['material_uri','title','category','video_duration','impressions','clicks','conversions','ctr_weighted','cvr_weighted','ipm_raw','baseline_ipm','eb_index','conservative_index','impressions_P3','conversions_P3','ipm_P3','recent_ipm_change_vs_P2','conversion_day_rate','play_3s_rate_weighted','retention_5s_to_3s','diagnosis']

def print_table(frame, n=20):
    x = frame[cols].head(n).copy()
    for c in ['ctr_weighted','cvr_weighted','play_3s_rate_weighted','retention_5s_to_3s']:
        x[c] = (100*x[c]).round(2)
    for c in ['ipm_raw','baseline_ipm','eb_index','conservative_index','ipm_P3']:
        x[c] = x[c].round(2)
    x['recent_ipm_change_vs_P2'] = (100*x['recent_ipm_change_vs_P2']).round(1)
    print(x.to_markdown(index=False))

print('TOP_EFFICIENCY')
print_table(priority.sort_values(['conservative_index','conversions'], ascending=False), 20)
print('\nTOP_SCALE')
print_table(priority.sort_values(['conversions','conservative_index'], ascending=False), 15)
print('\nCATEGORY_LEADERS')
leaders = priority.sort_values(['conservative_index','conversions'], ascending=False).groupby('category', group_keys=False).head(3)
print_table(leaders.sort_values(['category','conservative_index'], ascending=[True,False]), 40)
print('\nCOUNTS_BY_CATEGORY')
print(priority.category.value_counts().to_string())
print('\nTOTALS_AFTER_GATES')
print(scores[['impressions','clicks','conversions']].sum().to_string())
print('\nPERIOD_TOTALS_AFTER_GATES')
for p in ['P1','P2','P3']:
    imp=scores[f'impressions_{p}'].sum(); clk=scores[f'clicks_{p}'].sum(); conv=scores[f'conversions_{p}'].sum()
    print(p, imp, clk, conv, 'IPM',1000*conv/imp)

priority.sort_values(['conservative_index','conversions'], ascending=False).head(20)[cols+['video_url','people_tags','material_tags','product_cate']].to_csv(OUT/'top20_efficiency.csv',index=False,encoding='utf-8-sig')
priority.sort_values(['conversions','conservative_index'], ascending=False).head(20)[cols+['video_url','people_tags','material_tags','product_cate']].to_csv(OUT/'top20_scale.csv',index=False,encoding='utf-8-sig')
leaders[cols+['video_url','people_tags','material_tags','product_cate']].to_csv(OUT/'category_leaders.csv',index=False,encoding='utf-8-sig')
