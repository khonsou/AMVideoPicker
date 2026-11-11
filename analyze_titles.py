import re
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
df=pd.read_csv(ROOT/'outputs'/'h5_candidates_enriched.csv',low_memory=False)
base=df[df.growthComparable & df.qualityTrend.notna()].copy()
median_ctr=base.ctr.median()
median_play=base.playOver.median()
base['rising']=base.qualityTrend>0
base['current_high']=(base.ctr>=median_ctr)&(base.playOver>=median_play)
base['robust']=base.rising&base.current_high
base['rebound']=base.rising&~base.current_high
print({'median_ctr':median_ctr,'median_playOver':median_play,'comparable':len(base),'rising':int(base.rising.sum()),'robust':int(base.robust.sum()),'rebound':int(base.rebound.sum()),'non_rising':int((~base.rising).sum())})

features={
    '疑问或反问':r'[?？]|怎么|怎样|如何|为什么|什么|谁|哪|吗|呢',
    '包含数字':r'\d',
    '具体优惠':r'优惠|补贴|福利|到手|直降|降价|降价|特价|秒杀|包邮|免息|赠送|赠|送|活动|大促|双11|双十一|券|价格|价位|百元|千元|折',
    '人群场景':r'学生党|打工人|女生|男生|新手|小白|租房|出差|户外|旅行|办公|游戏|孩子|家长|妈妈|职场|宿舍|汗手|手小|苹果用户|华为|小米|果粉|开学|上班|出门|家用|别墅|食堂|情侣|礼物',
    '痛点问题':r'不够用|不会|不懂|不知道|怕|麻烦|踩坑|智商税|卡顿|手疼|手小|汗手|笨重|噪音|噪声|吵|没电|来不及|焦虑|难选|纠结|痛|难|愁|烦|晕|醒|废|亏|慌|累|堵|漏|掉线|断|模糊|发烫|热',
    '实测证明':r'实测|测评|评测|对比|挑战|演示|教程|教你|秒懂|一分钟|开箱|体验|亲测|试一|试用|检验|实验|拆解|拆解|上手',
    '行动引导':r'直播间|快来|点击|下单|入手|别错过|赶紧|冲冲|去看看|来买|秒杀|抢购|预约|锁定|来看|速来|快点|快点|码住|安排',
    '口语悬念':r'真的|居然|竟然|谁懂|别再|不是吧|太|绝|神器|天花板|神仙|拿捏|绝绝子|没想到|震惊|离谱|原来|这才|难怪|坦白|求求|拜托|听劝|哇|哦|哟|嘛|啦|呀|啊|哈',
    '功能利益':r'提速|省电|轻巧|便携|续航|降噪|清晰|快充|不伤|防滑|稳定|流畅|简单|轻松|解放|省时|省钱|大容量|多功能|网速|信号|画质|音质|舒适|好用|耐用|护眼|智能|精准|高效|安全|干净|清洁|自由|兼容|降温|低温|快充|防水|防尘|防摔|收纳|免费|好看|高颜值',
}
for name,pattern in features.items():
    base[name]=base.title.fillna('').str.contains(pattern,regex=True)
base['标题长度']=base.title.fillna('').str.len()
base['话题标签数']=base.title.fillna('').str.count('#')
base['含表情符号']=base.title.fillna('').str.contains(r'[🍎🔥✨🎁🎉💡😎😭🤣🥰😍🤩🙌👍👏🙏💪🤔🤯😱🤫🤭🤤🥳🥵🥶🫠🫡🫣🫢🫨🫰🫵✅❌⭐🌟💯❗‼️]',regex=True)

compare=[]
for name in features:
    a=base.loc[base.robust,name].mean()
    b=base.loc[~base.rising,name].mean()
    compare.append({'feature':name,'robust_rate':a,'non_rising_rate':b,'difference_pp':(a-b)*100,'ratio':a/b if b>0 else np.nan})
print('\nFEATURE_COMPARISON\n',pd.DataFrame(compare).sort_values('difference_pp',ascending=False).to_string(index=False))
print('\nLENGTHS\n',base.groupby('robust')[['标题长度','话题标签数']].median().to_string())
cols=['title','category','qualityTrend','ctrChange','playOverChange','ctr','playOver','play3s','qualityCoverage','duration']
print('\nTOP_ROBUST\n',base[base.robust].nlargest(30,'qualityTrend')[cols].to_string(index=False))
print('\nTOP_REBOUND\n',base[base.rebound].nlargest(12,'qualityTrend')[cols].to_string(index=False))
base.to_csv(ROOT/'outputs'/'title_analysis_base.csv',index=False,encoding='utf-8-sig')
pd.DataFrame(compare).to_csv(ROOT/'outputs'/'title_feature_comparison.csv',index=False,encoding='utf-8-sig')
