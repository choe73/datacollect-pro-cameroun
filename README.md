# DataCollect Pro Cameroun

[![CI](https://github.com/choe73/datacollect-pro-cameroun/actions/workflows/ci.yml/badge.svg)](https://github.com/choe73/datacollect-pro-cameroun/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-00a393.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Plateforme intelligente de collecte, traitement et analyse de données ouvertes du Cameroun**

![Version](https://img.shields.io/badge/version-1.0.0-orange)
![Data Size](https://img.shields.io/badge/data-450K%2B%20rows-success)

## 🎯 Objectifs

- **Automatiser** la collecte de données depuis des sources externes (World Bank, Open Data Cameroun, etc.)
- **Analyser** via des techniques statistiques avancées (régression, ACP, classification)
- **Visualiser** les résultats de manière interactive et responsive
- **Prédire** les tendances futures à partir des modèles entraînés

## 🏗️ Architecture

```
Sources Externes → Celery Workers → Redis → PostgreSQL → FastAPI → React SPA
                    (Collecte)      (Cache)  (Storage)   (API)     (UI)
```

### Stack Technologique

| Couche | Technologies |
|--------|-------------|
| **Backend** | FastAPI, PostgreSQL + PostGIS, Redis, Celery |
| **Frontend** | React 18, TypeScript, Tailwind CSS, shadcn/ui |
| **ML/Stats** | scikit-learn, scipy, pandas, plotly |
| **DevOps** | Docker, GitHub Actions, Render.com |

## 🚀 Démarrage Rapide

### Prérequis

- Docker & Docker Compose
- Git
- Make (optionnel)

### Installation

```bash
# Cloner le repository
git clone https://github.com/choe73/datacollect-pro-cameroun.git
cd datacollect-pro-cameroun

# Copier les variables d'environnement
cp .env.example .env

# Lancer l'application
docker-compose up --build
```

L'application sera accessible sur :
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **PgAdmin** : http://localhost:5050

## 📊 Modules Analytiques

### 1. Collecte de Données
- World Bank API
- Cameroon Open Data
- OpenStreetMap
- FRED/IMF
- UNICEF/WHO
- NASA POWER (météo)
- FAO

### 2. Analyse Descriptive
- Statistiques univariées et bivariées
- Corrélations (Pearson, Spearman)
- Tests statistiques (t-test, chi², ANOVA)
- Visualisations interactives

### 3. Régression Linéaire
- Simple et multiple
- Ridge / Lasso / ElasticNet
- Polynomiale (degrés 2-5)
- Diagnostics complets (VIF, résidus)

### 4. Analyse en Composantes Principales (ACP)
- Standardisation automatique
- Sélection composantes (Kaiser / variance ≥80%)
- Biplot interactif (zoom, sélection)
- Cercle des corrélations

### 5. Classification Supervisée
- Régression Logistique
- SVM
- Random Forest
- Gradient Boosting
- KNN
- Naive Bayes

### 6. Classification Non Supervisée
- K-Means
- DBSCAN
- Clustering Hiérarchique
- Gaussian Mixture Models
- Spectral Clustering

## 🛠️ Développement

### Structure du Projet

```
datacollect-pro-cameroun/
├── .github/workflows/    # CI/CD GitHub Actions
├── backend/
│   ├── app/
│   │   ├── api/        # Routes FastAPI
│   │   ├── core/       # Configuration
│   │   ├── models/     # Modèles SQLAlchemy
│   │   ├── schemas/    # Pydantic schemas
│   │   ├── services/   # Logique métier
│   │   ├── tasks/      # Tâches Celery
│   │   └── utils/      # Utilitaires
│   ├── tests/          # Tests pytest
│   ├── alembic/        # Migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/ # Composants React
│   │   ├── pages/      # Pages
│   │   ├── hooks/      # Custom hooks
│   │   ├── lib/        # Utilitaires
│   │   └── types/      # Types TypeScript
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Tests

```bash
# Backend
cd backend
pytest --cov=app tests/ --cov-report=html

# Frontend
cd frontend
npm test
```

## 📱 Responsive Design

L'application est optimisée pour :
- **Mobile** : 375×667
- **Tablette** : 768×1024
- **Desktop** : 1920×1080

## 🔒 Sécurité

- Authentification JWT (access + refresh tokens)
- Rate limiting (Redis)
- Validation Pydantic
- Headers HTTP sécurisés (HSTS, CSP)
- SQL Injection prevention (ORM)

## 📈 Performance

| Métrique | Objectif |
|----------|----------|
| Temps de chargement | < 2s |
| API response (p95) | < 200ms |
| Analyse descriptive (10k lignes) | < 5s |
| Régression (10k lignes) | < 10s |

## 📝 License

MIT License - voir [LICENSE](LICENSE)

## 👥 Auteurs

- **Choe73** - *Développement initial*

## 🙏 Remerciements

- [World Bank Open Data](https://data.worldbank.org/)
- [Cameroon Open Data](https://cameroon.opendataforafrica.org/)
- [OpenStreetMap](https://www.openstreetmap.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [shadcn/ui](https://ui.shadcn.com/)

---

**Made with ❤️ for Cameroon** 🇨🇲
