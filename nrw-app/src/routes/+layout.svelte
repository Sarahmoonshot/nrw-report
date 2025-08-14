<script lang="ts">
  import "../app.css"
  import favicon from "$lib/assets/favicon.svg"
  import * as Sidebar from "$lib/components/ui/sidebar/index.js"
  import AppSidebar from "$lib/components/AppSideBar.svelte"
  import AppAvatar from "$lib/components/AppAvatar.svelte"

  let { children } = $props()
</script>

<Sidebar.Provider>
  <link rel="icon" href={favicon} />
  <!-- <AppSidebar /> -->
  <main class="flex overflow-x-hidden">
    <!-- <Sidebar.Trigger class="relative left-1 top-1" /> -->
    <AppAvatar />
    {@render children?.()}
  </main>
</Sidebar.Provider>
