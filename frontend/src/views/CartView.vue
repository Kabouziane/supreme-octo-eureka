<script setup>
import { computed, onMounted, ref } from 'vue';
import { request } from '../api';
import { useAuth } from '../composables/useAuth';

const items = ref([]);
const loading = ref(false);
const error = ref('');
const success = ref('');
const { isAuthenticated } = useAuth();

const total = computed(() =>
  items.value.reduce((acc, item) => acc + Number(item.subtotal || 0), 0).toFixed(2)
);

const loadCart = async () => {
  if (!isAuthenticated.value) return;
  loading.value = true;
  error.value = '';
  try {
    const data = await request('/cart/');
    items.value = data.items || [];
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const updateQuantity = async (itemId, quantity) => {
  error.value = '';
  success.value = '';
  try {
    await request(`/cart/items/${itemId}/`, {
      method: 'PATCH',
      body: { quantity },
    });
    await loadCart();
    success.value = 'Quantité mise à jour.';
  } catch (err) {
    error.value = err.message;
  }
};

const removeItem = async (itemId) => {
  error.value = '';
  success.value = '';
  try {
    await request(`/cart/items/${itemId}/`, { method: 'DELETE' });
    items.value = items.value.filter((item) => item.id !== itemId);
  } catch (err) {
    error.value = err.message;
  }
};

const checkout = async () => {
  error.value = '';
  success.value = '';
  if (!items.value.length) {
    error.value = 'Votre panier est vide.';
    return;
  }
  try {
    await request('/orders/', { method: 'POST' });
    items.value = [];
    success.value = 'Commande passée avec succès.';
  } catch (err) {
    error.value = err.message;
  }
};

onMounted(loadCart);
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Votre panier</h1>
      <span class="badge">{{ items.length }} articles</span>
    </div>

    <div v-if="!isAuthenticated" class="error">Connectez-vous pour gérer votre panier.</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div v-if="loading">Chargement...</div>
    <template v-else>
      <ul class="list">
        <li v-for="item in items" :key="item.id" class="list-item">
          <div>
            <div class="product-title">{{ item.product.name }}</div>
            <div class="muted">{{ item.product.description }}</div>
            <div class="price">{{ item.subtotal }} €</div>
          </div>
          <div class="actions">
            <input
              class="input"
              type="number"
              min="1"
              :max="item.product.stock"
              :value="item.quantity"
              @change="(e) => updateQuantity(item.id, Number(e.target.value))"
            />
            <button class="ghost" @click="removeItem(item.id)">Supprimer</button>
          </div>
        </li>
      </ul>
      <div class="heading" style="margin-top: 18px">
        <span class="product-title">Total</span>
        <span class="price">{{ total }} €</span>
      </div>
      <button class="primary" :disabled="!items.length" @click="checkout">
        Passer la commande
      </button>
    </template>
  </section>
</template>
