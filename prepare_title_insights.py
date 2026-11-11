import json
import shutil
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
APP=ROOT/'app'
DATA_DIR=APP/'src'/'data'
DOWNLOAD_DIR=APP/'public'/'downloads'
DATA_DIR.mkdir(parents=True,exist_ok=True)
DOWNLOAD_DIR.mkdir(parents=True,exist_ok=True)

base=pd.read_csv(OUT/'title_analysis_base.csv',low_memory=False)
features=pd.read_csv(OUT/'title_feature_comparison.csv')
base=base[base.growthComparable & base.qualityTrend.notna()].copy()
rising=base[base.rising]
robust=base[base.robust]
rebound=base[base.rebound]
non_rising=base[~base.rising]
assert (len(rising),len(robust),len(rebound),len(non_rising))==(178,64,114,329)

feature_data=[]
for _,r in features.iterrows():
    feature_data.append({
        'name':r.feature,
        'robustRate':round(float(r.robust_rate),4),
        'nonRisingRate':round(float(r.non_rising_rate),4),
        'difference':round(float(r.difference_pp),1),
    })

examples=[]
for _,r in robust.nlargest(3,'qualityTrend').iterrows():
    examples.append({
        'title':r.title,'category':r.category,'qualityTrend':round(float(r.qualityTrend),4),
        'ctrChange':round(float(r.ctrChange),4),'playOverChange':round(float(r.playOverChange),4),
        'ctr':round(float(r.ctr),4),'playOver':round(float(r.playOver),4),
        'videoUrl':r.videoUrl,
    })

data={
    'summary':{'rising':len(rising),'robust':len(robust),'rebound':len(rebound),'nonRising':len(non_rising)},
    'features':feature_data,
    'examples':examples,
    'frameworks':[
        {'title':'具体障碍＋产品＋用户利益＋可验证信息','description':'疑问句只是形式，真正有用的是问题足够具体。数字、参数、价格、实测或演示必须真实可核验。'},
        {'title':'目标人群／场景＋产品结果＋证据','description':'先说明谁在什么场景遇到什么任务，再告诉用户产品能帮助完成什么结果。'},
        {'title':'真实优惠＋产品利益＋真实行动','description':'优惠与使用利益同时出现，比只写“直播间福利”更具体；价格和赠品必须与当期活动一致。'},
    ],
}
content='import type { TitleInsightData } from \'@/types/titleInsights\'\n\nexport const titleInsights: TitleInsightData = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
(DATA_DIR/'titleInsights.ts').write_text(content,encoding='utf-8')
shutil.copy2(OUT/'高双升标题学习清单.xlsx',DOWNLOAD_DIR/'高双升标题学习清单.xlsx')
print(json.dumps({'features':len(feature_data),'examples':len(examples),'summary':data['summary']},ensure_ascii=False))
