<script lang="ts">
  import { PUBLIC_SERVER_ADDRESS } from "$env/static/public"
  import { getCache, setCache } from "$lib/cache"
  import ComparisonChart from "$lib/components/ComparisonChart.svelte"
  import MonthlyChart from "$lib/components/MonthlyChart.svelte"
  import { onMount } from "svelte"

  let chartData: data | null = $state(null)
  let monthlyData: YearlyNRWData | null = $state(null)
  let loading = $state(false)
  let error: string | null = $state(null)

  async function getNRWData() {
    loading = true
    error = null
    chartData = null

    const cached = getCache<data>("nrwData")
    if (cached) {
      console.log("getting from cache..")
      chartData = cached
      loading = false
      return
    }
    try {
      const response = await fetch(
        `${PUBLIC_SERVER_ADDRESS}/api/daily-flow?month=2025-07`
      )

      if (!response.ok) {
        error = `Request failed with status ${response.status}`
        return
      }

      const json = await response.json()
      setCache("nrwData", json, 1000 * 60 * 60)
      chartData = json
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error"
    } finally {
      loading = false
    }
  }

  async function getMonthlyData() {
    loading = true
    error = null

    const cached = getCache<YearlyNRWData>("monthlyData")
    if (cached) {
      console.log("getting from cache..")
      monthlyData = cached
      loading = false

      return
    }
    try {
      const response = await fetch(`${PUBLIC_SERVER_ADDRESS}/nrw/volume-data`)

      if (!response.ok) {
        error = `Request failed with status ${response.status}`
        return
      }

      const json = await response.json()
      setCache("monthlyData", json, 1000 * 60 * 60)
      monthlyData = json
    } catch (e) {
      error = e instanceof Error ? e.message : "Unknown error"
    } finally {
      loading = false
    }
  }
  function retry() {
    getNRWData()
    getMonthlyData()
  }

  $inspect(chartData)
  $inspect(monthlyData)
  onMount(() => {
    getNRWData()
    getMonthlyData()
  })
</script>

<div class="flex flex-col items-center p-8 transition-all w-screen">
  <h1 class="flex mx-auto w-fit text-3xl select-none font-semibold">
    {"Non-Revenue Water".toUpperCase()}
  </h1>

  {#if loading}
    <div
      class="w-[80rem] h-[40rem] bg-zinc-200 rounded-md mt-10 flex animate-pulse justify-center items-center"
    >
      Loading NRW data...
    </div>
  {:else if error}
    <div
      class="w-[80rem] h-[40rem] bg-red-100 border border-red-400 rounded-md mt-10 flex flex-col justify-center items-center gap-4"
    >
      <p class="text-red-600 font-semibold">Error: {error}</p>
      <button
        class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-md"
        onclick={retry}
      >
        Retry
      </button>
    </div>
  {:else}
    <div class="flex gap-2 p-4 flex-col w-[80rem]">
      {#if chartData}
        <ComparisonChart data={chartData} />
      {/if}
      {#if monthlyData}
        <MonthlyChart data={monthlyData} />
      {/if}
    </div>
  {/if}
</div>
