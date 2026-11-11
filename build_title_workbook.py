from pathlib import Path
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'outputs'
base=pd.read_csv(OUT/'title_analysis_base.csv',low_memory=False)
base=base[base.growthComparable & base.qualityTrend.notna()].copy()
assert len(base)==507
wb=Workbook()
wb.remove(wb.active)
ACCENT='2F6BFF'
DARK='17365D'
LIGHT='EAF1FF'
MUTED='64748B'
INPUT_BLUE='0000CC'
FORMULA_BLACK='000000'
EXTERNAL_RED='CC0000'
THIN=Side(style='thin',color='D9E2F2')


def setup(ws, freeze='A2'):
    ws.sheet_view.showGridLines=False
    ws.freeze_panes=freeze
    ws.sheet_properties.pageSetUpPr.fitToPage=True
    ws.page_setup.fitToWidth=1
    ws.page_setup.fitToHeight=0


def title(ws, text, end_col=8):
    ws.merge_cells(start_row=1,start_column=2,end_row=1,end_column=end_col)
    c=ws.cell(1,2,text)
    c.font=Font(name='PingFang SC',size=18,bold=True,color=DARK)
    c.alignment=Alignment(vertical='center')
    ws.row_dimensions[1].height=34


def header(ws,row,cols,start_col=2):
    for i,value in enumerate(cols,start_col):
        c=ws.cell(row,i,value)
        c.font=Font(name='PingFang SC',bold=True,color='FFFFFF')
        c.fill=PatternFill('solid',fgColor=DARK)
        c.alignment=Alignment(horizontal='center',vertical='center',wrap_text=True)
        c.border=Border(bottom=THIN)
    ws.row_dimensions[row].height=30


def body_style(cell,formula=False,wrap=False,center=False):
    if isinstance(cell.value,str) and cell.value.startswith('#'):
        cell.value="'"+cell.value
    if isinstance(cell.value,str) and not cell.value.startswith('='):
        cell.data_type='s'
    cell.font=Font(name='PingFang SC',size=10,color=FORMULA_BLACK if formula else INPUT_BLUE)
    cell.alignment=Alignment(vertical='center',horizontal='center' if center else 'left',wrap_text=wrap)
    cell.border=Border(bottom=THIN)

