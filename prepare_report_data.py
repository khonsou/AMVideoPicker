import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT/'outputs'
ASSETS = ROOT/'report_assets'
ASSETS.mkdir(exist_ok=True)
scores = pd.read_csv(OUT/'video_scores_all.csv', low_memory=False)
summary = json.loads((OUT/'scoring_summary.json').read_text(encoding='utf-8'))
verification = json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
priority = scores[scores.priority_flag & (scores.category != '其他及待复核3C')].copy()
eff = priority.sort_values(['conservative_index','conversions'],ascending=False).head(20)
scale = priority.sort_values(['conversions','conservative_index'],ascending=False).head(20)


def short_title(s, n=25):
    s = str(s).replace('\n',' ').replace('|','｜')
    return s if len(s)<=n else s[:n]+'…'


def fmt_int(x):
    return f'{int(round(x)):,}'


def fmt_change(x):
    return '新进场／无前期' if pd.isna(x) else f'{x*100:+.1f}%'


def efficiency_table(frame, n=10):
    lines = ['| 排名 | 视频（预览） | 品类 | 曝光 | 转化当量 | CTR | CVR | IPM | 保守指数 | 近期变化 |',
             '|---:|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for rank,(_,r) in enumerate(frame.head(n).iterrows(),1):
        lines.append(f"| {rank} | [{short_title(r.title,28)}]({r.video_url}) | {r.category} | {fmt_int(r.impressions)} | {fmt_int(r.conversions)} | {r.ctr_weighted*100:.2f}% | {r.cvr_weighted*100:.2f}% | {r.ipm_raw:.2f} | {r.conservative_index:,.0f} | {fmt_change(r.recent_ipm_change_vs_P2)} |")
    return '\n'.join(lines)


def scale_table(frame,n=8):
    lines = ['| 排名 | 视频（预览） | 品类 | 曝光 | 转化当量 | IPM | 保守指数 | 近28天IPM |',
             '|---:|---|---|---:|---:|---:|---:|---:|']
    for rank,(_,r) in enumerate(frame.head(n).iterrows(),1):
        lines.append(f"| {rank} | [{short_title(r.title,28)}]({r.video_url}) | {r.category} | {fmt_int(r.impressions)} | {fmt_int(r.conversions)} | {r.ipm_raw:.2f} | {r.conservative_index:,.0f} | {r.ipm_P3:.2f} |")
    return '\n'.join(lines)

(ASSETS/'top_efficiency_table.md').write_text(efficiency_table(eff,12),encoding='utf-8')
(ASSETS/'top_scale_table.md').write_text(scale_table(scale,8),encoding='utf-8')

# Top-10 horizontal bar data, reversed for SVG rendering from largest at top.
top10 = eff.head(10).iloc[::-1]
bar_data = [{
    'title':short_title(r.title,18), 'fullTitle':r.title, 'uri':r.material_uri,
    'index':round(float(r.conservative_index),1), 'ipm':round(float(r.ipm_raw),3),
    'baseline':round(float(r.baseline_ipm),3), 'conversions':int(r.conversions),
} for _,r in top10.iterrows()]

# Deterministic scale-efficiency map sample; always include the top candidates.
pool = scores[(scores.scope_status=='纳入') & (scores.evidence_tier!='证据不足') & (scores.impressions>0) & (scores.ipm_raw>0)].copy()
sample = pd.concat([pool.sample(min(6500,len(pool)),random_state=20261110), pool[pool.priority_flag]]).drop_duplicates('material_uri')

def scatter_group(frame,name,color):
    data=[]
    for _,r in frame.iterrows():
        data.append({'name':short_title(r.title,20),'value':[round(float(r.impressions),2),round(float(r.ipm_raw),5),int(r.conversions)],'uri':r.material_uri})
    return {'name':name,'color':color,'data':data}
scatter_series = [
    scatter_group(sample[sample.priority_flag],'优先候选','#2F6BFF'),
    scatter_group(sample[(~sample.priority_flag)&(~sample.efficiency_decline_flag)],'验证／观察','#8A94A6'),
    scatter_group(sample[(~sample.priority_flag)&(sample.efficiency_decline_flag)],'近期衰退','#E15759'),
]

# Temporal validation points. Reproduce the train top-100 selection from score_videos.py.
train_pool = scores[(scores.scope_status=='纳入') & (scores.train_impressions>=50000) & (scores.train_conversions>=10)].copy()
top_train = train_pool.nlargest(100,'train_index')
test_pool = train_pool[train_pool.impressions_P3>=10000].copy()
test_sample = pd.concat([test_pool.sample(min(4500,len(test_pool)),random_state=42),top_train[top_train.impressions_P3>=10000]]).drop_duplicates('material_uri')
temporal_series = [
    {'name':'其他素材','color':'#8A94A6','data':[{'name':short_title(r.title,20),'value':[float(r.train_index),float(r.test_index_raw)]} for _,r in test_sample[~test_sample.material_uri.isin(top_train.material_uri)].iterrows() if r.train_index>0 and r.test_index_raw>0]},
    {'name':'前56天Top 100','color':'#2F6BFF','data':[{'name':short_title(r.title,20),'value':[float(r.train_index),float(r.test_index_raw)]} for _,r in test_sample[test_sample.material_uri.isin(top_train.material_uri)].iterrows() if r.train_index>0 and r.test_index_raw>0]},
]
periods=[]
for p,label in [('P1','第1–4周'),('P2','第5–8周'),('P3','第9–12周')]:
    imp=scores[f'impressions_{p}'].sum(); clk=scores[f'clicks_{p}'].sum(); conv=scores[f'conversions_{p}'].sum()
    periods.append({'period':label,'impressions':int(imp),'clicks':int(clk),'conversions':int(conv),'ipm':1000*conv/imp})
chart_data = {
    'bar':bar_data,
    'scatter':scatter_series,
    'temporal':temporal_series,
    'temporalSummary':summary['temporal_validation'],
    'funnel':{'impressions':int(scores.impressions.sum()),'clicks':int(scores.clicks.sum()),'conversions':int(scores.conversions.sum())},
    'periods':periods,
}
(ASSETS/'chart_data.json').write_text(json.dumps(chart_data,ensure_ascii=False),encoding='utf-8')
print('report assets prepared',ASSETS)
print('funnel',chart_data['funnel'])
print('periods',periods)
