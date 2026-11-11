import { lazy, Suspense, useEffect } from 'react'
import { Routes, Route, useLocation } from 'react-router'
import './App.css'
import './BrandPlaybook.css'

const Home = lazy(() => import('./pages/Home'))
const BrandPlaybook = lazy(() => import('./pages/BrandPlaybook'))

function ScrollToTop() {
  const { pathname } = useLocation()
  useEffect(() => {
    window.scrollTo(0, 0)
    document.title = pathname === '/brand-playbook' ? '品牌片场｜品牌向视频生产 Know-how' : '3C 短视频内容证据看板'
  }, [pathname])
  return null
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Suspense fallback={<div className="route-loading" role="status">正在打开页面…</div>}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/brand-playbook" element={<BrandPlaybook />} />
        </Routes>
      </Suspense>
    </>
  )
}
