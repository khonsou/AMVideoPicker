from pathlib import Path
import pandas as pd
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
base=pd.read_csv(OUT/'title_analysis_base.csv',low_memory=False)
base=base[base.growthComparable & base.qualityTrend.notna()].copy()
expected={'双升':int(base.rising.sum()),'高双升':int(base.robust.sum()),'低基数反弹':int(base.rebound.sum()),'非双升':int((~base.rising).sum())}
assert expected=={'双升':178,'高双升':64,'低基数反弹':114,'非双升':329}

verify=load_workbook(OUT/'高双升标题学习清单_recalc_verify.xlsx',data_only=True)
summary=verify['摘要']
actual={'双升':summary['C4'].value,'高双升':summary['C5'].value,'低基数反弹':summary['C6'].value,'非双升':summary['C7'].value}
assert actual==expected,(actual,expected)
print('分组数量核对',actual)

features=['疑问或反问','包含数字','具体优惠','人群场景','痛点问题','实测证明','行动引导','口语悬念','功能利益']
comparison=[]
for row,name in enumerate(features,4):
    excel_a=verify['特征对比'].cell(row,3).value
    excel_b=verify['特征对比'].cell(row,4).value
    raw_a=base.loc[base.robust,name].mean()
    raw_b=base.loc[~base.rising,name].mean()
    assert abs(excel_a-raw_a)<1e-6,(name,excel_a,raw_a)
    assert abs(excel_b-raw_b)<1e-6,(name,excel_b,raw_b)
    comparison.append({'特征':name,'高双升占比':round(excel_a*100,1),'非双升占比':round(excel_b*100,1),'差值pp':round((excel_a-excel_b)*100,1)})
print(pd.DataFrame(comparison).to_string(index=False))

original=load_workbook(OUT/'高双升标题学习清单.xlsx',data_only=False)
assert len(original['特征对比']._charts)==1 and original['特征对比']._charts[0].series
assert original['素材数据']['M2'].value=='=LEN(B2)'
assert original['摘要']['C5'].value=='=COUNTIF(素材数据!$Y$2:$Y$508,1)'
assert original['高双升示例'].max_row==33
formula_count=sum(1 for ws in original for row in ws.iter_rows() for cell in row if cell.data_type=='f')
assert formula_count>7000,formula_count
print('原始工作簿结构、图表与公式数量核对',{'formula_count':formula_count,'charts':1,'example_rows':30})
