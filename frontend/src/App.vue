<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { useAuth } from './composables/useAuth';

const route = useRoute();
const { state, isAuthenticated, logout } = useAuth();

const links = [
  { to: '/', label: 'Produits' },
  { to: '/cart', label: 'Panier' },
  { to: '/orders', label: 'Commandes' },
];
</script>

<template>
  <div class="page">
    <header class="topbar">
      <div class="brand">Bazely Shop</div>
      <nav class="nav">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :class="[{ active: route.path === link.to }, 'nav-link']"
        >
          {{ link.label }}
        </RouterLink>
      </nav>
      <div class="auth">
        <template v-if="isAuthenticated">
          <span class="welcome">Bonjour, {{ state.username }}</span>
          <button class="ghost" type="button" @click="logout">Déconnexion</button>
        </template>
        <template v-else>
          <RouterLink class="ghost" to="/login">Connexion</RouterLink>
          <RouterLink class="primary" to="/register">Créer un compte</RouterLink>
        </template>
      </div>
    </header>
    <main class="main">
      <RouterView />
    </main>
  </div>
</template>
