const fs = require('fs');
const path = require('path');
const echarts = require('echarts');

const root = __dirname;
const assets = path.join(root, 'report_assets');
const data = JSON.parse(fs.readFileSync(path.join(assets, 'chart_data.json'), 'utf8'));
const C = {blue:'#2F6BFF', green:'#16A085', orange:'#F5A623', red:'#E15759', gray:'#8A94A6', text:'#17233D', light:'#E8EDF5'};
const base = {
  backgroundColor:'#FFFFFF', animation:false,
  textStyle:{fontFamily:'PingFang SC, Microsoft YaHei, Arial, sans-serif',color:C.text},
  title:{textStyle:{fontSize:26,fontWeight:700,color:C.text},subtextStyle:{fontSize:14,color:'#64748B',lineHeight:22}},
};
function merge(a,b){
  const out = {...a,...b};
  if(a.title||b.title) out.title={...a.title,...b.title};
  return out;
}
function render(name,option,width=1400,height=850){
  const chart=echarts.init(null,null,{renderer:'svg',ssr:true,width,height});
  chart.setOption(merge(base,option));
  fs.writeFileSync(path.join(assets,name),chart.renderToSVGString(),'utf8');
  chart.dispose();
  console.log(name);
}
const fmtWan = v => v>=1e8?(v/1e8).toFixed(2)+' 亿':v>=1e4?(v/1e4).toFixed(1)+' 万':String(v);

const nodes = [
  ['原始日榜\n504,000 行',0.5,0.7,C.gray],['质量闸门\n去重·异常·缺失',1.5,0.7,C.orange],
  ['同层效率\n品类×时长×收缩',2.5,0.7,C.blue],['候选分层\n复投·验证·衰退',3.5,0.7,C.green],
  ['随机复投实验\n同人群·同周期·SRM',2.5,2.2,C.orange],['财务与增量ROI\n净收入·毛利·留白',3.5,2.2,C.blue],
].map((n,i)=>({name:n[0],value:[n[1],n[2]],itemStyle:{color:n[3],opacity:i<4?0.92:0.82}}));
render('01_evaluation_framework.svg',{
  title:{text:'3C 短视频 ROI 评估：从榜单代理到因果与财务闭环',subtext:'主排名回答“谁值得进入复投”，实验与财务数据才回答“谁真正创造增量利润”',left:36,top:24},
  grid:{left:70,right:70,top:145,bottom:70},
  xAxis:{show:false,type:'value',min:0,max:4},
  yAxis:{show:false,type:'value',min:0,max:3,inverse:true},
  series:[{type:'graph',coordinateSystem:'cartesian2d',layout:'none',roam:false,symbol:'roundRect',symbolSize:[180,68],
    label:{show:true,fontSize:15,fontWeight:600,color:'#FFFFFF',lineHeight:23},
    edgeSymbol:['none','arrow'],edgeSymbolSize:[0,12],lineStyle:{color:'#94A3B8',width:2.2,curveness:0.08},data:nodes,
    links:[{source:nodes[0].name,target:nodes[1].name},{source:nodes[1].name,target:nodes[2].name},{source:nodes[2].name,target:nodes[3].name},
      {source:nodes[3].name,target:nodes[4].name},{source:nodes[4].name,target:nodes[5].name}]
  }]
},1200,720);

render('02_funnel_and_period.svg',{
  title:{text:'质量门槛后的转化代理漏斗与分期变化',subtext:'转化是平台事件当量，不等同支付订单；IPM＝每千次曝光转化事件数',left:36,top:24},
  legend:{show:false},
  grid:{left:'58%',right:'7%',top:'28%',bottom:'18%'},
  xAxis:{type:'category',data:data.periods.map(x=>x.period),name:'84 天窗口的三个 28 天分期',nameLocation:'middle',nameGap:38,axisLabel:{fontSize:13}},
  yAxis:{type:'value',name:'IPM（事件／千次曝光）',min:0,max:2,axisLabel:{formatter:v=>v.toFixed(1)}},
  series:[
    {name:'漏斗',type:'funnel',left:'5%',top:'20%',bottom:'12%',width:'39%',minSize:'12%',maxSize:'88%',sort:'descending',gap:8,
      label:{show:true,position:'right',fontSize:14,fontWeight:600,color:C.text,lineHeight:22,formatter:p=>p.name+'\n'+fmtWan(p.value)},labelLine:{length:24,lineStyle:{color:'#94A3B8'}},
      data:[{name:'曝光',value:data.funnel.impressions,itemStyle:{color:C.blue}},{name:'点击',value:data.funnel.clicks,itemStyle:{color:C.green}},{name:'转化事件当量',value:data.funnel.conversions,itemStyle:{color:C.orange}}]},
    {name:'IPM',type:'line',smooth:false,symbol:'circle',symbolSize:12,lineStyle:{width:4,color:C.blue},itemStyle:{color:C.blue},
      label:{show:true,position:'top',fontSize:16,fontWeight:700,formatter:p=>p.value.toFixed(3)},data:data.periods.map(x=>Number(x.ipm.toFixed(3)))}
  ],
  graphic:[{type:'text',left:'7%',bottom:24,style:{text:`整体 CTR ${(100*data.funnel.clicks/data.funnel.impressions).toFixed(2)}%　｜　整体点击后 CVR ${(100*data.funnel.conversions/data.funnel.clicks).toFixed(2)}%　｜　整体 IPM ${(1000*data.funnel.conversions/data.funnel.impressions).toFixed(3)}`,fontSize:15,fill:'#475569'}}]
},1400,820);

