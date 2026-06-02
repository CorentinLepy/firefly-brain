# Firefly Brain MVP V1.1

Firefly Brain est une surcouche moderne pour Firefly III. Cette version MVP V1.1 ajoute un dashboard enrichi basé sur les vraies données Firefly III.

## Fonctionnalités incluses

- Backend FastAPI
- Frontend Next.js
- PostgreSQL local pour les futures données Firefly Brain
- Connexion API Firefly III
- Lecture des comptes Firefly III
- Lecture des budgets Firefly III
- Lecture des transactions Firefly III
- Alias `/api/transactions`
- Transactions simplifiées via `/api/transactions/simple`
- Transactions non catégorisées via `/api/transactions/uncategorized`
- Dashboard enrichi : revenus, dépenses, épargne, taux d'épargne, patrimoine brut, dettes, patrimoine net, top catégories, top marchands

## Déploiement Unraid

```bash
cd /mnt/user/appdata/firefly-brain
git pull
cp backend/.env.example backend/.env
nano backend/.env
docker compose up -d --build
```

Si le fichier `backend/.env` existe déjà sur Unraid, ne l'écrase pas.

## Variables importantes

```env
DATABASE_URL=postgresql+psycopg://firefly_brain:TON_MDP@firefly-brain-db:5432/firefly_brain
APP_SECRET_KEY=UNE_CLE_LONGUE
FERNET_KEY=UNE_CLE_FERNET
FIREFLY_BASE_URL=http://192.168.1.49:8085
FIREFLY_ACCESS_TOKEN=TON_TOKEN_FIREFLY
APP_ENV=production
```

## Endpoints utiles

```text
GET /health
GET /api/firefly/status
GET /api/firefly/accounts
GET /api/firefly/budgets
GET /api/transactions
GET /api/transactions/firefly
GET /api/transactions/simple
GET /api/transactions/uncategorized
GET /api/dashboard/summary
GET /api/dashboard/summary?start=2026-05-01&end=2026-05-31
```

## URLs par défaut

```text
Frontend : http://192.168.1.49:3010
API      : http://192.168.1.49:8010/docs
```
