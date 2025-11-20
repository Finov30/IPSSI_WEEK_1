# 🎨 Guide de Setup du Frontend React

## 📋 Vue d'ensemble

Le frontend React avec TypeScript est maintenant créé avec :
- ✅ React 18 + TypeScript
- ✅ Vite (build tool moderne)
- ✅ React Router pour la navigation
- ✅ Leaflet pour les cartes interactives
- ✅ Recharts pour les graphiques
- ✅ Axios pour les appels API
- ✅ 5 pages complètes pour chaque use case

## 🚀 Installation

### 1. Installer les dépendances

```bash
cd src/frontend
npm install
```

### 2. Configuration

Le frontend est configuré pour se connecter à l'API sur `http://localhost:8000` par défaut.

Pour changer l'URL de l'API, créer un fichier `.env` dans `src/frontend/` :

```env
VITE_API_URL=http://localhost:8000
```

### 3. Lancer le frontend

```bash
# Depuis la racine du projet
make run-frontend

# OU depuis src/frontend
cd src/frontend
npm run dev
```

L'application sera accessible sur **http://localhost:3001** (port changé pour éviter le conflit avec Docker)

## 📁 Structure créée

```
src/frontend/
├── package.json              # Dépendances npm
├── tsconfig.json             # Configuration TypeScript
├── vite.config.ts            # Configuration Vite
├── index.html                # Point d'entrée HTML
└── src/
    ├── main.tsx              # Point d'entrée React
    ├── App.tsx               # Application principale avec routing
    ├── index.css             # Styles globaux
    │
    ├── components/
    │   ├── Layout/
    │   │   ├── Layout.tsx    # Layout avec navigation
    │   │   └── Layout.css
    │   ├── Map/
    │   │   ├── FranceMap.tsx      # Composant carte Leaflet
    │   │   ├── FranceMap.css
    │   │   └── RegionMarker.tsx   # Marqueurs de région
    │   └── Filters/
    │       ├── YearFilter.tsx     # Filtre par année
    │       ├── SectorFilter.tsx   # Filtre par secteur
    │       ├── RegionFilter.tsx   # Filtre par région
    │       └── Filters.css
    │
    ├── pages/
    │   ├── Home.tsx          # Page d'accueil
    │   ├── Home.css
    │   ├── UseCase1.tsx     # Évolution des créations
    │   ├── UseCase2.tsx     # Répartition par sexe dirigeants
    │   ├── UseCase3.tsx     # Répartition des effectifs
    │   ├── UseCase4.tsx     # Dominance sectorielle
    │   ├── UseCase5.tsx     # Types juridiques
    │   └── UseCase.css      # Styles communs
    │
    ├── services/
    │   └── api.ts           # Client API avec Axios
    │
    └── utils/
        ├── regions.ts       # Coordonnées des régions
        └── secteurs.ts      # Mapping codes APE → libellés
```

## 🎯 Fonctionnalités

### Page d'accueil
- Vue d'ensemble des 5 use cases
- Navigation vers chaque analyse

### Use Case 1: Évolution des créations
- Carte de France avec marqueurs par région
- Graphique temporel (bar chart)
- Filtres : Année, Secteur, Région

### Use Case 2: Répartition par sexe dirigeants
- Carte de France avec répartition par région
- Graphique en camembert (pie chart)
- Filtres : Secteur, Région, Sexe

### Use Case 3: Répartition des effectifs
- Carte de France avec tailles proportionnelles
- Filtres : Secteur, Région, Tranche d'effectifs

### Use Case 4: Dominance sectorielle
- Carte de France avec couleurs par secteur dominant
- Tableau détaillé par région
- Filtre : Année

### Use Case 5: Types juridiques
- Carte de France avec visualisation
- Tableau croisé des catégories juridiques
- Filtres : Secteur, Région

## 🎨 Design

- **Couleurs** : Dégradé violet/bleu pour le header
- **Cartes** : Leaflet avec OpenStreetMap
- **Graphiques** : Recharts (bar charts, pie charts)
- **Responsive** : Adapté mobile et desktop

## 🔧 Commandes disponibles

```bash
# Développement
npm run dev          # Lance le serveur de développement (port 3000)

# Build
npm run build        # Créé le build de production

# Preview
npm run preview      # Prévisualise le build de production

# Linting
npm run lint         # Vérifie le code avec ESLint
```

## ⚠️ Notes importantes

1. **API doit être lancée** : Le frontend nécessite que l'API soit accessible sur `http://localhost:8000`
2. **Données de test** : Le frontend utilisera automatiquement les données de test si disponibles
3. **CORS** : L'API est configurée pour accepter les requêtes depuis `localhost:3000`

## 🐛 Dépannage

### Erreur : "Cannot find module"
```bash
# Réinstaller les dépendances
cd src/frontend
rm -rf node_modules package-lock.json
npm install
```

### Erreur : "API not accessible"
```bash
# Vérifier que l'API est lancée
curl http://localhost:8000/health

# Si non, lancer l'API
make run-api
```

### Port 3000 déjà utilisé
Le port a été changé à 3001 par défaut pour éviter le conflit avec le conteneur Docker frontend.
Si vous voulez utiliser le port 3000, arrêtez d'abord le conteneur Docker frontend :
```bash
docker stop sirene-frontend
```

## 📝 Prochaines améliorations possibles

- [ ] Ajouter des animations de chargement
- [ ] Implémenter le lazy loading des données
- [ ] Ajouter des exports CSV/PDF
- [ ] Améliorer les tooltips sur les cartes
- [ ] Ajouter des comparaisons temporelles
- [ ] Implémenter le partage de vues filtrées

