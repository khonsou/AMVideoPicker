import { useState } from 'react'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, ArrowDownRight, ArrowUpRight } from 'lucide-react'
import type { PeriodMetric } from '@/types/dashboard'
import { formatPercent } from '@/utils/format'

type MetricKey = 'ctr' | 'play3s' | 'playOver'
const metricConfig: Record<MetricKey, { label: string; domain: number[] }> = {
  ctr: { label: '点击率', domain: [0, 0.05] },
  play3s: { label: '看到 3 秒比例', domain: [0, 0.45] },
  playOver: { label: '看完比例', domain: [0, 0.08] },
}

export function PeriodPanel({ periods }: { periods: PeriodMetric[] }) {
  const [metric, setMetric] = useState<MetricKey>('ctr')
  const config = metricConfig[metric]
  const previous = periods[1][metric]
  const current = periods[2][metric]
  const change = previous && current ? current / previous - 1 : 0
  return (
    <section className="panel period-panel quality-period-panel" aria-labelledby="period-title">
      <div className="panel-heading">
        <div><span className="panel-kicker"><Activity size={15} />行业质量趋势</span><h2 id="period-title">行业{config.label}走势</h2></div>
        <span className={`trend-badge ${change < 0 ? 'down' : 'up'}`}>{change < 0 ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />}{(change * 100).toFixed(1)}%</span>
      </div>
      <div className="metric-switch" role="tablist" aria-label="趋势指标">{(Object.keys(metricConfig) as MetricKey[]).map(key => <button key={key} role="tab" aria-selected={metric === key} className={metric === key ? 'active' : ''} onClick={() => setMetric(key)}>{metricConfig[key].label}</button>)}</div>
      <div className="period-chart" role="img" aria-label={`三个二十八天周期的行业${config.label}折线图`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={periods} margin={{ top: 22, right: 24, bottom: 0, left: 2 }}>
            <CartesianGrid vertical={false} stroke="rgba(148,163,184,.12)" />
            <XAxis dataKey="period" tick={{ fill: '#8290a9', fontSize: 12 }} tickLine={false} axisLine={false} />
            <YAxis domain={config.domain} tickFormatter={value => `${(value * 100).toFixed(0)}%`} tick={{ fill: '#8290a9', fontSize: 12 }} tickLine={false} axisLine={false} />
            <Tooltip formatter={(value) => [`${(Number(value) * 100).toFixed(2)}%`, config.label]} contentStyle={{ background: '#151e31', border: '1px solid #2b3a55', borderRadius: 10, color: '#edf3ff' }} />
            <Line type="monotone" dataKey={metric} stroke="#55d6be" strokeWidth={3} dot={{ r: 6, fill: '#55d6be', strokeWidth: 0 }} activeDot={{ r: 8 }} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="quality-chart-foot"><span>第 3 期观看数据可用比例</span><strong>{formatPercent(periods[2].qualityCoverage, 1)}</strong><p>只保留质量趋势，不再展示投放量曲线。</p></div>
    </section>
  )
}
