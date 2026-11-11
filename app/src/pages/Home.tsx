import type { ReactNode } from 'react'
import {
  ArrowDown, ArrowRight, BarChart3, BookOpen, Clapperboard, Download, Eye, FileText,
  Gauge, Layers3, ScanLine, ShieldAlert, TimerReset, TrendingUp,
} from 'lucide-react'
import { Link } from 'react-router'
import { dashboard } from '@/data/dashboard'
import { formatInt, formatPercent } from '@/utils/format'
import { PeriodPanel } from '@/components/OverviewCharts'
import { RankingTable } from '@/components/RankingTable'
import { TitleInsights } from '@/components/TitleInsights'

function Metric({ icon, label, value, note, accent = false }: { icon: ReactNode; label: string; value: string; note: string; accent?: boolean }) {
  return <article className={`metric-card ${accent ? 'accent' : ''}`}><div className="metric-icon">{icon}</div><div><span>{label}</span><strong>{value}</strong><p>{note}</p></div></article>
}

function PlainGuide() {
  return (
    <details className="plain-guide" open>
      <summary><span><BookOpen size={19} />信息很多，先按这个顺序看</span><ChevronIcon /></summary>
      <div className="guide-content">
        <div className="guide-definitions">
          <p><strong>第一：质量有没有变好</strong>点击率从 2% 升到 3% 是上升 50%；看完比例从 4% 升到 5% 是上升 25%。两项都上升，才进入优先清单。</p>
          <p><strong>第二：现在表现好不好</strong>趋势变好但当前数值仍低，也不能直接称为优质。还要看当前点击率和看完比例。</p>
          <p><strong>第三：问题出在开头还是正文</strong>看到 3 秒比例偏低先改开头；看到 5 秒或看完比例偏低，再检查正文承接。</p>
          <p><strong>第四：结论有多可靠</strong>两期观看数据覆盖率都达到一半，才进入质量趋势排名。</p>
        </div>
        <p className="guide-note">规模、投放量和目标行为已移到辅助信息，不影响主榜顺序。</p>
      </div>
    </details>
  )
}