# Source data with Excel formulas for all derived fields.
ws=wb.create_sheet('素材数据')
setup(ws,'A2')
cols=['标题','品类','时长（秒）','质量趋势','点击率变化','看完比例变化','当前点击率','当前看完比例','看到3秒比例','观看数据覆盖率','视频链接','标题长度','疑问或反问','包含数字','具体优惠','人群场景','痛点问题','实测证明','行动引导','口语悬念','功能利益','双升','当前双高','高双升','低基数反弹','话题标签数']
header(ws,1,cols)
base=base.sort_values('qualityTrend',ascending=False).reset_index(drop=True)
feature_patterns={
    '具体优惠':['优惠','补贴','福利','到手','直降','降价','特价','秒杀','包邮','免息','赠送','赠','送','活动','大促','双11','双十一','券','价格','价位','百元','千元','折'],
    '人群场景':['学生党','打工人','女生','男生','新手','小白','租房','出差','户外','旅行','办公','游戏','孩子','家长','妈妈','职场','宿舍','汗手','手小','苹果用户','华为','小米','果粉','开学','上班','出门','家用','别墅','食堂','情侣','礼物'],
    '痛点问题':['不够用','不会','不懂','不知道','怕','麻烦','踩坑','智商税','卡顿','手疼','手小','汗手','笨重','噪音','噪声','吵','没电','来不及','焦虑','难选','纠结','痛','难','愁','烦','晕','醒','废','亏','慌','累','堵','漏','掉线','断','模糊','发烫','热'],
    '实测证明':['实测','测评','评测','对比','挑战','演示','教程','教你','秒懂','一分钟','开箱','体验','亲测','试一','试用','检验','实验','拆解','上手'],
    '行动引导':['直播间','快来','点击','下单','入手','别错过','赶紧','冲冲','去看看','来买','秒杀','抢购','预约','锁定','来看','速来','快点','码住','安排'],
    '口语悬念':['真的','居然','竟然','谁懂','别再','不是吧','太','绝','神器','天花板','神仙','拿捏','绝绝子','没想到','震惊','离谱','原来','这才','难怪','坦白','求求','拜托','听劝','哇','哦','哟','嘛','啦','呀','啊','哈'],
    '功能利益':['提速','省电','轻巧','便携','续航','降噪','清晰','快充','不伤','防滑','稳定','流畅','简单','轻松','解放','省时','省钱','大容量','多功能','网速','信号','画质','音质','舒适','好用','耐用','护眼','智能','精准','高效','安全','干净','清洁','自由','兼容','降温','低温','防水','防尘','防摔','收纳','免费','好看','高颜值'],
}
for idx,r in base.iterrows():
    row=idx+2
    raw=[r.title,r.category,float(r.duration),float(r.qualityTrend),float(r.ctrChange),float(r.playOverChange),float(r.ctr),float(r.playOver),float(r.play3s),float(r.qualityCoverage),r.videoUrl]
    for col,value in enumerate(raw,2):
        ws.cell(row,col,value)
        body_style(ws.cell(row,col),wrap=(col in [2,11]))
    ws.cell(row,13,f'=LEN(B{row})')
    question_words=['怎么','怎样','如何','为什么','什么','谁','哪','吗','呢']
    question_checks=','.join(f'ISNUMBER(SEARCH("{word}",B{row}))' for word in question_words)
    ws.cell(row,14,f'=IF(OR(ISNUMBER(SEARCH("？",B{row})),ISNUMBER(SEARCH("~?",B{row})),{question_checks}),1,0)')
    digits=['0','1','2','3','4','5','6','7','8','9']
    digit_checks=','.join(f'ISNUMBER(SEARCH("{digit}",B{row}))' for digit in digits)
    ws.cell(row,15,f'=IF(OR({digit_checks}),1,0)')
    for col,name in [(16,'具体优惠'),(17,'人群场景'),(18,'痛点问题'),(19,'实测证明'),(20,'行动引导'),(21,'口语悬念'),(22,'功能利益')]:
        words=feature_patterns[name]
        checks=','.join(f'ISNUMBER(SEARCH("{word}",B{row}))' for word in words)
        ws.cell(row,col,f'=IF(OR({checks}),1,0)')
    ws.cell(row,23,f'=IF(E{row}>0,1,0)')
    ws.cell(row,24,f'=IF(AND(H{row}>=MEDIAN($H$2:$H$508),I{row}>=MEDIAN($I$2:$I$508)),1,0)')
    ws.cell(row,25,f'=IF(AND(W{row}=1,X{row}=1),1,0)')
    ws.cell(row,26,f'=IF(AND(W{row}=1,X{row}=0),1,0)')
    ws.cell(row,27,f'=LEN(B{row})-LEN(SUBSTITUTE(B{row},"#",""))')
    for col in range(13,28): body_style(ws.cell(row,col),formula=True,center=True)
    for col in [4,5,6,10]: ws.cell(row,col).number_format='0.00%'
    for col in [7,8,9]: ws.cell(row,col).number_format='0.00%'
    for col in [4,5,6]: ws.cell(row,col).number_format='+0.0%;-0.0%;0.0%'
ws.auto_filter.ref=f'A1:AA{len(base)+1}'
widths={2:62,12:42}
for col in range(2,28): ws.column_dimensions[get_column_letter(col)].width=widths.get(col,14)
ws.column_dimensions['B'].width=62
ws.column_dimensions['L'].width=42
ws.column_dimensions['M'].width=12

