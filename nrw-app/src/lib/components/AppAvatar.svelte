<script lang="ts">
  import * as Avatar from "$lib/components/ui/avatar/index"
  import UserIcon from "@lucide/svelte/icons/user"
  import Button from "$lib/components/ui/button/button.svelte"
  import {
    DropdownMenu,
    DropdownMenuTrigger,
    DropdownMenuContent,
    DropdownMenuItem,
  } from "$lib/components/ui/dropdown-menu/index"
  import { auth } from "$lib/client"
  import { GoogleAuthProvider, onAuthStateChanged, signInWithPopup, signOut, type User } from "firebase/auth"
  import { onMount } from "svelte"

  let user: User | null = null

  // Restore user from Firebase on page load
  onMount(() => {
    return onAuthStateChanged(auth, (u) => {
      user = u
    })
  })
  const login = async () => {
    try {
      const provider = new GoogleAuthProvider()
      const result = await signInWithPopup(auth, provider)
      user = result.user
    } catch (e) {
      console.log(e)
    }
  }

  async function logout() {
    try {
      await signOut(auth)
    } catch (error) {
      console.error("Sign-out failed:", error)
    }
  }
</script>

<div class="absolute right-5 top-5">
  <DropdownMenu>
    <DropdownMenuTrigger>
      <Button
        variant="ghost"
        class=" hover:cursor-pointer transition-shadow duration-200 ease-in-out rounded-full w-10"
      >
        <Avatar.Root class="w-10 h-10">
          <Avatar.Image src={user?.photoURL} />
          <Avatar.Fallback>
            <UserIcon />
          </Avatar.Fallback>
        </Avatar.Root>
      </Button>
    </DropdownMenuTrigger>
    <DropdownMenuContent align="end" class="w-40">
      {#if user}
        <DropdownMenuItem onclick={logout}>Sign Out</DropdownMenuItem>
      {:else}
        <DropdownMenuItem onclick={login}>Sign In</DropdownMenuItem>
      {/if}
    </DropdownMenuContent>
  </DropdownMenu>
</div>
