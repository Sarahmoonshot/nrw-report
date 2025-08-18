<script lang="ts">
  import { BarChart } from "layerchart"

  const { data }: { data: YearlyNRWData | null } = $props()

  // Convert Record -> Array
  const chartData = data
    ? Object.entries(data).map(([month, values]) => ({
        month,
        nrwPercent: values.nrw_percent / 100,
      }))
    : []
</script>

<div class="flex flex-col w-full h-[30rem] border rounded-sm p-4">
  <p class="flex mx-auto">Monthly NRW %</p>

  <BarChart
    data={chartData}
    x="month"
    series={[
      { key: "nrwPercent", label: "NRW Percent", color: "var(--chart-2)" },
    ]}
    renderContext="svg"
    legend
    props={{
      legend: { placement: "bottom" },
      highlight: {
        area: {class: "fill-black opacity-10" },
      },
      bars: { class: "fill-teal-600 stroke-none" },
      tooltip: {
        root: { class: "bg-zinc-100" },
        header: { class: "text-teal-600" },
        item: { format: "percentRound" },
      },
    }}
  />
</div>
