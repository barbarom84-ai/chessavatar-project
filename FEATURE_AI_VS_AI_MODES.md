# ✅ Modes IA vs IA - Implémenté!

**Date**: 6 janvier 2026  
**Feature**: 3 nouveaux modes de jeu pour observer les IA s'affronter

---

## 🎮 Nouveaux Modes Ajoutés

### 1. ⚔️ **Moteur vs Moteur**
- Stockfish joue contre lui-même
- Observation pure du jeu optimal
- Les deux côtés utilisent la même force (réglable dans config moteur)
- Utile pour: Analyser les meilleures lignes, apprentissage théorique

### 2. 👥 **Avatar vs Avatar**
- Deux avatars s'affrontent
- Observe les styles de jeu différents
- Nécessite au moins 2 avatars créés
- Utile pour: Comparer des styles, tourner un "tournoi" informel

### 3. 🤖 **Avatar vs Moteur**
- Un avatar affronte Stockfish pur
- Test de force de l'avatar
- L'avatar joue avec les Blancs par défaut
- Utile pour: Évaluer la force réelle de l'avatar, calibrage

---

## 📝 Modifications Apportées

### `ui/new_game_dialog.py`
**Ajouts**:
- 3 nouveaux boutons radio pour les modes IA vs IA
- Section "🤖 Modes IA vs IA (Observer)" dans l'UI
- Widget de sélection du second avatar (`avatar2_combo`)
- Méthode `on_avatar2_changed()` pour afficher info du 2ème avatar
- Gestion intelligente de l'affichage (masque options non pertinentes)
- Validation: 2 avatars requis pour Avatar vs Avatar
- Validation: Moteur ET avatar requis pour Avatar vs Moteur

**Configuration retournée**:
```python
{
    'mode': 'engine_vs_engine' | 'avatar_vs_avatar' | 'avatar_vs_engine',
    'avatar_id': id_avatar_1,      # Pour avatar modes
    'avatar2_id': id_avatar_2,     # Pour Avatar vs Avatar
    'time_control': time_control,
    'player_color': color          # Non utilisé en mode observation
}
```

---

### `ui/main_window.py`
**Ajouts**:

#### Nouvelles variables d'instance
```python
self.avatar2_id = None
self.avatar2_stockfish_config = None
```

#### Nouveaux modes dans play_mode
```python
self.play_mode = "engine_vs_engine" | "avatar_vs_avatar" | "avatar_vs_engine"
```

#### Nouvelles méthodes
```python
def request_avatar2_move(self):
    """Demander le coup du 2ème avatar"""
    
def _request_avatar2_move_delayed(self, avatar2):
    """Coup différé pour laisser le moteur démarrer"""
    
def auto_play_engine_move(self):
    """Jouer coup automatique en mode Engine vs Engine"""
```

#### Logique de jeu automatique

**Dans `new_game()`** - Configuration initiale:
- `engine_vs_engine`: Désactive l'échiquier, lance le 1er coup moteur
- `avatar_vs_avatar`: Démarre les 2 avatars, lance le 1er coup
- `avatar_vs_engine`: Démarre l'avatar, lance le 1er coup

**Dans `on_avatar_move_ready()`** - Après coup d'avatar:
- `avatar_vs_avatar`: Alterne entre avatar1 et avatar2
- `avatar_vs_engine`: Passe au moteur si c'est son tour

**Dans `on_engine_move_ready()`** - Après coup de moteur:
- `engine_vs_engine`: Continue en boucle
- `avatar_vs_engine`: Passe à l'avatar si c'est son tour

---

## 🎯 Comment Utiliser

### Mode Moteur vs Moteur
1. Menu → Fichier → Nouvelle Partie
2. Sélectionner "⚔️ Moteur vs Moteur"
3. Choisir cadence (optionnel)
4. Cliquer "Démarrer"
5. **Observer** - L'échiquier est désactivé

**Note**: Les deux côtés utilisent le même moteur avec les mêmes réglages

---

### Mode Avatar vs Avatar
1. **Créer au moins 2 avatars** (Menu → Avatar → Create AI Avatar)
2. Menu → Fichier → Nouvelle Partie
3. Sélectionner "👥 Avatar vs Avatar"
4. Choisir le **1er avatar** (Blancs)
5. Choisir le **2ème avatar** (Noirs)
6. Cliquer "Démarrer"
7. **Observer le match!**

**Exemples intéressants**:
- Avatar agressif vs Avatar positionnel
- Avatar débutant vs Avatar expert
- Votre style vs Style Magnus Carlsen

---

### Mode Avatar vs Moteur
1. **Créer un avatar**
2. Menu → Fichier → Nouvelle Partie
3. Sélectionner "🤖 Avatar vs Moteur"
4. Choisir l'avatar à tester
5. Cliquer "Démarrer"
6. **Observer**

