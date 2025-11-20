# 🔧 Résolution du conflit de port 3000

## Problème

Le port 3000 est utilisé par un autre service (probablement Grafana ou le conteneur Docker frontend), ce qui empêche le frontend React de démarrer.

## Solution appliquée

Le port du frontend Vite a été changé de **3000** à **3001**.

## Utilisation

### Option 1 : Utiliser le nouveau port (recommandé)

Le frontend est maintenant accessible sur **http://localhost:3001**

```bash
# Relancer le frontend
make run-frontend

# Puis ouvrir http://localhost:3001 dans votre navigateur
```

### Option 2 : Libérer le port 3000

Si vous préférez utiliser le port 3000, arrêtez d'abord le service qui l'utilise :

```bash
# Vérifier quel conteneur utilise le port 3000
docker ps --filter "publish=3000"

# Arrêter le conteneur frontend Docker (si lancé)
docker stop sirene-frontend

# OU arrêter Grafana (si présent)
docker stop <nom-conteneur-grafana>

# Puis remettre le port 3000 dans vite.config.ts
```

## Vérification

Pour vérifier quel service utilise le port 3000 :

```bash
# Dans WSL
netstat -tuln | grep :3000
# OU
ss -tuln | grep :3000

# Vérifier les conteneurs Docker
docker ps --format "table {{.Names}}\t{{.Ports}}"
```

## Note

Le conteneur Docker `sirene-frontend` (si lancé) utilise le port 3000 pour servir le frontend en production (nginx). En développement, on utilise Vite directement sur le port 3001 pour éviter le conflit.

