# Correction et Amélioration du Système d'Avatars

## 🔴 Problèmes Identifiés

### 1. **Mode "vs_avatar" non intégré dans new_game_dialog.py**
- Le `NewGameDialog` a 3 modes mais le mode `vs_avatar` ne déclenche rien
- Pas de connexion avec le système d'avatars existant

### 2. **Gestion asynchrone problématique**
- Les avatars utilisent `asyncio` dans un thread séparé
- Risque de blocage et de conflit avec le thread UI
- Pas d'intégration avec le système de worker existant

### 3. **Pas de configuration de force de jeu basée sur le profil**
- Le Skill Level est calculé mais pas assez personnalisé
- Manque d'options pour ajuster le niveau manuellement
- Pas d'analyse approfondie du style (ouvertures, tactique vs positionnel)

### 4. **Interface limitée**
- Pas assez d'options de personnalisation de l'avatar
- Pas de prévisualisation du niveau de l'avatar
- Pas de statistiques détaillées

### 5. **Synchronisation avec le moteur principal**
- Conflit potentiel entre `EngineManager` et `AvatarEngine`
- Deux instances de Stockfish peuvent tourner en parallèle

## 📋 Plan de Correction

### ✅ TODO 1: Intégrer le mode Avatar dans NewGameDialog
**Fichier**: `ui/new_game_dialog.py`
- ✅ Déjà présent: Radio button "Jouer contre un avatar"
- ❌ Manquant: Sélecteur d'avatar dans le dialogue
- **Action**: Ajouter un `QComboBox` pour choisir l'avatar quand le mode est sélectionné

### ✅ TODO 2: Refactorer AvatarEngine pour utiliser le système de Worker
**Fichier**: `core/avatar_engine.py` + `core/engine_manager.py`
- **Problème actuel**: Avatar utilise son propre thread asyncio séparé
- **Solution**: Créer un `AvatarWorker` similaire à `EngineWorker`
- **Avantages**:
  - Pas de conflit avec le moteur principal
  - Gestion cohérente des threads
  - Signaux PyQt pour communication thread-safe

### ✅ TODO 3: Améliorer le calcul de force basé sur le profil
**Fichier**: `core/style_analyzer.py` + `core/avatar_engine.py`
- Analyser:
  - **Elo moyen** → Skill Level (0-20)
  - **Précision moyenne** → Error probability
  - **Temps de réflexion moyen** → Time limits
  - **Style tactique/positionnel** → Depth + MultiPV
  - **Ouvertures préférées** → Book moves
- Ajouter méthode `get_engine_config()` dans `PlayerStyle`

### ✅ TODO 4: Ajouter panneau de configuration d'avatar
**Fichier**: `ui/avatar_config_dialog.py` (NOUVEAU)
- Afficher les stats du joueur:
  - Nom, plateforme, Elo, taux de victoires
  - Style de jeu (Tactique/Positionnel/Équilibré)
  - Ouvertures favorites
- Curseurs pour ajuster:
  - **Skill Level** (override automatique)
  - **Agressivité** (influence les choix de coups)
  - **Temps de réflexion**
  - **Variance** (constance du jeu)
- Bouton "Tester" pour jouer quelques coups

### ✅ TODO 5: Connecter le système dans MainWindow
**Fichier**: `ui/main_window.py`
- Modifier `new_game()` pour gérer le mode `vs_avatar`:
  ```python
  if config['mode'] == "vs_avatar":
      avatar_id = config['avatar_id']
      self.start_avatar_game(avatar_id)
  ```
- Simplifier `start_avatar_game()`:
  - Supprimer le thread asyncio manuel
  - Utiliser `AvatarWorker` à la place
- Ajouter `on_avatar_move_ready()` similaire à `on_engine_move_ready()`

### ✅ TODO 6: Améliorer AvatarPanel
**Fichier**: `ui/avatar_panel.py`
- Afficher plus d'infos par avatar:
  - Photo de profil
  - Niveau estimé (★★★☆☆)
  - Style de jeu en un mot
  - Dernière partie jouée
- Bouton "⚙️ Configurer" → Ouvre `AvatarConfigDialog`
- Bouton "▶️ Jouer" → Lance `NewGameDialog` en mode avatar pré-sélectionné

