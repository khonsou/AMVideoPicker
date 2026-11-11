import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'outputs'
quality = json.loads((OUT/'extraction_quality.json').read_text(encoding='utf-8'))
scoring = json.loads((OUT/'scoring_summary.json').read_text(encoding='utf-8'))
daily = pd.read_csv(OUT/'video_daily.csv.gz', low_memory=False)
scores = pd.read_csv(OUT/'video_scores_all.csv', low_memory=False)
priority = pd.read_csv(OUT/'priority_candidates.csv', low_memory=False)
top20 = pd.read_csv(OUT/'top20_efficiency.csv', low_memory=False)

assert len(daily) == 504000
assert daily.groupby('date').size().eq(6000).all()
assert not daily.duplicated(['date','material_uri']).any()
assert daily.material_uri.nunique() == 59232
assert len(scores) == 59232 and scores.material_uri.nunique() == 59232
assert quality['duplicate_rows_removed'] == 72000
assert scoring['excluded_funnel_rows'] == 102
assert len(priority) == scoring['priority_candidates']
assert len(top20) == 20
priority_check = scores[scores.priority_flag]
assert len(priority_check) == len(priority)
assert priority_check.scope_status.eq('纳入').all()
assert priority_check.evidence_tier.eq('规模证据').all()
assert priority_check.recent_evidence.eq('近28天足量').all()
assert priority_check.high_efficiency_flag.all()
assert (~priority_check.efficiency_decline_flag).all()
assert np.isfinite(priority[['ipm_raw','eb_ipm','lcb90_ipm','eb_index','conservative_index']].to_numpy()).all()
assert (priority.lcb90_ipm <= priority.eb_ipm + 1e-9).all()
assert top20.video_url.str.startswith('https://yuntu.oceanengine.com/').all()

click_residual = (daily.impressions * daily.ctr - daily.clicks).abs()
event_residual = (daily.impressions * daily.pvr - daily.conversions).abs()
attention_reasons = {
    'play_3s_rate_above_1': int((daily.play_3s_rate > 1).sum()),
    'play_5s_rate_above_1': int((daily.play_5s_rate > 1).sum()),
    'play_over_rate_above_1': int((daily.play_over_rate > 1).sum()),
    'play_5s_above_3s': int((daily.play_5s_rate > daily.play_3s_rate).sum()),
    'play_over_above_5s': int((daily.play_over_rate > daily.play_5s_rate).sum()),
    'negative_average_watch': int((daily.play_duration_avg < 0).sum()),
}
invalid_attention = (
    daily[['play_3s_rate','play_5s_rate','play_over_rate']].gt(1).any(axis=1)
    | daily[['play_3s_rate','play_5s_rate','play_over_rate']].lt(0).any(axis=1)
    | (daily.play_5s_rate > daily.play_3s_rate)
    | (daily.play_over_rate > daily.play_5s_rate)
    | (daily.play_duration_avg < 0)
)
assert int(invalid_attention.sum()) == scoring['invalid_attention_rows']

verification = {
    'status': 'all_assertions_passed',
    'daily_rows': len(daily),
    'days': daily.date.nunique(),
    'unique_daily_material_keys': int(len(daily.drop_duplicates(['date','material_uri']))),
    'unique_materials': daily.material_uri.nunique(),
    'click_integer_reconstruction_max_abs_residual': float(click_residual.max()),
    'click_integer_reconstruction_p99_abs_residual': float(click_residual.quantile(.99)),
    'event_integer_reconstruction_max_abs_residual': float(event_residual.max()),
    'event_integer_reconstruction_p99_abs_residual': float(event_residual.quantile(.99)),
    'attention_invalid_reason_counts_not_mutually_exclusive': attention_reasons,
    'priority_rows': len(priority),
    'priority_gates_rechecked': True,
    'top20_rows': len(top20),
    'top20_links_rechecked': True,
}
(OUT/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(verification,ensure_ascii=False,indent=2))
print('\nATTENTION_EXAMPLES')
print(daily.loc[invalid_attention,['date','material_uri','title','video_duration','play_3s_rate','play_5s_rate','play_over_rate','play_duration_avg']].head(12).to_string(index=False))
