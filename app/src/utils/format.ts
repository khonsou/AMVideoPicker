export const formatInt = (value: number) => new Intl.NumberFormat('zh-CN').format(value)

export const formatCompact = (value: number) => {
  if (value >= 100_000_000) return `${(value / 100_000_000).toFixed(2)} 亿`
  if (value >= 10_000) return `${(value / 10_000).toFixed(value >= 1_000_000 ? 0 : 1)} 万`
  return formatInt(value)
}

export const formatPercent = (value: number | null, digits = 1) =>
  value === null ? '—' : `${(value * 100).toFixed(digits)}%`

export const formatIndex = (value: number | null) =>
  value === null ? '—' : `${(value / 100).toFixed(1)}×`

export const formatChange = (value: number | null) =>
  value === null ? '新进场' : `${value >= 0 ? '+' : ''}${(value * 100).toFixed(1)}%`

export const shortTitle = (title: string, length = 24) =>
  title.length > length ? `${title.slice(0, length)}…` : title
