# Guide de Deploiement - DataCollect Pro Cameroun

## Environnements

| Environnement | URL | Description |
|---------------|-----|-------------|
| Production | https://datacollect-pro-cameroun.onrender.com | Application de production |
| API | https://datacollect-api.onrender.com | API FastAPI |

## Deploiement Local (Docker Compose)

### Prerequisites
- Docker 24+
- Docker Compose 2+

### Commandes

```bash
# Construction et demarrage
docker-compose up --build -d

# Verification des services
docker-compose ps

# Logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Arret
docker-compose down

# Avec suppression des volumes (reinitialisation DB)
docker-compose down -v
```

### Ports
| Service | Port | URL |
|---------|------|-----|
| Frontend | 3000 | http://localhost:3000 |
| Backend API | 8000 | http://localhost:8000/docs |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| PgAdmin | 5050 | http://localhost:5050 |

## Deploiement Render.com

### Methode 1: Blueprint (Recommandee)

1. Connecter le depot GitHub dans le Dashboard Render
2. Aller sur https://dashboard.render.com/blueprints
3. Cliquer "New Blueprint Instance"
4. Selectionner `choe73/datacollect-pro-cameroun`
5. Render detecte automatiquement `render.yaml`

### Methode 2: API Render

```bash
# 1. Recuperer l'ownerId
OWNER_ID=$(curl -s -H "Authorization: Bearer $RENDER_API_KEY" \
  "https://api.render.com/v1/owners" | jq -r '.[0].owner.id')

# 2. Creer le blueprint
curl -X POST "https://api.render.com/v1/blueprints" \
  -H "Authorization: Bearer $RENDER_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"datacollect-pro-cameroun\",
    \"repo\": \"https://github.com/choe73/datacollect-pro-cameroun\",
    \"branch\": \"main\",
    \"ownerId\": \"$OWNER_ID\"
  }"
```

### Services Render

| Service | Type | Description |
|---------|------|-------------|
| datacollect-backend | Web | API FastAPI + Uvicorn |
| datacollect-frontend | Static | React build statique |
| datacollect-worker | Worker | Celery tasks |
| datacollect-beat | Worker | Celery scheduler |
| datacollect-db | Database | PostgreSQL + PostGIS |
| datacollect-redis | Redis | Cache, sessions, Celery |

### Variables d'environnement requises

```bash
# Backend
DATABASE_URL=postgresql://... (auto depuis DB Render)
REDIS_URL=redis://... (auto depuis Redis Render)
SECRET_KEY=<genere automatiquement>
ENVIRONMENT=production
CELERY_BROKER_URL=redis://...

# Frontend
VITE_API_URL=https://datacollect-api.onrender.com/api/v1
```

## CI/CD Pipeline

### GitHub Actions
- `.github/workflows/ci.yml` : Tests + build Docker a chaque push
- `.github/workflows/deploy.yml` : Deploiement auto sur Render apres merge main

### Flux de travail
1. Push sur branche feature
2. CI execute tests backend + frontend
3. PR vers main
4. Merge -> deploy auto sur Render

## Verification post-deploiement

```bash
# Health check
curl https://datacollect-api.onrender.com/api/v1/health

# Documentation API
curl https://datacollect-api.onrender.com/api/v1/docs

# Frontend
curl https://datacollect-pro-cameroun.onrender.com
```

## Troubleshooting

### Problemes courants

| Symptome | Cause probable | Solution |
|----------|---------------|----------|
| 502 Bad Gateway | Backend non demarre | Verifier logs Render backend |
| DB connection failed | URL incorrecte | Verifier DATABASE_URL dans env |
| Celery tasks pending | Redis non connecte | Verifier REDIS_URL |
| Frontend blank | Build React echoue | Verifier logs build Render |

### Commandes de debug

```bash
# Logs Render CLI
render logs --service datacollect-backend

# SSH sur le service
render ssh --service datacollect-backend

# Redeploy manuel
curl -X POST "https://api.render.com/v1/services/{service_id}/deploys" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```
