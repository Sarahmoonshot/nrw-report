<script lang="ts">
  import DataChart from "$lib/components/DataChart.svelte"
  import { useSidebar } from "$lib/components/ui/sidebar/index"
  import { derived, toStore } from "svelte/store"
  import { PUBLIC_SERVER_ADDRESS } from "$env/static/public"
  import { onMount } from "svelte"
  // const sidebar = useSidebar()

  // const contentWidth = derived(
  //   toStore(() => sidebar.open),
  //   ($open) => ($open ? "w-screen" : "w-screen")
  // )

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

  let chartData: data[] = $state([])
  const getNRWData = async () => {
    try {
      const response = await fetch(
        `${PUBLIC_SERVER_ADDRESS}/api/daily-flow?month=2025-07`
      )

      if (!response.ok) {
        console.log("ERR status code: ", response.status)
        return
      }

      const data = await response.json()
      chartData = data
      console.log({ data })
    } catch (e) {
      console.log(e)
    }
  }

  onMount(() => {
    getNRWData()
  })
</script>

<div class={`flex flex-col items-center p-8 transition-all w-screen`}>
  <h1 class="flex mx-auto w-fit text-3xl select-none font-semibold">
    <!-- why -->
    {"Non-Revenue Water".toUpperCase()}
  </h1>
  <DataChart data={chartData} />
</div>