# Summary sheet with formula-driven KPI values.
ws=wb.create_sheet('摘要',0)
setup(ws,'B2')
title(ws,'高排名标题学习摘要',8)
summary_rows=[
    ('双升素材（点击率与看完比例同时上升）','=COUNTIF(素材数据!$W$2:$W$508,1)','趋势改善，但还要看当前水平'),
    ('高双升素材','=COUNTIF(素材数据!$Y$2:$Y$508,1)','趋势与当前表现均高于中位数，优先学习'),
    ('低基数反弹素材','=COUNTIF(素材数据!$Z$2:$Z$508,1)','涨幅大但当前未达双高，不直接当模板'),
    ('非双升素材','=COUNTIF(素材数据!$W$2:$W$508,0)','作为标题特征对照组'),
    ['高双升平均标题长度','=AVERAGEIFS(素材数据!$M$2:$M$508,素材数据!$Y$2:$Y$508,1)','非双升平均长度见特征对比'],
]
header(ws,3,['指标','数量／数值','使用方式'])
for row_idx,(label,formula,note) in enumerate(summary_rows,4):
    ws.cell(row_idx,2,label); body_style(ws.cell(row_idx,2))
    ws.cell(row_idx,3,formula); body_style(ws.cell(row_idx,3),formula=True,center=True)
    ws.cell(row_idx,4,note); body_style(ws.cell(row_idx,4),wrap=True)
ws.cell(11,2,'核心结论')
ws.cell(11,2).font=Font(name='PingFang SC',size=13,bold=True,color=DARK)
conclusions=[
    '可学习的不是“问句越多越好”，而是具体功能利益、真实数字和可验证信息。',
    '高双升组的具体优惠、功能利益、数字信息占比均高于非双升组。',
    '疑问、人群标签、口语悬念并未呈现优势，不能把固定句式当万能公式。',
    '高双升只有 64 条；114 条属于低基数反弹，必须先检查当前点击率和看完比例。',
]
for i,text in enumerate(conclusions,12):
    ws.merge_cells(start_row=i,start_column=2,end_row=i,end_column=7)
    c=ws.cell(i,2,f'• {text}')
    c.font=Font(name='PingFang SC',size=11,color=DARK)
    c.alignment=Alignment(wrap_text=True,vertical='center')
    ws.row_dimensions[i].height=28
for col,width in {'A':3,'B':38,'C':18,'D':40,'E':12,'F':12,'G':12,'H':12}.items(): ws.column_dimensions[col].width=width

# Feature comparison with formulas and a real chart.
ws=wb.create_sheet('特征对比')
setup(ws,'A2')
title(ws,'高双升与非双升：标题特征对比',7)
header(ws,3,['标题特征','高双升占比','非双升占比','差值（百分点）','解释'])
features=['疑问或反问','包含数字','具体优惠','人群场景','痛点问题','实测证明','行动引导','口语悬念','功能利益']
col_map={'疑问或反问':'N','包含数字':'O','具体优惠':'P','人群场景':'Q','痛点问题':'R','实测证明':'S','行动引导':'T','口语悬念':'U','功能利益':'V'}
for i,name in enumerate(features,4):
    col=col_map[name]
    ws.cell(i,2,name); body_style(ws.cell(i,2))
    ws.cell(i,3,f'=COUNTIFS(素材数据!$Y$2:$Y$508,1,素材数据!${col}$2:${col}$508,1)/COUNTIF(素材数据!$Y$2:$Y$508,1)')
    ws.cell(i,4,f'=COUNTIFS(素材数据!$W$2:$W$508,0,素材数据!${col}$2:${col}$508,1)/COUNTIF(素材数据!$W$2:$W$508,0)')
    ws.cell(i,5,f'=(C{i}-D{i})*100')
    ws.cell(i,6,'仅描述关键词命中率差异，不证明因果')
    for c in range(3,7): body_style(ws.cell(i,c),formula=(c in [3,4,5],),wrap=(c==6))
    ws.cell(i,3).number_format='0.0%'; ws.cell(i,4).number_format='0.0%'; ws.cell(i,5).number_format='+0.0;-0.0;0.0'
