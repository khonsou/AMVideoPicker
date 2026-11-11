import json
import shutil
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
APP=ROOT/'app'
OUT=ROOT/'outputs'
DATA_DIR=APP/'src'/'data'
DOWNLOAD_DIR=APP/'public'/'downloads'
DATA_DIR.mkdir(parents=True,exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True,exist_ok=True)

scores=pd.read_csv(OUT/'video_scores_all.csv',low_memory=False)
summary=json.loads((OUT/'scoring_summary.json').read_text(encoding='utf-8'))
chart=json.loads((ROOT/'report_assets'/'chart_data.json').read_text(encoding='utf-8'))
p=scores[scores.priority_flag].copy()
usecols=['date','period','material_uri','impressions','clicks','conversions','play_3s_rate','play_5s_rate','play_over_rate','play_duration_avg']
daily=pd.read_csv(OUT/'video_daily.csv.gz',usecols=usecols)
daily['valid_attention']=(
    daily[['play_3s_rate','play_5s_rate','play_over_rate']].ge(0).all(axis=1)
    & daily[['play_3s_rate','play_5s_rate','play_over_rate']].le(1).all(axis=1)
    & (daily.play_5s_rate<=daily.play_3s_rate)
    & (daily.play_over_rate<=daily.play_5s_rate)
    & (daily.play_duration_avg>=0)
)
period_map={'P1_20260811_20260907':'P1','P2_20260908_20261005':'P2','P3_20261006_20261102':'P3'}
daily['period_short']=daily.period.map(period_map)


def clean(v,digits=4):
    if v is None or pd.isna(v) or not np.isfinite(v): return None
    return round(float(v),digits)


def weighted(sub,rate):
    valid=sub[sub.valid_attention]
    if valid.empty or valid.impressions.sum()==0: return None
    return float((valid[rate]*valid.impressions).sum()/valid.impressions.sum())


def period_record(sub):
    return {
        'days':int(sub.date.nunique()),'impressions':int(sub.impressions.sum()),
        'clicks':int(sub.clicks.sum()),'conversions':int(sub.conversions.sum()),
        'play3s':weighted(sub,'play_3s_rate'),'play5s':weighted(sub,'play_5s_rate'),
        'playOver':weighted(sub,'play_over_rate'),
        'attentionImpressions':int(sub.loc[sub.valid_attention,'impressions'].sum()),
    }


def growth(previous,current):
    if previous is None or current is None or previous==0: return None
    return current/previous-1


def ratio_change(previous,current,previous_key,current_key=None):
    current_key=current_key or previous_key
    if not previous or not current or not previous.get(previous_key) or not current.get(current_key): return None
    return current[current_key]/previous[previous_key]-1

# Overall period series, including independently quality-gated watch metrics.
periods=[]
for period,label in [('P1','第1–4周'),('P2','第5–8周'),('P3','第9–12周')]:
    sub=daily[daily.period_short==period]
    rec=period_record(sub)
    periods.append({
        'period':label,'ipm':clean(1000*rec['conversions']/rec['impressions'],3),
        'ctr':clean(rec['clicks']/rec['impressions'],6),
        'play3s':clean(rec['play3s'],5),'play5s':clean(rec['play5s'],5),
        'playOver':clean(rec['playOver'],5),
        'qualityCoverage':clean(rec['attentionImpressions']/rec['impressions'],4),
        'impressions':rec['impressions'],'conversions':rec['conversions'],
    })