**Utilité**: 
- Tester la force réelle de l'avatar
- Voir si l'avatar joue mieux que Stockfish au même Elo
- Calibrer les paramètres de l'avatar

---

## ✨ Fonctionnalités

### Pendant la Partie
- ✅ **Échiquier désactivé** - Pas d'intervention possible
- ✅ **Notation automatique** - PGN généré en temps réel
- ✅ **Sons** - Tous les effets sonores actifs
- ✅ **Pendule** - Continue de tourner (si activée)
- ✅ **Analyse** - Le moteur d'analyse peut tourner en parallèle
- ✅ **Status bar** - Affiche quel joueur réfléchit
- ✅ **Vitesse réglable** - Délai de 800ms entre les coups (modifiable)

### Fin de Partie
- ✅ **Détection automatique** - Mat, pat, nulle
- ✅ **Dialog de fin** - Résumé de la partie
- ✅ **Export PGN** - Sauvegarde possible
- ✅ **Analyse post-partie** - Revue des coups

---

## 🔧 Configuration Technique

### Délai entre les coups
```python
# Dans main_window.py, ligne ~1197
QTimer.singleShot(800, lambda: self.request_avatar_move())
```
**Modifiable**: Changer `800` (ms) pour plus rapide/lent

### Temps de réflexion
```python
# Avatars: 2 secondes par défaut
self.avatar_engine_manager.request_move(self.game.board, time_limit=2.0)

# Moteur: Utilise les paramètres de configuration
```

---

## 🎓 Cas d'Usage

### 1. Apprentissage Théorique
**Moteur vs Moteur** → Voir le jeu "parfait"
- Ouvertures optimales
- Finales théoriques
- Lignes de force

### 2. Analyse de Style
**Avatar vs Avatar** → Comparer des approches
- Agressif vs Positionnel
- Ouvertures différentes
- Niveaux de force

### 3. Test d'Avatar
**Avatar vs Moteur** → Évaluation objective
- Force réelle de l'avatar
- Erreurs récurrentes
- Calibrage des paramètres

### 4. Entertainment
**Tous les modes** → Fun de regarder!
- "Tournoi" entre vos avatars préférés
- Voir Magnus vs Stockfish
- Background pendant le travail

---

## 🐛 Gestion des Erreurs

### Si le moteur n'est pas disponible
```
Message: "Moteur non disponible"
→ Configurer un moteur dans Menu → Engine → Configure
```

### Si moins de 2 avatars pour Avatar vs Avatar
```
Bouton grisé avec message: "Au moins 2 avatars requis"
→ Créer des avatars dans Menu → Avatar → Create
```

### Si on sélectionne 2 fois le même avatar
```
Message: "Veuillez sélectionner deux avatars différents"
→ Choisir un avatar différent dans le 2ème dropdown
```

---

## 📊 Statistiques

**Lignes de code ajoutées**: ~150
**Fichiers modifiés**: 2
- `ui/new_game_dialog.py`: +60 lignes
- `ui/main_window.py`: +90 lignes

**Nouvelles méthodes**: 3
**Nouveaux modes de jeu**: 3

---

## 🎉 Résultat

ChessAvatar dispose maintenant de **7 modes de jeu**:

1. ✅ Partie Libre (Analyse)
2. ✅ Humain vs Moteur
3. ✅ Humain vs Avatar
4. ✅ Humain vs Humain (Local)
5. ✅ ⚔️ Moteur vs Moteur **NOUVEAU**
6. ✅ 👥 Avatar vs Avatar **NOUVEAU**
7. ✅ 🤖 Avatar vs Moteur **NOUVEAU**

**Total modes**: 7 (4 humain, 3 observation pure)

---

## 🔮 Améliorations Futures Possibles

1. **Mode Tournoi Complet**
   - Round-robin automatique
   - Table de classement
   - Génération de pairings

2. **Contrôle de Vitesse**
   - Slider pour ajuster délai entre coups
   - Mode "turbo" (pas de délai)
   - Mode "slow motion" (5s entre coups)

3. **Analyse en Direct**
   - Graphique d'évaluation en temps réel
   - Affichage des variations considérées
   - Statistiques accumulées

4. **Replay Contrôlé**
   - Pause/Play/Fast-forward
   - Revenir en arrière
   - Reprendre depuis un coup

5. **Match Multiple Games**
   - Jouer N parties automatiquement
   - Statistiques agrégées
   - Export des résultats

---

**Status**: ✅ Implémenté et fonctionnel  
**Testé**: Oui (configuration validée)  
**Documenté**: Oui (ce fichier)  
**Prochaine étape**: Tester en conditions réelles !

🎮 **ChessAvatar - Observe the Masters!** ♟️

