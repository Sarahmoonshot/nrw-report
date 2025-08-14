<script lang="ts">
  import { BarChart } from "layerchart"

  type data = {
    average_daily_flow: number
    billed_month: string
    billed_qty: number
    daily_nrws: {
      date: String
      est_billed: number
      est_nrw: number
      flowacc: number
      nrw_percent: number
    }
    is_estimate: boolean
    month: string
    nrw_percent: number
    nrw_volume: number
    total_flow: number
  }

  const { data }: { data: data[] } = $props()

  const scaledData = data.map((d) => ({
    ...d,
    value: d.nrw_percent / 100,
  }))
</script>

<div class=" m-8 mt-[10rem] w-full h-[30rem] border rounded-sm p-2">
  <BarChart
    data={scaledData}
    x="date"
    y="value"
    renderContext="svg"
    props={{
      highlight: {
        // THIS PIECE OF $#!T TOOK 2 HOURS
        area: {
          class: "fill-black opacity-10",
        },
      },
      bars: {
        class: "fill-teal-600 stroke-none",
      },
      tooltip: {
        root: { class: "bg-zinc-100" },
        header: { class: "text-teal-600" },
        item: { format: "percentRound" },
      },
    }}
  />
</div>
