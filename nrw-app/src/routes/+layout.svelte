<script lang="ts">
  import "../app.css"
  import favicon from "$lib/assets/favicon.svg"
  import * as Sidebar from "$lib/components/ui/sidebar/index.js"
  import AppSidebar from "$lib/components/AppSideBar.svelte"

  let { children } = $props()
</script>

<Sidebar.Provider>
  <link rel="icon" href={favicon} />
  <AppSidebar />
  <main>
    <Sidebar.Trigger />
    {@render children?.()}
  </main>
</Sidebar.Provider>
