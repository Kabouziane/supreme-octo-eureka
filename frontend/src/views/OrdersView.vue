<script setup>
import { onMounted, ref } from 'vue';
import { request } from '../api';
import { useAuth } from '../composables/useAuth';

const orders = ref([]);
const loading = ref(false);
const error = ref('');
const { isAuthenticated } = useAuth();

const loadOrders = async () => {
  if (!isAuthenticated.value) return;
  loading.value = true;
  error.value = '';
  try {
    orders.value = await request('/orders/');
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const payOrder = async (orderId) => {
  error.value = '';
  try {
    await request(`/orders/${orderId}/pay/`, { method: 'POST' });
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  }
};

onMounted(loadOrders);
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Commandes</h1>
      <span class="badge">{{ orders.length }} commandes</span>
    </div>

    <div v-if="!isAuthenticated" class="error">Connectez-vous pour voir vos commandes.</div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading">Chargement...</div>

    <div class="grid" v-else>
      <article v-for="order in orders" :key="order.id" class="card">
        <div class="heading">
          <div class="product-title">Commande #{{ order.id }}</div>
          <span class="badge">{{ order.status }}</span>
        </div>
        <p class="muted">Total : {{ order.total_amount }} €</p>
        <ul class="list">
          <li v-for="item in order.items" :key="item.id" class="list-item">
            <div>
              <div class="product-title">{{ item.product.name }}</div>
              <div class="muted">Quantité : {{ item.quantity }}</div>
            </div>
            <div class="price">{{ item.subtotal }} €</div>
          </li>
        </ul>
        <div v-if="order.status === 'pending'" class="actions" style="margin-top: 12px">
          <button class="primary" @click="payOrder(order.id)">Valider paiement (test)</button>
        </div>
      </article>
    </div>
  </section>
</template>
