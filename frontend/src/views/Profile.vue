<!--
  Profile — account card: name/email/join-date from the auth store
  plus a shortcut to History. Guests see a login prompt instead.
-->
<template>
  <div class="max-w-md mx-auto px-4 py-14">
    <p class="eyebrow mb-2"><i class="fa-solid fa-user me-2"></i>{{ $t('nav.profile') }}</p>
    <h1 class="font-display text-3xl font-bold mb-8">{{ $t('nav.profile') }}</h1>
    <div v-if="auth.user" class="panel p-6">
      <div class="flex items-center gap-4 mb-5">
        <span class="w-14 h-14 rounded-full bg-cipher/10 border border-cipher/30 flex items-center justify-center">
          <i class="fa-solid fa-user text-cipher text-xl"></i>
        </span>
        <div>
          <p class="font-semibold">{{ auth.user.name || auth.user.email }}</p>
          <p class="font-mono text-xs text-muted" dir="ltr">{{ auth.user.email }}</p>
        </div>
      </div>
      <div class="hairline-t pt-4 flex items-center justify-between text-sm">
        <span class="text-muted"><i class="fa-solid fa-calendar-days me-2"></i>{{ $t('profile.joined') }}</span>
        <span class="font-mono text-xs" dir="ltr">{{ (auth.user.created_at || '').slice(0, 10) }}</span>
      </div>
      <router-link to="/history" class="btn-ghost w-full py-2.5 text-sm mt-5 flex items-center justify-center gap-2">
        <i class="fa-solid fa-clock-rotate-left"></i>{{ $t('profile.view_history') }}
      </router-link>
    </div>
    <div v-else class="panel p-8 text-center">
      <i class="fa-solid fa-user-slash text-3xl text-muted mb-3"></i>
      <p class="text-sm text-muted mb-4">{{ $t('history.login_required') }}</p>
      <router-link to="/login" class="btn-cipher px-5 py-2.5 text-sm inline-block">{{ $t('nav.login') }}</router-link>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/authStore'
const auth = useAuthStore()
</script>