render('03_top_efficiency.svg',{
  title:{text:'效率优先 Top 10：90% 可信下界同层指数',subtext:'同层基准＝100；6,929 表示保守估计约为同品类、同时长组基准的 69.3 倍，并非 ROI 倍数',left:36,top:24},
  grid:{left:280,right:150,top:130,bottom:80},
  xAxis:{type:'value',name:'保守效率指数（同层＝100）',nameLocation:'middle',nameGap:42,splitLine:{lineStyle:{color:C.light}}},
  yAxis:{type:'category',data:data.bar.map(x=>x.title),axisLabel:{fontSize:13,width:250,overflow:'truncate'},axisTick:{show:false}},
  series:[{type:'bar',barWidth:26,data:data.bar.map(x=>({value:x.index,name:x.fullTitle,itemStyle:{color:C.blue,borderRadius:[0,6,6,0]}})),
    label:{show:true,position:'right',fontSize:13,fontWeight:700,formatter:p=>(p.value/100).toFixed(1)+'×'},
    markLine:{silent:true,symbol:'none',lineStyle:{color:C.red,type:'dashed',width:2},label:{show:true,position:'end',formatter:'同层基准 100',color:C.red},data:[{xAxis:100}]}
  }]
},1500,880);

render('04_scale_efficiency_map.svg',{
  title:{text:'规模—效率地图：高曝光不自动等于高效率',subtext:'横轴为榜内累计曝光（对数），纵轴为 IPM（对数）；点大小代表转化事件当量',left:36,top:24},
  legend:{top:100,left:40,itemWidth:16,itemHeight:10,textStyle:{fontSize:14}},
  grid:{left:100,right:70,top:160,bottom:90},
  xAxis:{type:'log',name:'累计曝光（次，对数坐标）',nameLocation:'middle',nameGap:42,min:10000,splitLine:{lineStyle:{color:C.light}},axisLabel:{formatter:v=>fmtWan(v)}},
  yAxis:{type:'log',name:'IPM（事件／千次曝光，对数坐标）',nameLocation:'middle',nameGap:58,min:0.05,splitLine:{lineStyle:{color:C.light}}},
  series:data.scatter.map(s=>({name:s.name,type:'scatter',data:s.data.map(d=>({name:d.name,value:d.value})),itemStyle:{color:s.color,opacity:s.name==='优先候选'?0.68:0.35},
    symbolSize:v=>Math.max(3,Math.min(17,3+Math.sqrt(v[2])/18)),
    markLine:s.name==='优先候选'?{silent:true,symbol:'none',lineStyle:{color:C.orange,type:'dashed'},label:{fontSize:12,color:'#B45309'},data:[{xAxis:100000,name:'规模门槛'},{yAxis:1000*data.funnel.conversions/data.funnel.impressions,name:'整体IPM'}]}:undefined
  }))
},1450,900);

render('05_temporal_validation.svg',{
  title:{text:'时间切分稳健性：前 56 天发现，后 28 天复核',subtext:`双对数坐标；同层基准按各期分别估计。可测试素材的 Spearman ρ＝${data.temporalSummary.train_test_spearman_all_testable.toFixed(3)}；缺失榜单不补零`,left:36,top:24},
  legend:{top:105,left:40,textStyle:{fontSize:14}},
  grid:{left:105,right:65,top:165,bottom:90},
  xAxis:{type:'log',name:'前 56 天收缩效率指数（同层＝100）',nameLocation:'middle',nameGap:44,min:1,splitLine:{lineStyle:{color:C.light}}},
  yAxis:{type:'log',name:'后 28 天原始效率指数（同层＝100）',nameLocation:'middle',nameGap:62,min:1,splitLine:{lineStyle:{color:C.light}}},
  series:data.temporal.map((s,i)=>({name:s.name,type:'scatter',data:s.data.map(d=>({name:d.name,value:d.value})),itemStyle:{color:s.color,opacity:i?0.78:0.28},symbolSize:i?8:4,
    markLine:i===0?{silent:true,symbol:'none',lineStyle:{color:C.red,type:'dashed'},label:{fontSize:12,color:C.red},data:[{xAxis:100},{yAxis:100}]}:undefined
  }))
},1450,900);
