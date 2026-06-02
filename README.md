# Firefly Brain V2

Firefly Brain est une surcouche intelligente et moderne pour Firefly III. L'objectif est de garder Firefly III comme moteur financier principal et d'ajouter un cockpit de pilotage personnel : patrimoine, cash-flow, alertes, abonnements, objectifs et pistes d'optimisation.

## Nouveautés V2

- Dashboard V2 avec score financier simple.
- Endpoints d'insights financiers.
- Détection heuristique des abonnements récurrents.
- Alertes intelligentes simples : cash-flow négatif, transactions non catégorisées, taux d'épargne faible, patrimoine net négatif, abonnements coûteux.
- Objectifs financiers persistés dans PostgreSQL.
- API transactions simplifiée.
- Frontend modernisé avec sections : alertes, optimisations, abonnements, objectifs.
- Docker Compose sans secret en dur, avec `.env` racine.

## Architecture

```text
firefly-brain/
├── backend/                 # FastAPI
│   ├── app/
│   │   ├── modules/
│   │   │   ├── firefly/
│   │   │   ├── dashboard/
│   │   │   ├── transactions/
│   │   │   ├── subscriptions/
│   │   │   ├── alerts/
│   │   │   ├── insights/
│   │   │   ├── goals/
│   │   │   ├── assets/
│   │   │   └── liabilities/
│   │   └── services/finance.py
│   └── .env.example
├── frontend/                # Next.js
├── docker-compose.yml
├── .env.example
└── scripts/update-unraid.sh
```

## Déploiement Unraid

Depuis `/mnt/user/appdata/firefly-brain` :

```bash
cp .env.example .env
cp backend/.env.example backend/.env
nano .env
nano backend/.env
docker compose up -d --build
```

### `.env` racine

```env
POSTGRES_DB=firefly_brain
POSTGRES_USER=firefly_brain
POSTGRES_PASSWORD=ton_mot_de_passe_postgres
POSTGRES_PORT=5434
API_PORT=8010
WEB_PORT=3010
NEXT_PUBLIC_API_URL=http://192.168.1.49:8010
```

### `backend/.env`

```env
DATABASE_URL=postgresql+psycopg://firefly_brain:ton_mot_de_passe_postgres@firefly-brain-db:5432/firefly_brain
APP_SECRET_KEY=cle_app
FERNET_KEY=cle_fernet
FIREFLY_BASE_URL=http://192.168.1.49:8085
FIREFLY_ACCESS_TOKEN=token_firefly
APP_ENV=production
```

## Endpoints importants

```text
GET /health
GET /api/firefly/status
GET /api/dashboard/summary?start=2026-05-01&end=2026-05-31
GET /api/dashboard/comparison?start=2026-05-01&end=2026-05-31
GET /api/transactions/simple
GET /api/transactions/uncategorized
GET /api/subscriptions/detect?start=2026-01-01&end=2026-05-31
GET /api/alerts?start=2026-05-01&end=2026-05-31
GET /api/insights/overview?start=2026-05-01&end=2026-05-31
GET /api/goals
POST /api/goals
```

## Mise à jour depuis GitHub sur Unraid

```bash
cd /mnt/user/appdata/firefly-brain
cp backend/.env /mnt/user/appdata/firefly-brain-backend.env.backup
cp .env /mnt/user/appdata/firefly-brain-root.env.backup 2>/dev/null || true
git fetch origin
git reset --hard origin/main
cp /mnt/user/appdata/firefly-brain-backend.env.backup backend/.env
cp /mnt/user/appdata/firefly-brain-root.env.backup .env 2>/dev/null || true
docker compose up -d --build
```

Ou :

```bash
./scripts/update-unraid.sh
```

## Sécurité

Ne versionne jamais :

- `backend/.env`
- `.env`
- token Firefly III
- clé OpenAI
- mots de passe PostgreSQL
- secrets de notification

## Limites V2

La V2 reste un MVP évolutif. La détection d'abonnements est heuristique, les alertes sont explicables mais simples, et l'IA conversationnelle n'est pas encore intégrée. Firefly III reste la source de vérité pour les transactions, budgets, comptes et catégories.
