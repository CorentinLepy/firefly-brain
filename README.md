# Firefly Brain MVP

Firefly Brain est une surcouche moderne pour Firefly III. Ce squelette contient :

- Backend FastAPI
- Frontend Next.js
- PostgreSQL
- Docker Compose
- Client Firefly III isolé
- Endpoints MVP dashboard, connexion Firefly, transactions, patrimoine et crédits

## Démarrage

```bash
docker compose up -d --build
```

API : http://localhost:8010/docs  
Frontend : http://localhost:3010

## Configuration

Modifier `backend/.env` :

```env
DATABASE_URL=postgresql+psycopg://firefly_brain:change_me_strong_password@firefly-brain-db:5432/firefly_brain
APP_SECRET_KEY=change_me_very_long_random_secret
FERNET_KEY=generate_with_python_cryptography_fernet
FIREFLY_BASE_URL=https://firefly.example.com
FIREFLY_ACCESS_TOKEN=your_firefly_token
```

## Générer une clé Fernet

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
