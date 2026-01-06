# 🎮 Guide d'Utilisation - Système d'Avatar IA

## Créer Votre Premier Avatar

### Étape 1: Ouvrir le Dialog

Menu → Avatar → 🤖 **Créer un Avatar IA** (ou `Ctrl+Shift+A`)

### Étape 2: Choisir la Plateforme

- **Lichess**: Pour les joueurs sur lichess.org
- **Chess.com**: Pour les joueurs sur chess.com

### Étape 3: Entrer le Nom d'Utilisateur

Exemples de joueurs publics à essayer:
- **Lichess**: Hikaru, DrNykterstein (Magnus), Bigfish1995, penguingm1
- **Chess.com**: GothamChess, GMHikaru, Magnuscarlsen

### Étape 4: Récupérer et Analyser

Cliquez **"🔍 Récupérer et Analyser"**

Vous verrez:
1. "Vérification de [username]..." ✓
2. "Récupération des parties..." (100 parties)
3. "Analyse en cours..." 
4. "Analyse terminée!" ✓

### Étape 5: Lire le Rapport

Le rapport affiche:
- 📊 Statistiques générales (Elo, victoires%)
- 🎨 Style de jeu (agressif/positionnel)
- ♟️ Performance par couleur
- 📖 Top 5 ouvertures préférées
- ⚙️ Niveau Stockfish estimé

### Étape 6: Ajouter une Photo (Optionnel)

1. Cliquez **"📁 Choisir une photo"**
2. Sélectionnez une image
3. La photo apparaît en preview

### Étape 7: Créer l'Avatar

Cliquez **"✔ Créer l'Avatar"**

✅ Avatar créé avec succès !

---

## Jouer Contre un Avatar

### Méthode 1: Via le Gestionnaire

1. Menu → Avatar → **📁 Gérer les Avatars**
2. Voir la liste de vos avatars
3. Cliquer **"▶ Jouer"** sur un avatar
4. La partie démarre !

### Méthode 2: Depuis le Panneau

*(Si le panneau avatar est visible dans l'interface)*
1. Sélectionner un avatar
2. Cliquer "Jouer"

### Pendant la Partie

- **Vous voyez:** Photo et stats de l'avatar à droite
- **L'avatar joue:** Automatiquement quand c'est son tour
- **Style respecté:** L'IA imite vraiment son style !
- **Temps de réflexion:** Variable selon le niveau

#### Exemples de Comportement:

**Joueur Agressif (Score 80/100):**
- Attaque rapide
- Sacrifices tactiques
- Parties courtes (30 coups)

**Joueur Positionnel (Score 30/100):**
- Jeu solide
- Amélioration progressive
- Parties longues (50+ coups)

---

## Gérer Vos Avatars

### Voir les Statistiques

Dans le gestionnaire, vous voyez:
- Total d'avatars créés
- Parties jouées contre chacun
- Répartition Lichess/Chess.com

### Supprimer un Avatar

1. Cliquer **"🗑 Supprimer"**
2. Confirmer
3. L'avatar et sa photo sont supprimés

---

## Conseils et Astuces

### Meilleurs Joueurs à Analyser

**Niveau Débutant (1000-1400):**
- Cherchez des joueurs avec beaucoup de parties
- Vérifiez qu'ils jouent régulièrement

**Niveau Intermédiaire (1400-1800):**
- Joueurs de clubs locaux
- Joueurs actifs en tournois

**Niveau Avancé (1800+):**
- Maîtres FIDE
- Grands Maîtres
- Streamers connus

### Astuces pour Trouver des Comptes Publics

#### Sur Lichess:
1. Allez sur lichess.org
2. Recherchez un joueur
3. Vérifiez que ses parties sont publiques
4. Copiez son nom d'utilisateur exact

#### Sur Chess.com:
1. Allez sur chess.com
2. Recherchez un joueur
3. Son profil doit être public
4. Utilisez son username exact

### Créer une "Collection" d'Adversaires

Idée: Créez plusieurs avatars de différents niveaux!

**Exemples:**
- **"Débutant Ami"** (1200 Elo) - Pour s'entraîner
- **"Rival Club"** (1600 Elo) - Pour progresser
- **"Boss Final"** (2400+ Elo) - Pour se challenger

---

## Dépannage

### "Utilisateur non trouvé"

**Causes:**
- Nom d'utilisateur incorrect
- Compte privé
- Compte inexistant

**Solution:**
- Vérifier l'orthographe
- Essayer un autre joueur
- Vérifier sur le site directement

### "Aucune partie trouvée"

**Causes:**
- Nouveau compte sans parties
- Toutes les parties sont privées

**Solution:**
- Choisir un joueur plus actif
- Vérifier qu'il a joué récemment

### "Moteur Requis"

Pour jouer contre un avatar, vous devez:
1. Menu → Moteur → Configuration
2. Ajouter Stockfish
3. Puis relancer la partie

### L'Avatar Joue Trop Fort/Faible

**C'est normal !** Le système ajuste automatiquement selon:
- L'Elo réel du joueur
- Son taux de victoires
- Ses performances

Si vous voulez un autre niveau:
→ Créez un avatar d'un joueur différent !

---

## Exemples de Profils Analysés

### Profil Agressif Type

```
🎨 STYLE DE JEU
  Agressivité:       85/100
  Tactique:          78/100
  
Ouvertures Favorites:
  - Sicilian Defense (Noirs)
  - King's Gambit (Blancs)
  - Budapest Gambit
  
→ Parties courtes, attaques directes
```

### Profil Positionnel Type

```
🎨 STYLE DE JEU
  Agressivité:       25/100
  Tactique:          35/100
  
Ouvertures Favorites:
  - Queen's Gambit (Blancs)
  - Caro-Kann (Noirs)
  - London System
  
→ Parties longues, jeu solide
```

### Profil Équilibré Type

```
🎨 STYLE DE JEU
  Agressivité:       55/100
  Tactique:          52/100
  
Ouvertures Favorites:
  - Ruy Lopez
  - Queen's Indian
  - French Defense
  
→ Adaptation au contexte
```

---

## FAQ

### Q: Combien d'avatars puis-je créer?
**R:** Illimité ! Créez autant que vous voulez.

### Q: Les avatars sont-ils sauvegardés?
**R:** Oui, dans `avatars_config.json` et le dossier `avatars/`.

### Q: Puis-je modifier un avatar?
**R:** Pour l'instant, non. Supprimez et recréez-le.

### Q: L'avatar devient-il plus fort avec le temps?
**R:** Non, il garde le niveau analysé initial.

### Q: Puis-je partager mes avatars?
**R:** Techniquement oui (fichier JSON + photos), mais pas d'export intégré pour l'instant.

### Q: Ça marche avec Chess24, FICS, etc?
**R:** Pour l'instant uniquement Lichess et Chess.com (APIs publiques).

### Q: Les avatars peuvent-ils jouer entre eux?
**R:** Pas encore implémenté, mais techniquement possible !

---

## 🎉 Amusez-vous !

Le système d'Avatar IA est une fonctionnalité unique qui rend l'entraînement aux échecs beaucoup plus personnel et motivant.

**Créez vos adversaires idéaux et progressez en vous amusant !** ♔♕♖♗♘♙

