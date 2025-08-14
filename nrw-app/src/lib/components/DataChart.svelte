<script lang="ts">
  import { BarChart } from "layerchart"

  type DataPoint = {
    value: number
    date: Date
  }

  const { data }: { data: DataPoint[] } = $props()

  const scaledData = data.map((d) => ({
    ...d,
    value: d.value / 100,
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
