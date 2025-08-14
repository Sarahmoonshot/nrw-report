<script>
  import DataChart from "$lib/components/DataChart.svelte"
  import { useSidebar } from "$lib/components/ui/sidebar/index"
  import { derived, toStore } from "svelte/store"
  const sidebar = useSidebar()

  const contentWidth = derived(
    toStore(() => sidebar.open),
    ($open) => ($open ? "w-[93.1rem]" : "w-screen")
  )

  const chartData = [
    {
      date: new Date("2025-07-14T16:00:00.000Z"),
      value: 72,
    },
    {
      date: new Date("2025-07-15T16:00:00.000Z"),
      value: 96,
    },
    {
      date: new Date("2025-07-16T16:00:00.000Z"),
      value: 61,
    },
    {
      date: new Date("2025-07-17T16:00:00.000Z"),
      value: 59,
    },
    {
      date: new Date("2025-07-18T16:00:00.000Z"),
      value: 89,
    },
    {
      date: new Date("2025-07-19T16:00:00.000Z"),
      value: 64,
    },
    {
      date: new Date("2025-07-20T16:00:00.000Z"),
      value: 99,
    },
    {
      date: new Date("2025-07-21T16:00:00.000Z"),
      value: 70,
    },
    {
      date: new Date("2025-07-22T16:00:00.000Z"),
      value: 69,
    },
    {
      date: new Date("2025-07-23T16:00:00.000Z"),
      value: 95,
    },
    {
      date: new Date("2025-07-24T16:00:00.000Z"),
      value: 50,
    },
    {
      date: new Date("2025-07-25T16:00:00.000Z"),
      value: 79,
    },
    {
      date: new Date("2025-07-26T16:00:00.000Z"),
      value: 68,
    },
    {
      date: new Date("2025-07-27T16:00:00.000Z"),
      value: 94,
    },
    {
      date: new Date("2025-07-28T16:00:00.000Z"),
      value: 76,
    },
    {
      date: new Date("2025-07-29T16:00:00.000Z"),
      value: 57,
    },
    {
      date: new Date("2025-07-30T16:00:00.000Z"),
      value: 89,
    },
    {
      date: new Date("2025-07-31T16:00:00.000Z"),
      value: 69,
    },
    {
      date: new Date("2025-08-01T16:00:00.000Z"),
      value: 75,
    },
    {
      date: new Date("2025-08-02T16:00:00.000Z"),
      value: 90,
    },
    {
      date: new Date("2025-08-03T16:00:00.000Z"),
      value: 88,
    },
    {
      date: new Date("2025-08-04T16:00:00.000Z"),
      value: 95,
    },
    {
      date: new Date("2025-08-05T16:00:00.000Z"),
      value: 83,
    },
    {
      date: new Date("2025-08-06T16:00:00.000Z"),
      value: 58,
    },
    {
      date: new Date("2025-08-07T16:00:00.000Z"),
      value: 74,
    },
    {
      date: new Date("2025-08-08T16:00:00.000Z"),
      value: 61,
    },
    {
      date: new Date("2025-08-09T16:00:00.000Z"),
      value: 62,
    },
    {
      date: new Date("2025-08-10T16:00:00.000Z"),
      value: 82,
    },
    {
      date: new Date("2025-08-11T16:00:00.000Z"),
      value: 99,
    },
    {
      date: new Date("2025-08-12T16:00:00.000Z"),
      value: 80,
    },
  ]
</script>

<div
  class={`flex flex-col items-center p-8 transition-all ${$contentWidth} w-screen duration-200 ease-in-out`}
>
  <h1 class="flex mx-auto w-fit text-3xl select-none font-semibold">
    <!-- why -->
    {"Non-Revenue Water".toUpperCase()}
  </h1>
  <DataChart data={chartData} />
</div>
