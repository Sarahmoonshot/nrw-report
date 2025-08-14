<script>
  import Button from "$lib/components/ui/button/button.svelte"

  let count = $state(0)

  const increment = () => {
    count++
  }
</script>

<Button
  onclick={increment} variant="secondary"
>
  {count}
</Button>
