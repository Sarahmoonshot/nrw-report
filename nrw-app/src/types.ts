type data = {
  average_daily_flow: number
  billed_month: string
  billed_qty: number
  daily_nrws: {
    date: string
    est_billed: number
    est_nrw: number
    flowacc: number
    nrw_percent: number
  }[]
  is_estimate: boolean
  month: string
  nrw_percent: number
  nrw_volume: number
  total_flow: number
}

type monthlyData = {
  billed_qty: number
  nrw_percent: number
  nrw_volume: number
  total_flows: number
}

type YearlyNRWData = Record<string, monthlyData>
