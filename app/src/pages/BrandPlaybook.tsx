import {
  ArrowDown, ArrowLeft, ArrowRight, ArrowUpRight, AudioLines, Check,
  Clapperboard, Code2, Film, Frame, Layers3, MousePointer2, Quote,
  ScanLine, Shapes, Smartphone, Sparkles, Video, WandSparkles,
} from 'lucide-react'
import { Link } from 'react-router'

const formats = [
  {
    icon: <Video size={22} />,
    title: '正式首发片',
    goal: '建立理解与信任',
    description: '从具体痛点开场，立刻亮出产品并完成一次真实操作。用一个案例串起功能，保留从原始记录到引用证据的信任链。',
    tag: '官网首屏／产品首发',
  },
  {
    icon: <MousePointer2 size={22} />,
    title: '功能介绍片',
    goal: '像朋友一样教会用户',
    description: '第一秒让产品出场，删掉寒暄和目录。旁白讲语境，短字抓重点，真实界面负责演示操作。',
    tag: '版本更新／社媒教程',
  },
  {
    icon: <Shapes size={22} />,
    title: '品牌符号片',
    goal: '留下视觉记忆',
    description: '提炼 Logo 的几何轮廓，寻找天然相似的生活物件。对齐视觉中心，用静帧和音乐鼓点快切。',
    tag: '品牌记忆／社交传播',
  },
  {
    icon: <Sparkles size={22} />,
    title: '生活形象片',
    goal: '传递一种品牌情绪',
    description: '先用单场景验证视觉语言，再扩展全片。通过同源同帧的前景与窗口遮罩，让空间自然展开。',
    tag: '品牌态度／生活方式',
  },
]

const rounds = [
  { title: '准备真实素材', action: '运行产品，放入干净的公开演示数据，截取真实 UI 和需要的原生组件。', gate: '确认截图真实、字体干净、无私人信息。' },
  { title: '排静态脚本', action: '写“旁白＋屏幕短字＋画面操作”三栏脚本，先排三张静态关键帧。', gate: '确认色调统一，同一设备连续操作。' },
  { title: '生成真实配音', action: '用真实台词试听两种声线，锁定参数，标出点击与切页的词级时间戳。', gate: '手机外放盲听，选择最像朋友聊天的一条。' },
  { title: '导出有声小样', action: '用 Remotion 合成 15–20 秒 MP4，按真实音长安排镜头，不先塞背景音乐。', gate: '静音看镜头、开声看卡点、小屏看阅读。' },
  { title: '每轮只改一处', action: '锁死满意部分，把反馈具体到秒数和问题，另存版本做新旧对比。', gate: '不做全盘重做，不说笼统的“再优化”。' },
  { title: '沿样板扩成成片', action: '保持既定底色、字体、声线和镜头规则，补充其余场景与片尾下载页。', gate: '归档成片、工程、素材和三条独立音轨。' },
]

const compositeSteps = [
  ['四角定位', '只框屏幕内侧发光区，避开金属边框。'],
  ['透视跟踪', '逐帧透视变换，并对角点轨迹做平滑。'],
  ['前景遮罩', '把经过屏幕的手指抠出，挡住下方 UI。'],
  ['混合反光', '使用 screen 等混合方式，保留玻璃环境光。'],
  ['质感匹配', '匹配原片的景深柔化、边缘与颗粒感。'],
]

