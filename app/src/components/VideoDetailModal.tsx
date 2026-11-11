import { useEffect, useRef } from 'react'
import { ExternalLink, TrendingUp, X } from 'lucide-react'
import type { VideoMetric } from '@/types/dashboard'
import { formatChange, formatInt, formatPercent } from '@/utils/format'

interface Props { video: VideoMetric; onClose: () => void }
const trend = (value: number | null) => value === null ? '不可比' : formatChange(value)

export function VideoDetailModal({ video, onClose }: Props) {
  const dialogRef = useRef<HTMLDivElement>(null)
  const closeRef = useRef<HTMLButtonElement>(null)

  useEffect(() => {
    const previousOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    closeRef.current?.focus()
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
      if (event.key === 'Tab' && dialogRef.current) {
        const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button, a[href], summary, [tabindex="0"]'))
        const first = focusable[0]
        const last = focusable[focusable.length - 1]
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus() }
        if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus() }
      }
    }
    document.addEventListener('keydown', handleKey)
    return () => { document.body.style.overflow = previousOverflow; document.removeEventListener('keydown', handleKey) }
  }, [onClose])

  const currentMetrics = [
    ['当前点击率', formatPercent(video.ctr, 2)], ['当前看完比例', formatPercent(video.playOver, 2)],
    ['看到 3 秒比例', formatPercent(video.play3s, 2)], ['看到 5 秒比例', formatPercent(video.play5s, 2)],
    ['平均观看时长', video.avgWatch === null ? '—' : `${video.avgWatch.toFixed(2)} 秒`],
    ['观看数据可用比例', formatPercent(video.qualityCoverage, 1)],
  ]
  const growthRows = [
    { label: '点击率', previous: formatPercent(video.p2Ctr, 2), current: formatPercent(video.p3Ctr, 2), change: trend(video.ctrChange) },
    { label: '看完比例', previous: '—', current: '—', change: trend(video.playOverChange) },
    { label: '看到 3 秒比例', previous: '—', current: '—', change: trend(video.play3sChange) },
  ]
  return (
    <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose() }}>
      <div className="video-modal" role="dialog" aria-modal="true" aria-labelledby="video-modal-title" ref={dialogRef}>
        <div className="modal-topline"><span className="category-pill">{video.category}</span><button className="icon-button" onClick={onClose} ref={closeRef} aria-label="关闭素材详情"><X size={20} /></button></div>
        <h2 id="video-modal-title">{video.title}</h2>
        <p className="modal-subtitle">{video.duration ?? '—'} 秒 · 只评价内容质量，不判断赚钱</p>
        <div className="plain-summary"><strong>一句话看这条素材</strong><p>{video.plainSummary}</p></div>

        <section className="detail-section"><h3>最重要：质量有没有变好</h3><div className="priority-metrics"><div><span>点击率变化</span><strong className={video.ctrChange !== null && video.ctrChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.ctrChange)}</strong></div><div><span>看完比例变化</span><strong className={video.playOverChange !== null && video.playOverChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.playOverChange)}</strong></div></div><div className="quality-trend-note">{video.qualityTrend === null ? '两期观看数据不足或覆盖率低于 50%，不能判断共同改善。' : `两项变化中较小的一项为 ${trend(video.qualityTrend)}；两期观看数据覆盖为 ${formatPercent(video.p2QualityCoverage, 0)}／${formatPercent(video.p3QualityCoverage, 0)}。`}</div></section>

        <section className="detail-section"><h3>其次：现在的观看和点击表现</h3><div className="detail-metrics">{currentMetrics.map(([label, value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div></section>

        <section className="detail-section">
          <div className="growth-title"><h3><TrendingUp size={17} />前后 28 天，怎么变</h3><span className={video.growthComparable ? 'comparable' : 'not-comparable'}>{video.growthComparable ? '前后可比较' : '前后数据不足'}</span></div>
          <div className="growth-table" role="table" aria-label="前后二十八天质量指标变化">
            <div className="growth-row header" role="row"><span>指标</span><span>前 28 天</span><span>后 28 天</span><span>变化</span></div>
            {growthRows.map(row => <div className="growth-row" role="row" key={row.label}><strong>{row.label}</strong><span>{row.previous}</span><span>{row.current}</span><span className={row.change.startsWith('-') ? 'negative-text' : 'positive-text'}>{row.change}</span></div>)}
          </div>
          <p className="growth-note">前期在榜 {video.p2Days} 天，后期在榜 {video.p3Days} 天；没进榜不当成零。变化用于判断趋势，不代表投放金额或销售结果。</p>
        </section>

        <details className="secondary-details"><summary>辅助信息（不用于主排序）</summary><div className="auxiliary-content"><p>广告展示 {formatInt(video.impressions)} 次，点击 {formatInt(video.clicks)} 次；平台估算目标行为 {formatInt(video.conversions)} 次，点击后转化率 {formatPercent(video.cvr, 2)}。目标行为的具体含义仍待确认，因此不用于视频质量主榜。</p><p>每千次广告展示目标行为 {video.ipm?.toFixed(2) ?? '—'}，保守估算效率 {video.conservativeIndex === null ? '—' : `${(video.conservativeIndex / 100).toFixed(1)}×`}</p>{video.peopleTags.length > 0 && <div className="detail-block"><h3>人群标签</h3><div className="tag-list">{video.peopleTags.slice(0, 10).map(tag => <span key={tag}>{tag}</span>)}</div></div>}{video.materialTags.length > 0 && <div className="detail-block"><h3>内容标签</h3><div className="tag-list muted">{video.materialTags.slice(0, 12).map(tag => <span key={tag}>{tag}</span>)}</div></div>}</div></details>
        <a className="primary-button modal-cta" href={video.videoUrl} target="_blank" rel="noreferrer">去云图查看这条视频 <ExternalLink size={17} /></a>
      </div>
    </div>
  )
}
