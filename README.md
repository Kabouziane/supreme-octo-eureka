# Bazely E-commerce (Django + Vue)

Backend: Django 5 + DRF + JWT (SimpleJWT). Frontend: Vue 3 (Vite). Features: produits, panier, commandes, paiement simulé, préparation/expédition, tableau staff, admin produit avec images.

## Prérequis
- Python 3.13+ (virtualenv `.venv` déjà créé)
- Node 20+ (frontend)

## Backend
1. Activer l’environnement: `.\.venv\Scripts\activate`
2. Lancer: `python manage.py runserver 8000`
3. Variables env utiles:
   - `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=false` (prod)
   - `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`
   - `CORS_ALLOWED_ORIGINS=http://localhost:5173`
4. Endpoints clés (`/api/`):
   - Auth: `/auth/token/`, `/auth/token/refresh/`, `/auth/me/`, `/register/`
   - Produits: `/products/` (POST réservé admin)
   - Panier: `/cart/`, `/cart/items/`
   - Commandes: `/orders/` (POST crée), `/orders/{id}/pay/`
   - Staff commandes: `/orders/{id}/prepare/`, `/orders/{id}/ready_to_ship/`, `/orders/{id}/ship/`, `/orders/{id}/set_status/`
5. Tests: `python manage.py test store`

## Frontend
1. Config API: `frontend/.env.local` contient `VITE_API_BASE_URL=http://localhost:8000/api`
2. Lancer: `cd frontend && npm run dev -- --host --port 5173`
3. Build: `cd frontend && npm run build`

## Comptes de test
- Superuser/staff: `karim` / `123`
- Staff: `marius` / `123`

## Parcours utilisateur
- Catalogue (public) : lister produits, ajout panier.
- Auth: se connecter/inscrire pour utiliser panier/commande.
- Panier: `/cart` → passer commande → commande en statut `pending`.
- Paiement simulé: `/orders` → bouton “Valider paiement (test)” → statut `paid`.

## Parcours staff
- Admin produits: `/admin/products` (front) ou `/admin` (Django) pour créer produits avec `image_url`.
- Tableau staff: `/staff/orders`
  - Pour chaque item: renseigner `prepared_quantity` puis “Valider préparation” → statut `prepared` si tout prêt.
  - “Marquer à distribuer” → statut `ready_to_ship`.
  - “Envoyer par poste” → statut `shipped`.

## Sécurité & prod (rappels)
- Mettre `DEBUG=false`, secret robuste, hôtes/CORS/CSRF configurés.
- Forcer HTTPS et cookies sécurisés.
- Utiliser une DB dédiée (PostgreSQL en prod).
- Brancher un vrai PSP pour le paiement (ici, bouton de test seulement).