export default function Home() {
  const { meta, periods, videos } = dashboard
  const qualityComparableCount = videos.filter(video => video.growthComparable && video.qualityTrend !== null).length
  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#overview" aria-label="素材罗盘返回总览"><span className="brand-mark"><BarChart3 size={20} /></span><span>素材罗盘</span></a>
        <nav aria-label="页面导航"><a href="#overview">总览</a><a href="#ranking">优先素材</a><a href="#title-insights">标题学习</a><a href="#method">指标重要度</a></nav>
        <a className="top-download" href="./downloads/h5_candidates_enriched.csv" download><Download size={16} /><span>下载素材数据</span></a>
      </header>

      <main>
        <section className="hero" id="overview">
          <div className="hero-copy">
            <div className="hero-status"><ScanLine size={16} /><span>3C 数码外设 · 84 天广告素材扫描</span></div>
            <h1>先看有没有变好，<br /><em>再谈素材好坏。</em></h1>
            <p>只用质量趋势、当前观看表现和数据可信度，找出真正值得小预算复测的视频。</p>
            <div className="hero-actions"><a className="primary-button" href="#ranking">直接看优先素材 <ArrowDown size={17} /></a><a className="text-link" href="#method">先看指标顺序 <ArrowRight size={16} /></a></div>
          </div>
          <aside className="evidence-card" aria-label="当前评价范围">
            <div className="evidence-top"><span>当前评价范围</span><span className="live-dot">只看内容质量</span></div>
            <div className="evidence-main"><span>重要度排序</span><strong>趋势 ＞ 当前 ＞ 留存 ＞ 可信度</strong><p>先看点击率和看完比例有没有一起变好，再看当前表现和数据是否可靠。</p></div>
            <div className="evidence-steps"><span className="active">质量趋势</span><span>当前表现</span><span>开头留存</span><span>数据可信</span></div>
            <div className="evidence-window"><TimerReset size={16} /><span>{meta.window}</span></div>
          </aside>
        </section>

        <section className="truth-banner" aria-label="评价边界提醒"><ShieldAlert size={22} /><div><strong>页面只做一件事：筛选视频质量</strong><p>投放量、目标行为和规模信息不再占据主榜；是否赚钱仍需真实订单、花费和每单利润。</p></div><a href="#ranking">直接看双升素材</a></section>

        <Link className="playbook-bridge" to="/brand-playbook" aria-label="打开品牌向视频生产方法手册">
          <span className="bridge-icon"><Clapperboard size={21} /></span>
          <div className="bridge-copy"><span>另一个维度 · 品牌向视频生产 Know-how</span><h2>不判断素材好坏，专讲品牌片怎么做出来</h2><p>片型选择、Seedance 与 Remotion 分工、六轮小样流程，以及实景 UI 合成。</p></div>
          <span className="bridge-link">打开独立方法手册 <ArrowRight size={16} /></span>
        </Link>

        <PlainGuide />

        <section className="metrics-grid" aria-label="质量指标摘要">
          <Metric icon={<TrendingUp size={20} />} label="质量双升素材" value={formatInt(meta.qualityRisingCount)} note="点击率和看完比例同时上升" accent />
          <Metric icon={<Layers3 size={20} />} label="质量趋势可比" value={formatInt(qualityComparableCount)} note="两期数据完整且覆盖率达到要求" />
          <Metric icon={<Gauge size={20} />} label="当前行业点击率" value={formatPercent(periods[2].ctr, 2)} note="第 9–12 周整体水平" />
          <Metric icon={<Eye size={20} />} label="当前行业看完比例" value={formatPercent(periods[2].playOver, 2)} note="第 9–12 周整体水平" />
        </section>

        <PeriodPanel periods={periods} />

        <RankingTable videos={videos} />

        <TitleInsights />

        <section className="method-section" id="method" aria-labelledby="method-title">
          <div className="section-heading"><div><span className="section-label">指标重要度</span><h2 id="method-title">所有信息，按这个顺序使用</h2><p>不是每个数字都值得同等关注。先判断变化，再判断现状，最后检查数据是否可信。</p></div><a className="download-link" href="./downloads/roi_evaluation_report.md" download><FileText size={17} />下载完整分析报告</a></div>
          <div className="method-grid priority-method-grid">
            <article><TrendingUp size={22} /><h3>质量趋势</h3><p>点击率和看完比例是否一起上升，是判断内容是否持续变好的第一证据。</p><span>最重要</span></article>
            <article><Gauge size={22} /><h3>当前表现</h3><p>当前点击率和看完比例用于防止“低基数上升”被误读成绝对优质。</p><span>第二重要</span></article>
            <article><Eye size={22} /><h3>开头与正文</h3><p>看到 3 秒、5 秒和看完比例，用于定位应该改开头、节奏还是正文。</p><span>用于诊断</span></article>
            <article><ShieldAlert size={22} /><h3>数据可信度</h3><p>两期观看数据覆盖都至少达到一半，才让趋势进入主榜。</p><span>决定能不能相信</span></article>
          </div>
          <div className="method-details">
            <details><summary>为什么把质量趋势放在第一位？<ChevronIcon /></summary><p>单看某一天的高点击率或高看完比例，很容易受到短期人群和活动影响。两项指标在前后两个时期同时上升，更能说明素材表现正在改善。</p></details>
            <details><summary>为什么还要看当前点击率和看完比例？<ChevronIcon /></summary><p>从很低水平大幅上升，不等于当前已经优秀。趋势回答“有没有变好”，当前值回答“现在好不好”，两者必须同时看。</p></details>
            <details><summary>为什么投放量不再出现在主榜？<ChevronIcon /></summary><p>本次任务是筛选视频质量，而不是评价预算规模。投放量只在辅助信息中保留，不参与素材排序，也不用于判断内容好坏。</p></details>
            <details><summary>为什么一定要看数据覆盖率？<ChevronIcon /></summary><p>如果只有少量记录有效，即使点击率和看完比例上升，也可能只是数据缺口造成的假象。两期覆盖率都达到 50% 是进入质量趋势榜的最低要求。</p></details>
          </div>
        </section>
      </main>

      <footer><div><strong>素材罗盘</strong><span>只看视频质量，按重要度展示证据</span></div><p>数据计算日 2026.11.10 · 原始数据未修改 · 全部结果可复算</p></footer>
    </div>
  )
}

function ChevronIcon() { return <ArrowDown size={17} aria-hidden="true" /> }
