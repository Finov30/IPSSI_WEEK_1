# Sirene DataViz - Frontend

Application React avec TypeScript pour la visualisation interactive des données Sirene.

## 🚀 Installation

```bash
cd src/frontend
npm install
```

## 🛠️ Développement

```bash
npm run dev
```

L'application sera accessible sur http://localhost:3001 (port changé pour éviter le conflit avec Docker)

## 📦 Build

```bash
npm run build
```

## 🧪 Linting

```bash
npm run lint
```

## 📁 Structure

```
src/
├── components/       # Composants réutilisables
│   ├── Layout/      # Layout principal
│   ├── Map/         # Composants de carte Leaflet
│   └── Filters/     # Composants de filtres
├── pages/           # Pages de l'application
├── services/        # Services API
└── utils/           # Utilitaires

