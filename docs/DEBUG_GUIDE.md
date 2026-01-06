# Guide de Débogage ChessAvatar

## 🔧 Système de Debug Automatique

ChessAvatar dispose d'un système complet de débogage et de gestion des crashs.

---

## 📁 Fichiers Créés

### 1. `debug_logger.py`
**Système de logging automatique**
- Capture toutes les erreurs et exceptions
- Crée des logs détaillés
- Génère des rapports de crash en JSON

### 2. `diagnostic.py`
**Script de diagnostic système**
- Vérifie l'état de l'installation
- Détecte les problèmes de configuration
- Génère un rapport complet

---

## 🚀 Utilisation

### Lancement Normal avec Logs

L'application crée automatiquement des logs à chaque démarrage :

```bash
python main.py
```

**Résultat** : Création automatique de `logs/chessavatar_YYYYMMDD_HHMMSS.log`

### Diagnostic Système

Pour vérifier que tout est OK avant de lancer l'app :

```bash
python diagnostic.py
```

**Ce script vérifie** :
- ✅ Version Python
- ✅ Dépendances installées (PyQt6, python-chess, etc.)
- ✅ Structure du projet
- ✅ Espace disque disponible
- ✅ Permissions d'écriture
- ✅ Crashs précédents

**Rapport généré** : `logs/diagnostic_YYYYMMDD_HHMMSS.json`

---

## 📊 Fichiers de Logs

Tous les logs sont créés dans le dossier `logs/` :

### Structure du dossier logs/
```
logs/
├── chessavatar_20260104_143052.log    # Log normal
├── crash_20260104_143052.json         # Rapport de crash (si crash)
└── diagnostic_20260104_143000.json    # Rapport de diagnostic
```

### Types de fichiers

#### 1. Logs normaux (`chessavatar_*.log`)
**Contenu** :
- Démarrage de l'application
- Actions utilisateur
- Coups d'échecs joués
- Événements moteur
- Événements avatar
- Arrêt normal

**Format** :
```
2026-01-04 14:30:52 [INFO] ChessAvatar - DÉMARRAGE DE CHESSAVATAR
2026-01-04 14:30:52 [INFO] ChessAvatar - Version: 1.0.0
2026-01-04 14:30:53 [DEBUG] ChessAvatar - Move: e2e4 | Data: {"fen": "..."}
2026-01-04 14:30:55 [INFO] ChessAvatar - Engine event: analysis_started
```

#### 2. Rapports de crash (`crash_*.json`)
**Contenu** :
- Type d'erreur
- Message d'erreur
- Stack trace complète
- État du système
- Modules installés

**Format JSON** :
```json
{
  "timestamp": "2026-01-04T14:30:52",
  "application": "ChessAvatar",
  "version": "1.0.0",
  "error": {
    "type": "AttributeError",
    "message": "...",
    "traceback": [...]
  },
  "system": {
    "platform": "Windows-10-...",
    "python_version": "3.14.0",
    ...
  }
}
```

#### 3. Diagnostics (`diagnostic_*.json`)
**Contenu** :
- Résultat de tous les checks
- État des dépendances
- Informations système

---

## 🔍 En Cas de Crash

### 1. Automatique

Quand l'application crash :
1. ✅ Un rapport de crash est créé automatiquement
2. ✅ Le message suivant s'affiche :
```
============================================================
❌ CHESSAVATAR A CRASHÉ
============================================================
Un rapport de crash a été créé: logs/crash_20260104_143052.json
Log complet disponible dans: logs/chessavatar_20260104_143052.log
============================================================
```

### 2. Manuel - Analyser le Crash

```bash
# 1. Lire le dernier crash
cd logs
# Ouvrir le fichier crash_*.json le plus récent

# 2. Voir les logs complets
# Ouvrir le fichier chessavatar_*.log correspondant

# 3. Lancer le diagnostic
cd ..
python diagnostic.py
```

### 3. Interpréter les Erreurs Courantes

#### `ImportError: No module named 'X'`
**Cause** : Module manquant
**Solution** :
```bash
pip install X
# ou
pip install -r requirements.txt
```

#### `AttributeError: 'ApplicationAttribute' has no attribute 'AA_EnableHighDpiScaling'`
**Cause** : Version Qt incompatible
**Solution** : Déjà corrigé dans la version actuelle

