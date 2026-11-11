export interface DashboardMeta {
  title: string
  window: string
  rawRows: number
  dailyRows: number
  materials: number
  priorityCount: number
  testCount: number
  declineCount: number
  excludedFunnelRows: number
  invalidAttentionRows: number
  globalIpm: number
  rho: number
  priorOverlap5k: number
  priorOverlap20k: number
  impressions: number
  clicks: number
  conversions: number
  growthComparableCount: number
  qualityRisingCount: number
  dilutionRiskCount: number
}

export interface PeriodMetric {
  period: string
  ipm: number | null
  ctr: number | null
  play3s: number | null
  play5s: number | null
  playOver: number | null
  qualityCoverage: number | null
  impressions: number
  conversions: number
}

export interface VideoMetric {
  uri: string
  title: string
  category: string
  duration: number | null
  impressions: number
  clicks: number
  conversions: number
  ctr: number | null
  cvr: number | null
  ipm: number | null
  baselineIpm: number | null
  ebIndex: number | null
  conservativeIndex: number | null
  p2Impressions: number
  p3Impressions: number
  p2Clicks: number
  p3Clicks: number
  p2Conversions: number
  p3Conversions: number
  p2Days: number
  p3Days: number
  p2Ctr: number | null
  p3Ctr: number | null
  p2Ipm: number | null
  p3Ipm: number | null
  recentChange: number | null
  impressionsGrowth: number | null
  clicksGrowth: number | null
  conversionsGrowth: number | null
  ctrChange: number | null
  ipmChange: number | null
  play3sChange: number | null
  playOverChange: number | null
  exposureMomentum: number | null
  qualityTrend: number | null
  p2QualityCoverage: number | null
  p3QualityCoverage: number | null
  growthComparable: boolean
  dilutionRisk: boolean
  trafficSignal: string
  conversionDayRate: number | null
  play3s: number | null
  play5s: number | null
  playOver: number | null
  avgWatch: number | null
  retention: number | null
  qualityCoverage: number | null
  plainSummary: string
  diagnosis: string
  videoUrl: string
  peopleTags: string[]
  materialTags: string[]
  productCate: string
}

export interface DashboardData {
  meta: DashboardMeta
  periods: PeriodMetric[]
  videos: VideoMetric[]
}