### ✅ TODO 7: Gérer l'arrêt propre des avatars
**Fichier**: `ui/main_window.py`
- Dans `new_game()`, `closeEvent()`, arrêter proprement l'avatar actif
- Éviter les fuites de ressources (engine toujours running)

## 🎯 Résultat Attendu

### Scénario d'utilisation complet:

1. **Créer un avatar**:
   - Menu → Avatar → Gérer les Avatars → Créer
   - Entrer username Lichess/Chess.com
   - Importer 100 dernières parties
   - Upload photo (optionnel)
   - ✅ Analyse automatique du style
   - ✅ Configuration Stockfish automatique

2. **Configurer un avatar** (optionnel):
   - Clic sur "⚙️ Configurer"
   - Voir les stats du joueur
   - Ajuster Skill Level manuellement
   - Tester quelques coups
   - Sauvegarder

3. **Jouer contre un avatar**:
   - Fichier → Nouvelle partie
   - Sélectionner "Jouer contre un avatar"
   - Choisir l'avatar dans la liste déroulante
   - Choisir couleur (Blanc/Noir/Aléatoire)
   - Choisir cadence
   - Cliquer "Commencer"
   - ✅ Partie démarre, avatar joue selon son style
   - ✅ Affichage du nom et photo de l'avatar pendant la partie

4. **Pendant la partie**:
   - ✅ Avatar réfléchit (temps réaliste)
   - ✅ Avatar fait des erreurs occasionnelles (humain)
   - ✅ Style de jeu cohérent avec les analyses
   - ✅ Pendule fonctionne
   - ✅ Notation mise à jour
   - ✅ Possibilité d'abandonner / proposer nulle

5. **Fin de partie**:
   - ✅ Dialogue de fin de partie
   - ✅ Statistiques sauvegardées pour l'avatar
   - ✅ Moteur avatar arrêté proprement

## 🔧 Détails Techniques

### Configuration Stockfish basée sur profil:

```python
def calculate_engine_config(player_style: PlayerStyle) -> Dict:
    """Calculate Stockfish config from player style"""
    config = {}
    
    # Skill Level (0-20) basé sur Elo
    if player_style.average_elo < 1200:
        config["Skill Level"] = 0
    elif player_style.average_elo < 1400:
        config["Skill Level"] = 5
    elif player_style.average_elo < 1600:
        config["Skill Level"] = 8
    elif player_style.average_elo < 1800:
        config["Skill Level"] = 12
    elif player_style.average_elo < 2000:
        config["Skill Level"] = 15
    elif player_style.average_elo < 2200:
        config["Skill Level"] = 18
    else:
        config["Skill Level"] = 20
    
    # UCI_Elo (si supporté)
    config["UCI_LimitStrength"] = True
    config["UCI_Elo"] = player_style.average_elo
    
    # Time limits (en secondes)
    # Joueur rapide → moins de temps
    # Joueur lent → plus de temps
    if player_style.avg_move_time:
        config["Move Overhead"] = min(50, int(player_style.avg_move_time * 1000))
    
    # MultiPV basé sur style
    # Tactique → MultiPV 1 (coups précis)
    # Positionnel → MultiPV 3 (plus de variantes)
    if player_style.tactical_rating > 0.7:
        config["MultiPV"] = 1
    else:
        config["MultiPV"] = 3
    
    return config
```

### Architecture des Workers:

```
┌─────────────────┐
│   MainWindow    │
│   (UI Thread)   │
└────────┬────────┘
         │
         ├─────────────────┐
         │                 │
┌────────▼────────┐ ┌─────▼──────────┐
│  EngineManager  │ │ AvatarManager  │
│   (Analysis)    │ │   (Opponent)   │
└────────┬────────┘ └─────┬──────────┘
         │                 │
┌────────▼────────┐ ┌─────▼──────────┐
│  EngineWorker   │ │  AvatarWorker  │
│  (QThread +     │ │  (QThread +    │
│   asyncio loop) │ │   asyncio loop)│
└─────────────────┘ └────────────────┘
```