#### `DLL load failed`
**Cause** : PyQt6 mal installé
**Solution** :
```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install --upgrade PyQt6
```

---

## 🛠️ Utilisation Avancée

### Ajouter des Logs Personnalisés

Dans votre code, importez les fonctions de logging :

```python
from debug_logger import log_info, log_debug, log_error, log_exception

# Log simple
log_info("Utilisateur a déplacé une pièce")

# Log avec données
log_debug("Analyse moteur", depth=20, score=1.5)

# Log d'erreur
try:
    # code risqué
    pass
except Exception as e:
    log_exception("Erreur lors de l'analyse")
```

### Niveaux de Log

| Niveau | Usage | Visible Console | Visible Fichier |
|--------|-------|-----------------|-----------------|
| **DEBUG** | Détails techniques | ❌ | ✅ |
| **INFO** | Informations importantes | ✅ | ✅ |
| **WARNING** | Avertissements | ✅ | ✅ |
| **ERROR** | Erreurs récupérables | ✅ | ✅ |
| **CRITICAL** | Erreurs fatales | ✅ | ✅ |

### Logger des Événements Spécifiques

```python
from debug_logger import get_logger

logger = get_logger()

# Log un coup d'échecs
logger.log_move("e2e4", board_fen="rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR")

# Log un événement moteur
logger.log_engine_event("analysis_complete", depth=20, score=1.5)

# Log un événement avatar
logger.log_avatar_event("avatar_created", username="hikaru", platform="lichess")
```

---

## 📋 Checklist de Débogage

### Avant de Signaler un Bug

1. **Lancer le diagnostic**
   ```bash
   python diagnostic.py
   ```
   ✅ Tous les checks sont OK ?

2. **Vérifier les logs**
   - Ouvrir `logs/chessavatar_*.log` (le plus récent)
   - Chercher les lignes `[ERROR]` ou `[CRITICAL]`

3. **Si crash, récupérer le rapport**
   - Ouvrir `logs/crash_*.json` (le plus récent)
   - Noter le type d'erreur et le message

4. **Informations à fournir**
   - Fichier `crash_*.json` complet
   - Fichier `diagnostic_*.json`
   - Dernières lignes du `chessavatar_*.log`
   - Ce que vous faisiez quand ça a crashé

---

## 🧹 Nettoyage des Logs

Les logs s'accumulent avec le temps. Pour nettoyer :

### Suppression Manuelle
```bash
# Supprimer tous les logs
rm -rf logs/

# Ou sur Windows
rmdir /s /q logs
```

### Garder les N Derniers
```python
# Script Python pour garder les 10 derniers logs
from pathlib import Path
import shutil

logs_dir = Path('logs')
log_files = sorted(logs_dir.glob('*.log'))

# Garder les 10 derniers
for old_log in log_files[:-10]:
    old_log.unlink()
```

---

## 💡 Conseils

### Performance
- Les logs DEBUG ralentissent légèrement l'app
- Pour production, utiliser seulement INFO et plus

### Sécurité
- Les logs peuvent contenir des infos sensibles
- Ne pas partager publiquement sans vérifier

### Taille
- Un log typique : 100-500 KB par session
- Nettoyer régulièrement si vous testez beaucoup

---

## 🆘 Support

Si vous rencontrez un problème :

1. **Lancer le diagnostic** : `python diagnostic.py`
2. **Récupérer les fichiers** :
   - `logs/crash_*.json` (si crash)
   - `logs/diagnostic_*.json`
   - Dernières 50 lignes de `logs/chessavatar_*.log`
3. **Ouvrir une issue** sur GitHub avec ces fichiers

---

## 🔄 Commandes Rapides

```bash
# Lancer avec logs (automatique)
python main.py

# Diagnostic complet
python diagnostic.py

# Voir le dernier log
cat logs/chessavatar_*.log | tail -n 50

# Voir le dernier crash
cat logs/crash_*.json | head -n 30

# Compter les erreurs
grep ERROR logs/chessavatar_*.log | wc -l

# Nettoyer les vieux logs (garde les 5 derniers)
ls -t logs/*.log | tail -n +6 | xargs rm
```

---

**Le système de debug est maintenant actif et capture automatiquement tous les problèmes !** 🛡️

