<script lang="ts">
  import { BarChart, Legend } from "layerchart"

  const {
    data,
  }: {
    data: data
  } = $props()
  const month = new Date(data?.month)?.toLocaleDateString("PH", {
    month: "long",
  })

  const breakdownData = data
    ? data.daily_nrws.map((nrw) => ({
        date: nrw.date.split("-")[2],
        billed: nrw.est_billed,
        nrw: nrw.est_nrw,
      }))
    : []
</script>

<div class="flex flex-col w-full h-[30rem] border rounded-sm p-4">
  <p class="flex mx-auto mb-2 font-semibold">
    [{month}] Billed Water vs NRW
  </p>

  <BarChart
    data={breakdownData}
    x="date"
    series={[
      { key: "billed", color: "var(--chart-2)" },
      { key: "nrw", color: "var(--chart-1)" },
    ]}
    seriesLayout="stack"
    renderContext="svg"
    legend
    props={{
      highlight: {
        area: { class: "fill-black opacity-10" },
      },
      bars: {
        class: "stroke-none",
      },
      tooltip: {
        root: { class: "bg-zinc-100" },
        header: {
          class: "text-teal-600",
          format: (d) => `${month} ${d}`,
        },
        item: { format: "metric" },
      },
      xAxis: { format: "none" },
      yAxis: { format: "metric" },
    }}
  />
</div>

<!-- <BarChart
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
  /> -->
