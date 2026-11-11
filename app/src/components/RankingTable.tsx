import { useCallback, useMemo, useState } from 'react'
import { ChevronDown, Download, Search, SearchX, SlidersHorizontal } from 'lucide-react'
import type { VideoMetric } from '@/types/dashboard'
import { formatChange, formatInt, formatPercent, shortTitle } from '@/utils/format'
import { VideoDetailModal } from './VideoDetailModal'

type Mode = 'trend' | 'current'
type SortKey = 'qualityTrend' | 'ctrChange' | 'playOverChange' | 'ctr' | 'playOver' | 'play3s'
const trend = (value: number | null) => value === null ? '不可比' : formatChange(value)

export function RankingTable({ videos }: { videos: VideoMetric[] }) {
  const [mode, setMode] = useState<Mode>('trend')
  const [showAllComparable, setShowAllComparable] = useState(false)
  const [sortKey, setSortKey] = useState<SortKey>('qualityTrend')
  const [query, setQuery] = useState('')
  const [category, setCategory] = useState('全部品类')
  const [visible, setVisible] = useState(10)
  const [selected, setSelected] = useState<VideoMetric | null>(null)
  const closeModal = useCallback(() => setSelected(null), [])
  const categories = useMemo(() => ['全部品类', ...Array.from(new Set(videos.map(v => v.category))).sort((a, b) => a.localeCompare(b, 'zh-CN'))], [videos])

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    return videos.filter(video => {
      const matchesCategory = category === '全部品类' || video.category === category
      const matchesQuery = !normalized || `${video.title} ${video.uri} ${video.category}`.toLowerCase().includes(normalized)
      const matchesMode = mode === 'current' || (video.growthComparable && video.qualityTrend !== null && (showAllComparable || video.qualityTrend > 0))
      return matchesCategory && matchesQuery && matchesMode
    }).sort((a, b) => (b[sortKey] ?? -Infinity) - (a[sortKey] ?? -Infinity))
  }, [videos, query, category, sortKey, mode, showAllComparable])

  const switchMode = (next: Mode) => { setMode(next); setSortKey(next === 'trend' ? 'qualityTrend' : 'ctr'); setVisible(10) }
  const expectedCount = mode === 'current' ? 846 : showAllComparable ? 507 : 178

  return (
    <section className="ranking-section" id="ranking" aria-labelledby="ranking-title">
      <div className="section-heading ranking-heading">
        <div><span className="section-label">质量优先清单</span><h2 id="ranking-title">先看有没有变好，再看现在好不好</h2><p>{mode === 'trend' ? '优先展示点击率和看完比例同时上升的素材；展示量不再参与排序。' : '查看全部素材当前的点击率、看完比例和开头留存。'}</p></div>
        <a className="download-link" href="./downloads/h5_candidates_enriched.csv" download><Download size={17} />下载完整数据</a>
      </div>
      <div className="ranking-controls">
        <div className="mode-tabs" role="tablist" aria-label="榜单类型"><button role="tab" aria-selected={mode === 'trend'} className={mode === 'trend' ? 'active' : ''} onClick={() => switchMode('trend')}>质量趋势</button><button role="tab" aria-selected={mode === 'current'} className={mode === 'current' ? 'active' : ''} onClick={() => switchMode('current')}>当前表现</button></div>
        <label className="search-box"><Search size={18} /><input value={query} onChange={event => { setQuery(event.target.value); setVisible(10) }} placeholder="搜索标题或素材编号" aria-label="搜索标题或素材编号" /></label>
        <label className="select-box"><SlidersHorizontal size={17} /><select value={category} onChange={event => { setCategory(event.target.value); setVisible(10) }} aria-label="按品类筛选">{categories.map(item => <option key={item}>{item}</option>)}</select><ChevronDown size={16} /></label>
        <label className="select-box sort-select"><select value={sortKey} onChange={event => setSortKey(event.target.value as SortKey)} aria-label="排序指标">{mode === 'trend' ? <><option value="qualityTrend">按共同改善</option><option value="ctrChange">按点击率变化</option><option value="playOverChange">按看完比例变化</option></> : <><option value="ctr">按当前点击率</option><option value="playOver">按当前看完比例</option><option value="play3s">按看到 3 秒比例</option></>}</select><ChevronDown size={16} /></label>
      </div>
      {mode === 'trend' && <div className="scope-tabs" role="tablist" aria-label="趋势素材范围"><button role="tab" aria-selected={!showAllComparable} className={!showAllComparable ? 'active' : ''} onClick={() => { setShowAllComparable(false); setVisible(10) }}>只看双升 178</button><button role="tab" aria-selected={showAllComparable} className={showAllComparable ? 'active' : ''} onClick={() => { setShowAllComparable(true); setVisible(10) }}>全部质量可比 507</button></div>}
      <div className="result-summary"><span>当前显示 <strong>{formatInt(filtered.length)}</strong> 条{mode === 'trend' && filtered.length !== expectedCount ? '（已应用筛选）' : ''}</span><span>重要度：质量变化 ＞ 当前表现 ＞ 开头留存 ＞ 数据可信度</span></div>

      {filtered.length === 0 ? (
        <div className="empty-state"><SearchX size={34} /><h3>没有匹配的素材</h3><p>试试缩短关键词，或清除品类筛选。</p><button onClick={() => { setQuery(''); setCategory('全部品类') }}>清除筛选</button></div>
      ) : (
        <>
          <div className="ranking-table-wrap">
            <table className="ranking-table quality-table">
              <thead><tr><th>排名</th><th>视频素材</th><th>点击率变化</th><th>看完比例变化</th><th>当前点击率</th><th>当前看完比例</th><th>看到 3 秒</th><th>数据可信度</th><th>操作</th></tr></thead>
              <tbody>{filtered.slice(0, visible).map((video, index) => (
                <tr key={video.uri}>
                  <td><span className={`rank-number ${index < 3 ? 'top' : ''}`}>{String(index + 1).padStart(2, '0')}</span></td>
                  <td><button className="video-title-button" onClick={() => setSelected(video)} title={video.title}>{shortTitle(video.title, 34)}</button><span className="video-uri">{video.category} · {shortTitle(video.plainSummary, 32)}</span></td>
                  <td className={video.ctrChange !== null && video.ctrChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.ctrChange)}</td>
                  <td className={video.playOverChange !== null && video.playOverChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.playOverChange)}</td>
                  <td><strong className="quality-value">{formatPercent(video.ctr, 2)}</strong></td>
                  <td><strong>{formatPercent(video.playOver, 2)}</strong></td>
                  <td>{formatPercent(video.play3s, 1)}</td>
                  <td><span className={video.qualityCoverage !== null && video.qualityCoverage < .5 ? 'coverage-low' : 'coverage-good'}>{formatPercent(video.qualityCoverage, 0)}</span></td>
                  <td><button className="detail-button" onClick={() => setSelected(video)}>详情</button></td>
                </tr>
              ))}</tbody>
            </table>
          </div>
          <div className="video-cards">{filtered.slice(0, visible).map((video, index) => (
            <article className="video-card" key={video.uri}>
              <div className="video-card-top"><span className={`rank-number ${index < 3 ? 'top' : ''}`}>{String(index + 1).padStart(2, '0')}</span><span className="table-category">{video.category}</span><strong className={video.qualityTrend !== null && video.qualityTrend < 0 ? 'negative-text' : 'positive-text'}>{trend(video.qualityTrend)}</strong></div>
              <button className="video-title-button" onClick={() => setSelected(video)}>{video.title}</button>
              <p className="card-plain-summary">{video.plainSummary}</p>
              <div className="priority-metrics"><div><span>点击率变化</span><strong className={video.ctrChange !== null && video.ctrChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.ctrChange)}</strong></div><div><span>看完比例变化</span><strong className={video.playOverChange !== null && video.playOverChange < 0 ? 'negative-text' : 'positive-text'}>{trend(video.playOverChange)}</strong></div></div>
              <div className="secondary-metrics"><span>当前点击率 <strong>{formatPercent(video.ctr, 2)}</strong></span><span>当前看完 <strong>{formatPercent(video.playOver, 2)}</strong></span><span>看到 3 秒 <strong>{formatPercent(video.play3s, 1)}</strong></span><span>数据覆盖 <strong>{formatPercent(video.qualityCoverage, 0)}</strong></span></div>
              <div className="video-card-bottom"><span>只评价内容质量，不代表赚钱</span><button className="detail-button" onClick={() => setSelected(video)}>查看详情</button></div>
            </article>
          ))}</div>
          {visible < filtered.length && <button className="load-more" onClick={() => setVisible(value => value + 20)}>再显示 20 条 <ChevronDown size={17} /></button>}
        </>
      )}
      {selected && <VideoDetailModal video={selected} onClose={closeModal} />}
    </section>
  )
}
