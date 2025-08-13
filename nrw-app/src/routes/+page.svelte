<script>
  let count = $state(0)

  const increment = () => {
    count++
  }
</script>

<button
  onclick={increment}
  class={"bg-amber-200 p-1 px-3 hover:bg-amber-300 rounded-md"}
>
  {count}
</button>
