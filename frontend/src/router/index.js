import { createRouter, createWebHistory } from 'vue-router';
import CartView from '../views/CartView.vue';
import LoginView from '../views/LoginView.vue';
import OrdersView from '../views/OrdersView.vue';
import ProductsView from '../views/ProductsView.vue';
import RegisterView from '../views/RegisterView.vue';

const routes = [
  { path: '/', name: 'products', component: ProductsView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { path: '/cart', name: 'cart', component: CartView },
  { path: '/orders', name: 'orders', component: OrdersView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
