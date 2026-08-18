# MiniMax-Music3 — AI Music Studio

> Generez de la musique complète (chansons avec paroles ou instrumentals) via le modèle MiniMax-Music3 (8B+0.6B).

## 🎵 Fonctionnalités

- **Génération de chansons** — lyrics + description musicale → audio 32kHz stereo WAV
- **Mode instrumental** — génération sans paroles
- **Player intégré** — lecture et téléchargement audio dans le navigateur
- **Historique** — liste des générations précédentes avec lecture directe
- **Génération de paroles** — génère des paroles depuis un prompt

## 📋 Prérequis

- Python 3.12+ (uv compatible)
- GPU NVIDIA (H100/DGX Spark recommandé) **si mode local**
- Compte MiniMax API **si mode cloud**

## 🚀 Installation

```bash
# Clone du repo
git clone https://huggingface.co/MiniMaxAI/MiniMax-Music3
cd minimax-music3

# Installation
bash install.sh
```

L'installation crée :
- Venv à `~/venv/minimax-music3`
- Fichier `.env` depuis `.env.example`
- Dépendances Python installées

## ⚙️ Configuration

Copiez `.env.example` vers `.env` et configurez :

```bash
cp .env.example .env
```

### Deux modes de fonctionnement

| Mode | Configuration |
|------|---------------|
| **Cloud (MiniMax)** | Définir `MINIMAX_API_KEY` et `MINIMAX_API_URL` dans `.env` |
| **Local (SGLang-Omni)** | Laisser `MINIMAX_API_KEY` vide, démarrer SGLang-Omni local |

### Variables `.env`

| Variable | Description | Par défaut |
|----------|-------------|------------|
| `MINIMAX_API_KEY` | Clé API MiniMax (cloud) | *(requis pour cloud)* |
| `MINIMAX_API_URL` | Endpoint API MiniMax | `https://api.minimaxi.com/v1` |
| `SGLANG_HOST` | Host SGLang-Omni local | `127.0.0.1` |
| `SGLANG_PORT` | Port SGLang-Omni local | `8000` |
| `HOST` | Host du serveur | `0.0.0.0` |
| `PORT` | Port du serveur | `8643` |

## 🏃 Lancement

```bash
# Lancement standard (port 8643)
bash run.sh

# Personnaliser host et port
bash run.sh 0.0.0.0 8080
```

Le serveur expose :
- **Frontend Web** : `http://localhost:8643/`
- **API OpenAPI** : `http://localhost:8643/docs`

### Démarrage SGLang-Omni (mode local)

```bash
pip install sglang[all]
sgl-omni serve --model-path MiniMaxAI/MiniMax-Music3 --port 8000
```

## 🌐 API

### Générer de la musique

```bash
curl -X POST http://localhost:8643/api/generate \
  -H 'Content-Type: application/json' \
  -d '{
    "prompt": "A warm acoustic pop song with intimate female vocals",
    "lyrics": "[Verse]\nMorning light filtering through the pine\n[Chorus]\nSoftly the world begins to breathe",
    "seed": 7,
    "max_new_tokens": 750
  }'
```

Réponse :
```json
{
  "generation_id": "abc12345",
  "audio_url": "/static/audio/abc12345.wav",
  "duration_seconds": 30.0,
  "lyrics": "...",
  "stream": false
}
```

### Générer des paroles

```bash
curl -X POST http://localhost:8643/api/lyrics \
  -H 'Content-Type: application/json' \
  -d '{"prompt": "A nostalgic folk song about summer evenings"}'
```

### Health Check

```bash
curl http://localhost:8643/api/health
```

### Historique des générations

```bash
curl http://localhost:8643/api/history
```

## 📁 Structure du projet

```
minimax-music3/
├── backend/               # FastAPI backend
│   ├── main.py            # Entry point (FastAPI app)
│   ├── config.py          # Settings (env vars)
│   └── routes/
│       └── generation.py  # /api/generate endpoint
├── frontend/              # Frontend web
│   └── index.html         # Single-page app (player + history)
├── temp/                  # Generated audio files (git-ignored)
├── install.sh             # Setup script (idempotent)
├── run.sh                 # Launch script
├── .env.example           # Environment template
├── requirements.txt       # Python dependencies
└── README.md
```

## ⚡ Modes de génération

### Cloud (MiniMax API)

1. Obtenir une clé API MiniMax
2. Configurer `MINIMAX_API_KEY` dans `.env`
3. Démarrer le serveur

**Avantage** : Pas besoin de GPU, fonctionne partout.
**Inconvénient** : Coût par génération, dépend du service.

### Local (SGLang-Omni)

1. Installer SGLang-Omni sur GPU NVIDIA
2. Servir le modèle MiniMax-Music3
3. Laisser `MINIMAX_API_KEY` vide dans `.env`

**Avantage** : Gratuit, contrôlé, pas de limite.
**Inconvénient** : Besoin GPU, plus lent que cloud.

## 🎨 Customisation

- Modifier le thème dans le CSS de `frontend/index.html` (variables CSS `:root`)
- Ajouter des plugins FastAPI dans `backend/routes/`
- Étendre les paramètres (replaygain, tempo, etc.) dans `generation.py`

## License

MIT
