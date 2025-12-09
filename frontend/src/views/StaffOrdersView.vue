<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue';
import { request } from '../api';
import { useAuth } from '../composables/useAuth';

const { isAuthenticated, isStaff } = useAuth();
const orders = ref([]);
const loading = ref(false);
const error = ref('');
const refreshInterval = ref(null);

const statusOptions = ['pending', 'paid', 'shipped', 'cancelled'];

const loadOrders = async () => {
  if (!isAuthenticated.value || !isStaff.value) return;
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

const updateStatus = async (orderId, status) => {
  error.value = '';
  try {
    await request(`/orders/${orderId}/set_status/`, {
      method: 'PATCH',
      body: { status },
    });
    await loadOrders();
  } catch (err) {
    error.value = err.message;
  }
};

const pendingCount = computed(
  () => orders.value.filter((o) => o.status === 'pending').length,
);

onMounted(() => {
  loadOrders();
  refreshInterval.value = setInterval(loadOrders, 10000);
});

onUnmounted(() => {
  if (refreshInterval.value) clearInterval(refreshInterval.value);
});
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Tableau employés</h1>
      <span class="badge">{{ pendingCount }} en attente</span>
    </div>
    <div v-if="!isAuthenticated" class="error">Connectez-vous.</div>
    <div v-else-if="!isStaff" class="error">Accès réservé au staff.</div>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="loading">Chargement...</div>

    <div v-else class="grid">
      <article v-for="order in orders" :key="order.id" class="card">
        <div class="heading">
          <div class="product-title">Commande #{{ order.id }}</div>
          <span class="badge">{{ order.status }}</span>
        </div>
        <p class="muted">Client : {{ order.user?.username || 'N/A' }}</p>
        <p class="muted">Total : {{ order.total_amount }} €</p>
        <ul class="list">
          <li v-for="item in order.items" :key="item.id" class="list-item">
            <div class="product-title">{{ item.product.name }}</div>
            <div class="muted">x{{ item.quantity }}</div>
          </li>
        </ul>
        <div class="form-row" style="margin-top: 12px">
          <select
            class="select"
            :value="order.status"
            @change="(e) => updateStatus(order.id, e.target.value)"
          >
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ status }}
            </option>
          </select>
        </div>
      </article>
    </div>
  </section>
</template>