length_row=13
ws.cell(length_row,2,'平均标题长度（字）'); body_style(ws.cell(length_row,2))
ws.cell(length_row,3,'=AVERAGEIFS(素材数据!$M$2:$M$508,素材数据!$Y$2:$Y$508,1)')
ws.cell(length_row,4,'=AVERAGEIFS(素材数据!$M$2:$M$508,素材数据!$W$2:$W$508,0)')
ws.cell(length_row,5,f'=C{length_row}-D{length_row}')
ws.cell(length_row,6,'高双升略短，但不构成独立写作规则')
for c in range(3,7): body_style(ws.cell(length_row,c),formula=(c in [3,4,5]),wrap=(c==6))
ws.cell(length_row,5).number_format='+0.0;-0.0;0.0'
for col,width in {'A':3,'B':24,'C':16,'D':16,'E':18,'F':42,'G':4}.items(): ws.column_dimensions[col].width=width
chart=BarChart()
chart.type='bar'
chart.style=10
chart.title='高双升与非双升的特征差值（百分点）'
chart.y_axis.title='标题特征'
chart.x_axis.title='高双升占比 − 非双升占比（百分点）'
chart.height=8.5
chart.width=17
chart.add_data(Reference(ws,min_col=5,min_row=3,max_row=12),titles_from_data=True)
chart.set_categories(Reference(ws,min_col=2,min_row=4,max_row=12))
chart.legend=None
chart.varyColors=False
chart.series[0].graphicalProperties.solidFill=ACCENT
ws.add_chart(chart,'B16')

# Robust examples.
ws=wb.create_sheet('高双升示例')
setup(ws,'A4')
title(ws,'高双升代表标题（按质量趋势排序）',12)
example_cols=['排名','标题','品类','质量趋势','点击率变化','看完比例变化','当前点击率','当前看完比例','看到3秒比例','数据覆盖率','时长（秒）','视频链接']
header(ws,3,example_cols)
robust=base[base.robust].nlargest(30,'qualityTrend')
for rank,(_,r) in enumerate(robust.iterrows(),1):
    row=rank+3
    values=[rank,r.title,r.category,float(r.qualityTrend),float(r.ctrChange),float(r.playOverChange),float(r.ctr),float(r.playOver),float(r.play3s),float(r.qualityCoverage),float(r.duration),r.videoUrl]
    for col,value in enumerate(values,2):
        ws.cell(row,col,value)
        body_style(ws.cell(row,col),wrap=(col in [3,12]))
    for col in [4,5,6]: ws.cell(row,col).number_format='+0.0%;-0.0%;0.0%'
    for col in [7,8,9,10]: ws.cell(row,col).number_format='0.00%'
ws.auto_filter.ref=f'A3:L{len(robust)+3}'
for col,width in {'A':5,'B':7,'C':66,'D':20,'E':14,'F':14,'G':15,'H':14,'I':14,'J':14,'K':14,'L':14,'M':42}.items(): ws.column_dimensions[col].width=width

# Practical guide.
ws=wb.create_sheet('标题学习指南')
setup(ws,'B2')
title(ws,'团队可复用的标题写法',7)
header(ws,3,['结构／规则','使用方式','注意边界'])
guide=[
    ('产品／功能＋明确利益＋可验证数字','把功能说成用户结果，并用真实参数、价格、数量或演示支撑。','数字必须真实可核验，不能编造性能。'),
    ('具体使用障碍＋产品解决方案','可以使用疑问，但必须是目标用户真实、具体的问题。','疑问句本身没有表现优势，不能为了提问而提问。'),
    ('真实优惠＋产品利益＋行动','优惠与使用利益同时出现，比只写“直播间福利”更具体。','价格、赠品、限时活动必须与当期真实活动一致。'),
    ('短一点，信息先于修饰','优先保留产品、利益、证据，删去无信息量的热词和堆叠标签。','高双升平均长度只是略短，不能机械限制字数。'),
    ('当前双高优先于涨幅','先确认当前点击率和看完比例，再学习上升趋势。','低基数反弹不能直接复制为“优质标题”。'),
    ('标题与视频共同验证','标题只负责承诺，视频必须快速兑现产品、功能或优惠。','同一标题的不同素材表现不同，不能归因于标题 alone。'),
]
for i,(a,b,c) in enumerate(guide,4):
    ws.cell(i,2,a); body_style(ws.cell(i,2),wrap=True)
    ws.cell(i,3,b); body_style(ws.cell(i,3),wrap=True)
    ws.cell(i,4,c); body_style(ws.cell(i,4),wrap=True)
    ws.row_dimensions[i].height=52