candidate_daily=daily[daily.material_uri.isin(set(p.material_uri))]
groups={uri:group for uri,group in candidate_daily.groupby('material_uri',sort=False)}
videos=[]
for _,r in p.iterrows():
    group=groups[r.material_uri]
    p2=period_record(group[group.period_short=='P2'])
    p3=period_record(group[group.period_short=='P3'])
    p2_ctr=p2['clicks']/p2['impressions'] if p2['impressions'] else None
    p3_ctr=p3['clicks']/p3['impressions'] if p3['impressions'] else None
    p2_ipm=1000*p2['conversions']/p2['impressions'] if p2['impressions'] else None
    p3_ipm=1000*p3['conversions']/p3['impressions'] if p3['impressions'] else None
    p2_daily=p2['impressions']/p2['days'] if p2['days'] else None
    p3_daily=p3['impressions']/p3['days'] if p3['days'] else None
    comparable=bool(p2['days']>=3 and p3['days']>=3 and p2['impressions']>=20000 and p3['impressions']>=20000)
    impressions_growth=growth(p2['impressions'],p3['impressions'])
    clicks_growth=growth(p2['clicks'],p3['clicks'])
    conversions_growth=growth(p2['conversions'],p3['conversions'])
    ctr_change=growth(p2_ctr,p3_ctr)
    ipm_change=growth(p2_ipm,p3_ipm)
    play3s_change=growth(p2['play3s'],p3['play3s'])
    play_over_change=growth(p2['playOver'],p3['playOver'])
    p2_quality_coverage=p2['attentionImpressions']/p2['impressions'] if p2['impressions'] else None
    p3_quality_coverage=p3['attentionImpressions']/p3['impressions'] if p3['impressions'] else None
    quality_trend=min(ctr_change,play_over_change) if ctr_change is not None and play_over_change is not None and p2_quality_coverage is not None and p3_quality_coverage is not None and p2_quality_coverage>=.5 and p3_quality_coverage>=.5 else None
    exposure_momentum=growth(p2_daily,p3_daily)
    dilution_risk=bool(comparable and exposure_momentum is not None and exposure_momentum>=.5 and ((ctr_change is not None and ctr_change<=-.2) or (play_over_change is not None and play_over_change<=-.2)))
    if not comparable:
        traffic_signal='趋势证据不足'
    elif dilution_risk:
        traffic_signal='加量投放伴随质量下滑'
    elif ipm_change is not None and ipm_change<=-.3:
        traffic_signal='转化效率下滑'
    elif exposure_momentum is not None and exposure_momentum>=.5 and ipm_change is not None and ipm_change>=0:
        traffic_signal='加量投放且效率保持'
    else:
        traffic_signal='未见异常组合'
    videos.append({
        'uri':r.material_uri,'title':r.title,'category':r.category,
        'duration':clean(r.video_duration,1),'impressions':int(r.impressions),
        'clicks':int(r.clicks),'conversions':int(r.conversions),
        'ctr':clean(r.ctr_weighted,6),'cvr':clean(r.cvr_weighted,6),
        'ipm':clean(r.ipm_raw,3),'baselineIpm':clean(r.baseline_ipm,3),
        'ebIndex':clean(r.eb_index,1),'conservativeIndex':clean(r.conservative_index,1),
        'p2Impressions':p2['impressions'],'p3Impressions':p3['impressions'],
        'p2Clicks':p2['clicks'],'p3Clicks':p3['clicks'],
        'p2Conversions':p2['conversions'],'p3Conversions':p3['conversions'],
        'p2Days':p2['days'],'p3Days':p3['days'],
        'p2Ctr':clean(p2_ctr,6),'p3Ctr':clean(p3_ctr,6),
        'p2Ipm':clean(p2_ipm,3),'p3Ipm':clean(r.ipm_P3,3),'recentChange':clean(r.recent_ipm_change_vs_P2,4),
        'impressionsGrowth':clean(impressions_growth),'clicksGrowth':clean(clicks_growth),
        'conversionsGrowth':clean(conversions_growth),'ctrChange':clean(ctr_change),
        'ipmChange':clean(ipm_change),'play3sChange':clean(play3s_change),
        'playOverChange':clean(play_over_change),'exposureMomentum':clean(exposure_momentum),
        'qualityTrend':clean(quality_trend),'p2QualityCoverage':clean(p2_quality_coverage,4),'p3QualityCoverage':clean(p3_quality_coverage,4),
        'growthComparable':comparable,'dilutionRisk':dilution_risk,'trafficSignal':traffic_signal,
        'conversionDayRate':clean(r.conversion_day_rate,4),
        'play3s':clean(r.play_3s_rate_weighted,4),'play5s':clean(r.play_5s_rate_weighted,4),
        'playOver':clean(r.play_over_rate_weighted,4),
        'avgWatch':clean(r.avg_watch_seconds,2),'retention':clean(r.retention_5s_to_3s,4),
        'qualityCoverage':clean(r.attention_impressions/r.raw_impressions if r.raw_impressions else None,4),
        'diagnosis':r.diagnosis,'videoUrl':r.video_url,
        'peopleTags':[] if pd.isna(r.people_tags) else str(r.people_tags).split('|'),
        'materialTags':[] if pd.isna(r.material_tags) else str(r.material_tags).split('|'),
        'productCate':'' if pd.isna(r.product_cate) else r.product_cate,
    })

