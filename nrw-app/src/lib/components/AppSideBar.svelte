<script lang="ts">
  import * as Sidebar from "$lib/components/ui/sidebar/index.js"
  import { collection, onSnapshot, query, where } from "firebase/firestore"
  import { db, auth } from "$lib/client"
  import { onMount } from "svelte"
  import { onAuthStateChanged, type User } from "firebase/auth"

  let items = $state<any[]>([])
  let user = $state<User | null>(null)

  let unsubscribeDocs: (() => void) | null = null

  function listenToDocs() {
    if (unsubscribeDocs) unsubscribeDocs()

    const q = query(
      collection(db, "stations"),
      where("monitors", "array-contains", "flow_rate")
    )
    unsubscribeDocs = onSnapshot(q, (snapshot) => {
      items = snapshot.docs.map((doc) => ({
        id: doc.id,
        ...doc.data(),
      }))
    })
  }
  $inspect(items)
  // Listen to auth changes
  onMount(() => {
    const unsubscribeAuth = onAuthStateChanged(auth, (u) => {
      user = u
    })

    return () => {
      unsubscribeAuth()
      if (unsubscribeDocs) unsubscribeDocs()
    }
  })

  // Automatically rerun Firestore subscription when user changes
  $effect(() => {
    if (user) {
      listenToDocs()
    } else {
      items = []
      if (unsubscribeDocs) {
        unsubscribeDocs()
        unsubscribeDocs = null
      }
    }
  })
</script>

<Sidebar.Root class="duration-200 transition-all ease-in-out">
  <Sidebar.Content>
    <Sidebar.Group>
      <Sidebar.GroupLabel>Stations</Sidebar.GroupLabel>
      <Sidebar.GroupContent>
        <Sidebar.Menu>
          {#each items as item (item.id)}
            <Sidebar.MenuItem>
              <Sidebar.MenuButton class={"py-5"}>
                {#snippet child({ props })}
                  <a href={item.code} {...props}>
                    <div class="flex gap-1">
                      <span
                        class="flex text-muted-foreground items-center shrink-0 text-[10px] w-fit"
                      >
                        [{item.code}]
                      </span>
                      <span class="">{item.name}</span>
                    </div>
                  </a>
                {/snippet}
              </Sidebar.MenuButton>
            </Sidebar.MenuItem>
          {/each}
        </Sidebar.Menu>
      </Sidebar.GroupContent>
    </Sidebar.Group>
  </Sidebar.Content>
</Sidebar.Root>
