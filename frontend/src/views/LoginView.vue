<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const username = ref('');
const password = ref('');
const router = useRouter();
const { login, loading, error, isAuthenticated } = useAuth();

const submit = async () => {
  await login(username.value, password.value);
  if (isAuthenticated.value) {
    router.push('/');
  }
};
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Connexion</h1>
    </div>
    <form class="form" @submit.prevent="submit">
      <div class="form-row">
        <input
          class="input"
          placeholder="Nom d'utilisateur"
          autocomplete="username"
          v-model="username"
          required
        />
      </div>
      <div class="form-row">
        <input
          class="input"
          type="password"
          placeholder="Mot de passe"
          autocomplete="current-password"
          v-model="password"
          required
        />
      </div>
      <button class="primary" type="submit" :disabled="loading">Se connecter</button>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </section>
</template>