# Plain-Chinese reading notes use candidate medians only for description, not for
# financial or causal claims.
median_ctr=float(np.nanmedian([v['ctr'] if v['ctr'] is not None else np.nan for v in videos]))
median_play3s=float(np.nanmedian([v['play3s'] if v['play3s'] is not None else np.nan for v in videos]))
median_play_over=float(np.nanmedian([v['playOver'] if v['playOver'] is not None else np.nan for v in videos]))
for v in videos:
    ctr_high=v['ctr'] is not None and v['ctr']>=median_ctr
    hook_low=v['play3s'] is not None and v['play3s']<median_play3s
    watch_high=v['playOver'] is not None and v['playOver']>=median_play_over
    ipm_high=v['ipm'] is not None and v['baselineIpm'] and v['ipm']>=1.2*v['baselineIpm']
    growth_bad=v['growthComparable'] and v['impressionsGrowth'] is not None and v['impressionsGrowth']>=.5 and ((v['ctrChange'] is not None and v['ctrChange']<=-.2) or (v['playOverChange'] is not None and v['playOverChange']<=-.2))
    quality_good=v['growthComparable'] and v['ctrChange'] is not None and v['ctrChange']>0 and v['playOverChange'] is not None and v['playOverChange']>0
    growth_good=v['growthComparable'] and v['impressionsGrowth'] is not None and v['impressionsGrowth']>=.5 and v['ipmChange'] is not None and v['ipmChange']>=0
    if growth_bad:
        summary_text='投放量增长很快，但点击率或看完比例下降：追加流量后质量被稀释，先查人群和出价。'
    elif quality_good:
        summary_text='点击率和看完比例都在上升：内容质量趋势向好，值得小预算复测。'
    elif hook_low and ctr_high:
        summary_text='点击率不错，但看到 3 秒的人偏少：可能人群较准，开头仍有优化空间。'
    elif ctr_high and not watch_high:
        summary_text='点击的人不少，但看完的人相对偏少：先检查开头承诺和正文是否接得上。'
    elif watch_high and not ctr_high:
        summary_text='看完的人不少，但点击相对偏少：内容有承接，行动引导可以更明确。'
    elif growth_good:
        summary_text='投放量上升，目标行为效率也没有掉队：值得进入小预算复测。'
    elif ctr_high and watch_high and ipm_high:
        summary_text='点击、观看和目标行为都较强：值得优先审片并小预算复测。'
    else:
        summary_text='指标有强有弱，不能只凭一项下结论，建议和同类视频一起复核。'
    v['plainSummary']=summary_text

data={
    'meta':{
        'title':'3C 短视频内容证据看板','window':'2026.08.11—2026.11.02',
        'rawRows':576000,'dailyRows':504000,'materials':59232,
        'priorityCount':summary['priority_candidates'],'testCount':summary['test_candidates'],
        'declineCount':summary['efficiency_decline_materials'],
        'excludedFunnelRows':summary['excluded_funnel_rows'],
        'invalidAttentionRows':summary['invalid_attention_rows'],
        'globalIpm':round(summary['global_ipm_after_quality_gate'],3),
        'rho':round(summary['temporal_validation']['train_test_spearman_all_testable'],3),
        'priorOverlap5k':round(summary['prior_sensitivity']['prior_5000_top50_overlap_with_prior_10000'],2),
        'priorOverlap20k':round(summary['prior_sensitivity']['prior_20000_top50_overlap_with_prior_10000'],2),
        'impressions':chart['funnel']['impressions'],'clicks':chart['funnel']['clicks'],
        'conversions':chart['funnel']['conversions'],
        'growthComparableCount':sum(v['growthComparable'] for v in videos),
        'qualityRisingCount':sum(v['growthComparable'] and v['qualityTrend'] is not None and v['ctrChange']>0 and v['playOverChange']>0 for v in videos),
        'dilutionRiskCount':sum(v['dilutionRisk'] for v in videos),
    },
    'periods':periods,
    'videos':videos,
}
content='import type { DashboardData } from \'@/types/dashboard\'\n\nexport const dashboard: DashboardData = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
(DATA_DIR/'dashboard.ts').write_text(content,encoding='utf-8')
enriched=pd.DataFrame(videos)
for column in ['peopleTags','materialTags']:
    enriched[column]=enriched[column].map(lambda values:'|'.join(values))
enriched.to_csv(OUT/'h5_candidates_enriched.csv',index=False,encoding='utf-8-sig')
shutil.copy2(OUT/'h5_candidates_enriched.csv',DOWNLOAD_DIR/'h5_candidates_enriched.csv')
shutil.copy2(OUT/'priority_candidates.csv',DOWNLOAD_DIR/'priority_candidates.csv')
shutil.copy2(OUT/'top20_efficiency.csv',DOWNLOAD_DIR/'top20_efficiency.csv')
shutil.copy2(ROOT/'3C短视频ROI评估与高潜视频筛选报告.md',DOWNLOAD_DIR/'roi_evaluation_report.md')
print('videos',len(videos),'typescript_bytes',len(content.encode('utf-8')),'growth_comparable',data['meta']['growthComparableCount'])
print('periods',periods)