ws.cell(12,2,'推荐标题骨架')
ws.cell(12,2).font=Font(name='PingFang SC',size=13,bold=True,color=DARK)
frames=[
    '［具体使用障碍］？［产品］，［用户能感知的利益］，［可验证参数／演示］',
    '［目标人群／场景］，［产品］帮你［具体结果］，［真实数字或证据］',
    '［真实时间限定优惠］，［产品核心利益］，［真实价格／赠品／行动］',
]
for i,text in enumerate(frames,13):
    ws.merge_cells(start_row=i,start_column=2,end_row=i,end_column=6)
    c=ws.cell(i,2,text); c.font=Font(name='PingFang SC',size=11,color=DARK); c.alignment=Alignment(wrap_text=True)
    ws.row_dimensions[i].height=28
for col,width in {'A':3,'B':38,'C':58,'D':44,'E':12,'F':12,'G':4}.items(): ws.column_dimensions[col].width=width

# Source and method audit.
ws=wb.create_sheet('数据来源与口径')
setup(ws,'B2')
title(ws,'数据来源与计算口径',5)
header(ws,3,['项目','说明','Source URL'])
source_rows=[
    ('原始数据','当前工作区 outputs/h5_candidates_enriched.csv；846 条优先复核素材。','/Users/linan/Desktop/投放视频原始数据/outputs/h5_candidates_enriched.csv'),
    ('质量趋势可比','507 条：前后各至少 3 天在榜、展示各至少 20,000，且两期观看数据覆盖率均≥50%。','本地计算'),
    ('双升','质量趋势＝min（点击率变化，看完比例变化）＞0，共 178 条。','本地计算'),
    ('高双升','双升且当前点击率、当前看完比例均不低于质量趋势可比组各自中位数，共 64 条。','素材数据表 Y 列公式'),
    ('低基数反弹','双升但未达到当前双高，共 114 条。','素材数据表 Z 列公式'),
    ('特征识别','使用标题关键词命中，不是语义分类或因果推断。差异仅用于提出创意假设。','素材数据表 N–V 列公式'),
    ('可复算脚本','analyze_titles.py 与 build_title_workbook.py。','当前工作区'),
]
for i,(a,b,c) in enumerate(source_rows,4):
    ws.cell(i,2,a); body_style(ws.cell(i,2),wrap=True)
    ws.cell(i,3,b); body_style(ws.cell(i,3),wrap=True)
    ws.cell(i,4,c); body_style(ws.cell(i,4),wrap=True)
    ws.cell(i,4).font=Font(name='PingFang SC',size=10,color=EXTERNAL_RED)
    ws.row_dimensions[i].height=44
for col,width in {'A':3,'B':24,'C':72,'D':66,'E':4}.items(): ws.column_dimensions[col].width=width

path=OUT/'高双升标题学习清单.xlsx'
wb.save(path)
# Structural checks before recalculation.
check=load_workbook(path, data_only=False)
assert {'摘要','特征对比','高双升示例','标题学习指南','素材数据','数据来源与口径'}.issubset(set(check.sheetnames))
assert check['素材数据']['M2'].value=='=LEN(B2)'
assert check['摘要']['C5'].value=='=COUNTIF(素材数据!$Y$2:$Y$508,1)'
assert len(check['特征对比']._charts)==1 and check['特征对比']._charts[0].series
print(path)