**Avantages**:
- Pas de conflit: 2 loops séparés
- Thread-safe: signaux PyQt
- Cohérent: même pattern pour les deux

## 📝 Fichiers à Créer/Modifier

### Nouveaux fichiers:
1. `ui/avatar_config_dialog.py` - Dialogue de configuration d'avatar
2. `core/avatar_worker.py` - Worker PyQt pour avatar engine

### Fichiers à modifier:
1. `ui/new_game_dialog.py` - Ajouter sélecteur d'avatar
2. `ui/main_window.py` - Intégrer mode vs_avatar
3. `core/avatar_engine.py` - Améliorer calcul de config
4. `core/style_analyzer.py` - Ajouter méthode get_engine_config()
5. `ui/avatar_panel.py` - Améliorer affichage et boutons

## ⚡ Ordre d'Implémentation

1. **Phase 1**: Corrections critiques
   - TODO 2: Refactorer avec Workers (éviter conflits)
   - TODO 5: Connecter dans MainWindow

2. **Phase 2**: Interface
   - TODO 1: Intégrer dans NewGameDialog
   - TODO 6: Améliorer AvatarPanel

3. **Phase 3**: Personnalisation
   - TODO 3: Améliorer calcul de force
   - TODO 4: Panneau de configuration

4. **Phase 4**: Polish
   - TODO 7: Arrêt propre
   - Tests complets

## 🧪 Tests à Effectuer

1. ✅ Créer un avatar depuis Lichess
2. ✅ Créer un avatar depuis Chess.com
3. ✅ Jouer contre un avatar faible (Elo < 1400)
4. ✅ Jouer contre un avatar fort (Elo > 2000)
5. ✅ Vérifier que l'avatar fait des erreurs
6. ✅ Vérifier que le style est cohérent
7. ✅ Configurer manuellement un avatar
8. ✅ Jouer plusieurs parties d'affilée
9. ✅ Arrêter une partie en cours
10. ✅ Fermer l'app avec avatar actif

## 🎨 Interface Mockup

### NewGameDialog avec Avatar:
```
┌─────────────────────────────────────────┐
│  🎮 Nouvelle Partie                     │
├─────────────────────────────────────────┤
│  Mode de jeu:                           │
│  ○ Partie libre (analyse)               │
│  ○ Jouer contre le moteur               │
│  ● Jouer contre un avatar               │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Avatar:                           │ │
│  │ [Magnus Carlsen (2850) ▼]        │ │
│  │ ⚙️ Configurer                    │ │
│  └───────────────────────────────────┘ │
│                                         │
│  Jouer avec:                           │
│  ● Blancs  ○ Noirs  ○ Aléatoire      │
│                                         │
│  Cadence: [Blitz 5+3 ▼]               │
│                                         │
│  [Annuler]              [Commencer]    │
└─────────────────────────────────────────┘
```

### AvatarConfigDialog:
```
┌──────────────────────────────────────────────────┐
│  ⚙️ Configuration de l'Avatar                   │
├──────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────┐ │
│  │  👤 Magnus Carlsen                        │ │
│  │  🌐 Lichess • Elo: 2850                   │ │
│  │  📊 Style: Tactique • WR: 68%             │ │
│  │  🏆 100 parties analysées                 │ │
│  └────────────────────────────────────────────┘ │
│                                                  │
│  Niveau de jeu:                                 │
│  ├────────────●────┤ Skill Level: 18/20        │
│                                                  │
│  Agressivité:                                   │
│  ├─────●──────────┤ Modérée                    │
│                                                  │
│  Temps de réflexion:                           │
│  ├──────────●─────┤ 2.5s / coup                │
│                                                  │
│  Variance (erreurs):                           │
│  ├────●───────────┤ 15% (humain)               │
│                                                  │
│  Ouvertures favorites:                         │
│  • Ruy Lopez (32%)                             │
│  • Sicilienne Najdorf (28%)                    │
│  • Gambit Dame (18%)                           │
│                                                  │
│  [🎲 Tester]  [💾 Sauvegarder]  [❌ Annuler]  │
└──────────────────────────────────────────────────┘
```

Voulez-vous que je commence l'implémentation ?

