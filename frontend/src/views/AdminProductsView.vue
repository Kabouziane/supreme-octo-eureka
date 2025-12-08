<script setup>
import { ref } from 'vue';
import { request } from '../api';
import { useAuth } from '../composables/useAuth';

const { isAuthenticated, isStaff } = useAuth();
const name = ref('');
const description = ref('');
const price = ref(0);
const stock = ref(0);
const imageUrl = ref('');
const error = ref('');
const success = ref('');
const loading = ref(false);

const submit = async () => {
  error.value = '';
  success.value = '';
  loading.value = true;
  try {
    await request('/products/', {
      method: 'POST',
      body: {
        name: name.value,
        description: description.value,
        price: Number(price.value),
        stock: Number(stock.value),
        image_url: imageUrl.value,
        is_active: true,
      },
    });
    success.value = 'Produit créé.';
    name.value = '';
    description.value = '';
    price.value = 0;
    stock.value = 0;
    imageUrl.value = '';
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Espace admin</h1>
      <span class="badge">Ajout produit</span>
    </div>
    <div v-if="!isAuthenticated" class="error">Connectez-vous.</div>
    <div v-else-if="!isStaff" class="error">Réservé aux admins.</div>
    <form v-else class="form" @submit.prevent="submit">
      <input class="input" placeholder="Nom" v-model="name" required />
      <textarea
        class="input"
        style="min-height: 80px"
        placeholder="Description"
        v-model="description"
      ></textarea>
      <div class="form-row">
        <input
          class="input"
          type="number"
          min="0"
          step="0.01"
          placeholder="Prix"
          v-model="price"
          required
        />
        <input
          class="input"
          type="number"
          min="0"
          step="1"
          placeholder="Stock"
          v-model="stock"
          required
        />
      </div>
      <input class="input" type="url" placeholder="URL de l'image" v-model="imageUrl" />
      <button class="primary" type="submit" :disabled="loading">Créer</button>
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">{{ success }}</div>
    </form>
  </section>
</template>