export default function BrandPlaybook() {
  return (
    <div className="app-shell playbook-shell">
      <header className="topbar playbook-topbar">
        <Link className="brand" to="/brand-playbook" aria-label="品牌片场返回页首">
          <span className="brand-mark"><Clapperboard size={20} /></span>
          <span>品牌片场</span>
        </Link>
        <nav aria-label="方法手册导航">
          <a href="#formats">片型选择</a>
          <a href="#division">工具分工</a>
          <a href="#six-rounds">六轮流程</a>
          <a href="#compositing">UI 合成</a>
        </nav>
        <Link className="top-download" to="/" aria-label="返回素材罗盘"><ArrowLeft size={16} /><span>返回素材罗盘</span></Link>
      </header>

      <main>
        <section className="playbook-hero" aria-labelledby="playbook-title">
          <div className="playbook-hero-copy">
            <div className="hero-status"><ScanLine size={16} /><span>品牌向视频生产 Know-how · 独立方法手册</span></div>
            <h1 id="playbook-title">品牌视频，<br /><em>不是一键生成。</em></h1>
            <p>AI 负责扩展素材与执行效率，人负责叙事、判断和反馈。用真实 UI、可控代码与真实配音，先把 15 秒小样做对，再扩成完整成片。</p>
            <div className="hero-actions">
              <a className="playbook-primary" href="#six-rounds">从 15 秒小样开始 <ArrowDown size={17} /></a>
              <Link className="text-link" to="/">回到大数据看板 <ArrowUpRight size={16} /></Link>
            </div>
            <ul className="hero-principles" aria-label="核心原则">
              <li><Check size={15} />真实素材打底</li>
              <li><Check size={15} />声音决定节奏</li>
              <li><Check size={15} />每轮单点迭代</li>
            </ul>
          </div>

          <aside className="production-console" aria-label="品牌视频生产栈">
            <div className="console-heading"><span>一条品牌片的生产栈</span><span className="console-role">人做导演</span></div>
            <div className="stack-row"><span className="stack-icon"><Film size={20} /></span><div><strong>Seedance</strong><p>生成稳定、纯黑屏的实景底片</p></div><span>生活场景</span></div>
            <div className="stack-connector" aria-hidden="true" />
            <div className="stack-row featured"><span className="stack-icon"><Code2 size={20} /></span><div><strong>Remotion</strong><p>转场、跟踪、遮罩与时间线</p></div><span>精确控制</span></div>
            <div className="stack-connector" aria-hidden="true" />
            <div className="stack-row"><span className="stack-icon"><AudioLines size={20} /></span><div><strong>MiniMax</strong><p>真实配音与动作时间戳</p></div><span>声音节奏</span></div>
            <div className="console-output"><span>最终输出</span><strong>可播放、可修改、可复用的 MP4 工程</strong></div>
          </aside>
        </section>

        <section className="dimension-split" aria-label="两个内容维度">
          <article>
            <span>现有 H5 · 投放数据维度</span>
            <h2>哪条素材正在变好？</h2>
            <p>用趋势、当前表现、留存和可信度，筛选值得复测的视频。</p>
            <Link to="/">打开素材罗盘 <ArrowUpRight size={15} /></Link>
          </article>
          <article className="current">
            <span>本页 · 品牌生产维度</span>
            <h2>怎样做出可信、耐看的品牌片？</h2>
            <p>讲生产决策与执行方法，不参与投放效果判断。</p>
            <strong><Frame size={15} />当前方法手册</strong>
          </article>
        </section>

        <section className="playbook-section" id="formats" aria-labelledby="formats-title">
          <div className="playbook-section-heading">
            <span className="section-label">先定传播任务</span>
            <h2 id="formats-title">先选片型，再决定技术</h2>
            <p>不要用同一套“功能介绍”思路做所有视频。首发片解决信任，功能片解决理解，品牌片解决记忆与情绪。</p>
          </div>
          <div className="format-grid">
            {formats.map(item => (
              <article key={item.title}>
                <div className="format-icon">{item.icon}</div>
                <span>{item.goal}</span>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
                <small>{item.tag}</small>
              </article>
            ))}
          </div>
        </section>

        <section className="playbook-section" id="division" aria-labelledby="division-title">
          <div className="playbook-section-heading">
            <span className="section-label">最容易混淆的分工</span>
            <h2 id="division-title">转场衔接，到底谁来做？</h2>
            <p>都可能出现，但主力分工明确：Seedance 生成镜头内部的自然世界，Remotion 控制镜头之间和界面之内的精确衔接。</p>
          </div>
          <div className="division-grid">
            <article className="division-card">
              <div className="division-title"><Film size={23} /><div><span>Seedance 负责</span><h3>真实世界自然发生</h3></div></div>
              <ul><li>人物交谈、抬腕、点击等自然动作</li><li>生活场景、环境光影与氛围</li><li>单机位、固定镜头、简单微动作</li></ul>
              <p>不要让模型硬做多机位切换、复杂 UI、文字或 Logo，容易人物复制、脸部变形和界面乱码。</p>
            </article>
            <article className="division-card code">
              <div className="division-title"><Code2 size={23} /><div><span>Remotion 负责</span><h3>镜头与界面精确衔接</h3></div></div>
              <ul><li>完整设备推近、卡片展开与归位</li><li>实景剪切、遮罩展开、音乐卡点</li><li>真实 UI 跟踪合成与词级声画对齐</li></ul>
              <p>凡是需要精确到像素、秒数、品牌形状和真实文字的部分，都交给代码。</p>
            </article>
          </div>
          <div className="production-flow" aria-label="生产顺序">
            <div><Film size={18} /><span>实景底片</span></div><ArrowRight size={17} />
            <div><Layers3 size={18} /><span>代码合成</span></div><ArrowRight size={17} />
            <div><AudioLines size={18} /><span>真实配音</span></div><ArrowRight size={17} />
            <div><Clapperboard size={18} /><span>MP4 成片</span></div>
          </div>
        </section>

        <section className="playbook-section narrative-section" aria-labelledby="narrative-title">
          <div className="playbook-section-heading">
            <span className="section-label">让陌生观众看得懂</span>
            <h2 id="narrative-title">三级镜头接力，不清空画面</h2>
            <p>同一台设备尽量持续留在场上。镜头运动跟随真实操作，关键结果必须停稳，留够阅读时间。</p>
          </div>
          <div className="shot-sequence">
            <article><Smartphone size={25} /><span>先建立空间感</span><h3>完整设备全貌</h3><p>露出完整机身和底部导航，先让人知道当前在哪个页面。</p></article>
            <ArrowRight className="shot-arrow" size={20} aria-hidden="true" />
            <article><MousePointer2 size={25} /><span>再顺着动作推近</span><h3>页面真实点击</h3><p>点击真实按钮后再推镜头，不为了节奏把 UI 裁成碎片。</p></article>
            <ArrowRight className="shot-arrow" size={20} aria-hidden="true" />
            <article><Quote size={25} /><span>最后让人读完</span><h3>核心结果特写</h3><p>结论、数字或原话出现时，稳稳停留，不字刚出来就切走。</p></article>
          </div>
          <div className="evidence-chain"><strong>首发片的信任链不能省：</strong><span>原始记录</span><ArrowRight size={14} /><span>高光整理</span><ArrowRight size={14} /><span>AI 结论</span><ArrowRight size={14} /><span>引用证据</span></div>
        </section>

        <section className="playbook-section rounds-section" id="six-rounds" aria-labelledby="rounds-title">
          <div className="playbook-section-heading">
            <span className="section-label">最小可行制作流程</span>
            <h2 id="rounds-title">六轮做出 15 秒，再扩成完整片</h2>
            <p>每轮都有可检查的交付物。先确认再进入下一轮，避免动画、配音和实景全部铺开后返工。</p>
          </div>
          <div className="rounds-list">
            {rounds.map((round, index) => (
              <article key={round.title}>
                <span className="round-number">{String(index + 1).padStart(2, '0')}</span>
                <div><h3>{round.title}</h3><p>{round.action}</p></div>
                <div className="round-gate"><Check size={15} /><span>{round.gate}</span></div>
              </article>
            ))}
          </div>
          <div className="audio-rule"><AudioLines size={22} /><div><strong>声音先行，是时间线的硬规则</strong><p>新增或修改旁白后，先生成真实音频、测准秒数，再调整画面。片子过长就删词、局部重录，不要整条倍速。</p></div></div>
        </section>

        <section className="playbook-section" id="compositing" aria-labelledby="compositing-title">
          <div className="playbook-section-heading">
            <span className="section-label">实景与真实 UI 的融合</span>
            <h2 id="compositing-title">黑屏底片＋代码跟踪合成</h2>
            <p>视频模型只生成没有文字和图标的黑屏设备，真实 UI 由后期逐帧贴入，避免乱码，也能保留真实操作。</p>
          </div>
          <div className="composite-layout">
            <div className="screen-demo" aria-hidden="true">
              <div className="demo-device">
                <i className="corner tl" /><i className="corner tr" /><i className="corner bl" /><i className="corner br" />
                <div className="demo-ui"><span /><span /><span /><strong /></div>
                <div className="demo-reflection" />
              </div>
              <div className="demo-caption"><WandSparkles size={16} /><span>透视跟随 · 手指遮挡 · 玻璃反光</span></div>
            </div>
            <div className="composite-steps">
              {compositeSteps.map(([title, description], index) => (
                <article key={title}><span>{String(index + 1).padStart(2, '0')}</span><div><h3>{title}</h3><p>{description}</p></div></article>
              ))}
            </div>
          </div>
          <p className="composite-tip"><strong>生成时更省心的做法：</strong>需要贴 UI 的设备尽量保持稳定，让交谈、夹菜、画图等生活动作发生在屏幕之外。</p>
        </section>

        <section className="playbook-section final-check" aria-labelledby="final-title">
          <div><span className="section-label">导演反馈方式</span><h2 id="final-title">把“感觉不好”改成可执行指令</h2><p>指出具体秒数和具体问题，同时锁死已经确认的部分。每轮只解决最影响观看的那一处。</p></div>
          <blockquote>“第 8 秒结果刚出现就切走了。前面设备出场、色调和配音锁死不动，只给原话特写增加 0.8 秒，并另存版本对比。”</blockquote>
          <Link className="playbook-primary" to="/">返回素材罗盘 <ArrowUpRight size={17} /></Link>
        </section>
      </main>

      <footer className="playbook-footer"><div><strong>品牌片场</strong><span>品牌向视频生产 Know-how</span></div><p>独立方法手册 · 与投放数据分析分维度使用</p></footer>
    </div>
  )
}
