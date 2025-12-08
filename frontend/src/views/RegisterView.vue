<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '../composables/useAuth';

const username = ref('');
const email = ref('');
const password = ref('');
const router = useRouter();
const { register, loading, error, isAuthenticated } = useAuth();

const submit = async () => {
  await register({ username: username.value, email: email.value, password: password.value });
  if (isAuthenticated.value) {
    router.push('/');
  }
};
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Créer un compte</h1>
    </div>
    <form class="form" @submit.prevent="submit">
      <div class="form-row">
        <input class="input" placeholder="Nom d'utilisateur" v-model="username" required />
      </div>
      <div class="form-row">
        <input class="input" type="email" placeholder="Email" v-model="email" required />
      </div>
      <div class="form-row">
        <input
          class="input"
          type="password"
          placeholder="Mot de passe (8+ caractères)"
          minlength="8"
          v-model="password"
          required
        />
      </div>
      <button class="primary" type="submit" :disabled="loading">S'inscrire</button>
      <div v-if="error" class="error">{{ error }}</div>
    </form>
  </section>
</template>
