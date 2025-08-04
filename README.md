# 🌱 Garden Planner Pro

Application complète de planification de jardins avec gestion de projets et système d'irrigation intelligent.

## 🚀 Démarrage Rapide

### Prérequis
- Python 3.11+
- Node.js 18+
- Docker (optionnel)

### Installation Locale

1. **Cloner le projet**
```bash
git clone <repository-url>
cd Garden_Planer_pro
```

2. **Backend (Python)**
```bash
cd app
pip install -r ../requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

3. **Frontend (React)**
```bash
cd ..
npm install
npm run dev
```

4. **Accès**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Avec Docker

```bash
# Démarrage simple
docker-compose up

# Avec cache Redis
docker-compose --profile cache up
```

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI + SQLAlchemy
- **Base de données**: SQLite (léger et simple)
- **Authentification**: JWT + CSRF Protection
- **API**: RESTful avec documentation automatique

### Frontend (React)
- **Framework**: React 18 + TypeScript
- **Build**: Vite
- **UI**: TailwindCSS + Radix UI
- **State**: Zustand + React Query

### Fonctionnalités
- ✅ Planification de jardins
- ✅ Gestion de projets
- ✅ Système d'irrigation
- ✅ Moteur agronomique
- ✅ Visualisation 3D
- ✅ Gestion des utilisateurs

## 📁 Structure

```
Garden_Planer_pro/
├── app/                    # Backend FastAPI
│   ├── api/               # Endpoints API
│   ├── core/              # Configuration
│   ├── models/            # Modèles SQLAlchemy
│   ├── services/          # Logique métier
│   └── main.py           # Point d'entrée
├── src/                   # Frontend React
│   ├── components/        # Composants UI
│   ├── features/          # Fonctionnalités
│   └── lib/              # Utilitaires
├── requirements.txt       # Dépendances Python
├── package.json          # Dépendances Node.js
├── Dockerfile            # Container unique
├── docker-compose.yml    # Orchestration simple
└── README.md            # Ce fichier
```

## 🔧 Configuration

### Variables d'environnement
```bash
# Backend (.env)
DATABASE_URL=sqlite:///./garden_planner.db
SECRET_KEY=your-secret-key-here
CLIENT_URL=http://localhost:8000

# Frontend (.env)
VITE_API_URL=http://localhost:8000/api/v1
```

## 🧪 Tests

```bash
# Backend
cd app
pytest

# Frontend
npm test
```

## 📦 Déploiement

### Production avec Docker
```bash
docker-compose up -d
```

### Production manuelle
```bash
# Backend
cd app
pip install -r ../requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
npm run build
npm run preview
```

## 🛠️ Développement

### Scripts utiles
```bash
# Démarrage rapide
./start_app.bat

# Nettoyage
npm run clean
```

### Ajout de fonctionnalités
1. Backend: Ajouter dans `app/api/v1/endpoints/`
2. Frontend: Ajouter dans `src/features/`
3. Modèles: Ajouter dans `app/models/`

## 📚 Documentation

- **API**: http://localhost:8000/docs
- **Code**: Commentaires dans le code
- **Issues**: GitHub Issues

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature
3. Commit les changements
4. Push vers la branche
5. Ouvrir une Pull Request

## 📄 Licence

MIT License - voir LICENSE pour plus de détails.

---

**Note**: Cette version est simplifiée et utilise SQLite au lieu de PostgreSQL pour faciliter le déploiement.
