<script setup>
import { onMounted, reactive, ref } from 'vue';
import { request } from '../api';
import { useAuth } from '../composables/useAuth';

const products = ref([]);
const loading = ref(false);
const error = ref('');
const success = ref('');
const quantities = reactive({});
const { isAuthenticated } = useAuth();

const loadProducts = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await request('/products/');
    products.value = data;
    data.forEach((p) => {
      quantities[p.id] = 1;
    });
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const addToCart = async (productId) => {
  success.value = '';
  error.value = '';
  try {
    const qty = quantities[productId] || 1;
    await request('/cart/items/', {
      method: 'POST',
      body: { product_id: productId, quantity: qty },
    });
    success.value = 'Produit ajouté au panier.';
  } catch (err) {
    error.value = err.message;
  }
};

onMounted(loadProducts);
</script>

<template>
  <section class="card">
    <div class="heading">
      <h1>Catalogue</h1>
      <span class="badge">{{ products.length }} produits</span>
    </div>
    <p class="muted">Ajoutez des produits actifs au panier et passez la commande.</p>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>

    <div v-if="loading">Chargement...</div>
    <div v-else class="grid products-grid">
      <article v-for="product in products" :key="product.id" class="product">
        <div class="product-title">{{ product.name }}</div>
        <img
          v-if="product.image_url"
          :src="product.image_url"
          alt="product"
          style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 160px"
        />
        <div class="muted">{{ product.description || 'Aucune description' }}</div>
        <div class="price">{{ product.price }} €</div>
        <div class="muted">Stock : {{ product.stock }}</div>
        <div class="actions">
          <input
            class="input"
            type="number"
            min="1"
            :max="product.stock"
            v-model.number="quantities[product.id]"
          />
          <button class="primary" :disabled="!isAuthenticated" @click="addToCart(product.id)">
            {{ isAuthenticated ? 'Ajouter au panier' : 'Connexion requise' }}
          </button>
        </div>
      </article>
    </div>
  </section>
</template>
