<script lang="ts">
  import {
    Chart,
    Layer,
    Axis,
    Bars,
    BarChart,
    Tooltip,
    LineChart,
  } from "layerchart"
  import { bin } from "d3-array"
  import { curveCatmullRom } from "d3-shape"

  type DataPoint = {
    value: number
    date: Date
  }

  // Now $props() knows the type automatically
  const { data }: { data: DataPoint[] } = $props()

  const scaledData = data.map((d) => ({
    ...d,
    value: d.value / 100,
  }))
</script>

<div class="h-[300px] m-8 w-full border rounded-sm p-2">
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
