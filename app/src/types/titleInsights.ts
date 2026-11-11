export interface TitleFeature {
  name: string
  robustRate: number
  nonRisingRate: number
  difference: number
}

export interface TitleExample {
  title: string
  category: string
  qualityTrend: number
  ctrChange: number
  playOverChange: number
  ctr: number
  playOver: number
  videoUrl: string
}

export interface TitleFramework {
  title: string
  description: string
}

export interface TitleInsightData {
  summary: {
    rising: number
    robust: number
    rebound: number
    nonRising: number
  }
  features: TitleFeature[]
  examples: TitleExample[]
  frameworks: TitleFramework[]
}
