<script lang="ts">
  import { page } from "$app/state"
  import DataChart from "$lib/components/ComparisonChart.svelte"

  const code = $derived(page.params.code)
</script>

<div class="flex w-full justify-center">
  <DataChart {code} />
</div>
