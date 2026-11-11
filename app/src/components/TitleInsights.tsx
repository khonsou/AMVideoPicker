import {
  Bar, BarChart, CartesianGrid, Cell, LabelList, ReferenceLine,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import { AlertTriangle, Download, Lightbulb, TrendingUp } from 'lucide-react'
import { titleInsights } from '@/data/titleInsights'
import type { TitleFeature } from '@/types/titleInsights'
import { formatChange, formatPercent } from '@/utils/format'

function FeatureTooltip({ active, payload }: { active?: boolean; payload?: Array<{ payload: TitleFeature }> }) {
  if (!active || !payload?.length) return null
  const feature = payload[0].payload
  return <div className="chart-tooltip"><strong>{feature.name}</strong><p>高双升：{formatPercent(feature.robustRate, 1)}</p><p>非双升：{formatPercent(feature.nonRisingRate, 1)}</p><p>差值：{feature.difference > 0 ? '+' : ''}{feature.difference.toFixed(1)} 个百分点</p></div>
}

export function TitleInsights() {
  const { summary, features, examples, frameworks } = titleInsights
  return (
    <section className="insights-section" id="title-insights" aria-labelledby="insights-title">
      <div className="section-heading">
        <div><span className="section-label">标题学习</span><h2 id="insights-title">高排名标题，值得学什么？</h2><p>不是背句式，而是学习怎样把利益、证据和真实活动说清楚。</p></div>
        <a className="download-link" href="./downloads/高双升标题学习清单.xlsx" download><Download size={17} />下载完整学习清单</a>
      </div>
      <div className="insight-summary">
        <div><strong>{summary.robust}</strong><span>高双升，优先学习</span></div>
        <div><strong>{summary.rebound}</strong><span>低基数反弹，先别照搬</span></div>
        <div><strong>{summary.nonRising}</strong><span>非双升对照组</span></div>
      </div>
      <div className="insights-grid">
        <div className="panel feature-panel">
          <div className="panel-heading"><div><span className="panel-kicker"><TrendingUp size={15} />特征对比</span><h3>哪些标题信息更值得关注</h3></div></div>
          <p className="panel-description">高双升占比 − 非双升占比，单位为个百分点；只描述差异，不证明因果。</p>
          <div className="feature-chart" role="img" aria-label="高双升与非双升标题特征差值图">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={features} layout="vertical" margin={{ top: 12, right: 58, left: 8, bottom: 12 }}>
                <CartesianGrid horizontal={false} stroke="rgba(148,163,184,.12)" />
                <XAxis type="number" domain={[-6, 8]} tick={{ fill: '#8290a9', fontSize: 12 }} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="name" width={92} tick={{ fill: '#a9b6cc', fontSize: 12 }} tickLine={false} axisLine={false} />
                <Tooltip content={<FeatureTooltip />} cursor={{ fill: 'rgba(76,131,255,.08)' }} />
                <ReferenceLine x={0} stroke="#64748B" />
                <Bar dataKey="difference" radius={[0, 5, 5, 0]} isAnimationActive={false}>
                  {features.map(feature => <Cell key={feature.name} fill={feature.difference >= 0 ? '#55d6be' : '#f5a623'} />)}
                  <LabelList dataKey="difference" position="right" />
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="framework-panel">
          <div className="panel-heading"><div><span className="panel-kicker"><Lightbulb size={15} />可复用结构</span><h3>三条标题骨架</h3></div></div>
          <div className="framework-list">{frameworks.map((item, index) => <article key={item.title}><span>{String(index + 1).padStart(2, '0')}</span><div><h4>{item.title}</h4><p>{item.description}</p></div></article>)}</div>
        </div>
      </div>
      <div className="example-section">
        <div className="example-heading"><h3>三个代表标题</h3><span>当前表现与前后变化同时展示，避免只看涨幅。</span></div>
        <div className="example-list">{examples.map(example => <article key={example.title}><div className="example-title"><span className="table-category">{example.category}</span><h4>{example.title}</h4></div><div className="example-metrics"><span>当前点击率 <strong>{formatPercent(example.ctr, 2)}</strong></span><span>当前看完 <strong>{formatPercent(example.playOver, 2)}</strong></span><span>点击率变化 <strong>{formatChange(example.ctrChange)}</strong></span><span>看完变化 <strong>{formatChange(example.playOverChange)}</strong></span><a href={example.videoUrl} target="_blank" rel="noreferrer">查看视频</a></div></article>)}</div>
      </div>
      <div className="insight-note"><AlertTriangle size={18} /><p>标题只负责承诺，视频必须在前 3–5 秒兑现。空泛悬念和低基数反弹不能直接复制；同一标题的不同素材也可能表现不同。</p></div>
    </section>
  )
}
