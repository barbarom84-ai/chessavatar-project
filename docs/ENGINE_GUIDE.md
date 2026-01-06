# ChessAvatar - Engine Integration Guide

## Vue d'ensemble

ChessAvatar intègre un système complet de gestion de moteurs d'échecs UCI, permettant l'analyse en temps réel des positions et l'affichage des évaluations.

## Installation d'un Moteur

### 1. Télécharger Stockfish (Recommandé)

**Stockfish** est le moteur d'échecs le plus fort et gratuit.

1. Visitez: https://stockfishchess.org/download/
2. Téléchargez la version Windows
3. Extrayez `stockfish.exe` dans un dossier de votre choix

### 2. Configuration dans ChessAvatar

1. Lancez ChessAvatar
2. Menu **Moteur → Configuration des moteurs...**
3. Cliquez **➕ Ajouter**
4. **Nom**: `Stockfish 16` (ou votre version)
5. **Chemin**: Cliquez **📁 Parcourir** et sélectionnez `stockfish.exe`
6. **Protocole**: UCI (par défaut)
7. Cliquez **💾 Sauvegarder**

### 3. Démarrer le Moteur

1. Menu **Moteur → Sélectionner le moteur → Stockfish 16**
2. Le moteur démarre automatiquement
3. Status "Moteur: Stockfish 16" s'affiche en vert

## Utilisation de l'Analyse

### Interface d'Analyse

Le panneau d'analyse se trouve sous l'échiquier et comprend:

#### 1. Barre d'Évaluation
- Barre verticale visuelle
- Blanc en bas, Noir en haut
- Ligne bleue au centre = égalité
- Plus la couleur domine, plus elle a l'avantage

#### 2. Évaluation Numérique
- Affichage en pawns (pions)
- `+2.50` = avantage blanc de 2.5 pions
- `-1.80` = avantage noir de 1.8 pions
- `Mat en 3` = mat forcé en 3 coups

#### 3. Informations Techniques
- **Profondeur**: Nombre de coups analysés à l'avance
- **Nœuds**: Positions calculées
- **N/s**: Vitesse de calcul (nœuds par seconde)

#### 4. Meilleures Lignes (Multi-PV)
Affiche les 3 meilleures continuations:
```
1. [+0.65] Nf3 d5 exd5 Nxd5 d4 ...
2. [+0.42] d4 d5 Nf3 Nf6 c4 ...
3. [+0.38] c4 e6 Nf3 d5 d4 ...
```

### Lancer l'Analyse

**Méthode 1: Manuel**
1. Cliquez **▶ Analyser** dans le panneau d'analyse
2. L'analyse commence et se met à jour en temps réel

**Méthode 2: Automatique**
1. Lancez l'analyse une fois
2. Chaque coup joué sera automatiquement analysé

### Arrêter l'Analyse

- Cliquez **⏹ Arrêter** dans le panneau d'analyse
- Ou menu **Moteur → Arrêter le moteur**

## Fonctionnalités Avancées

### Multi-PV (Variations Multiples)
Par défaut, ChessAvatar analyse les 3 meilleures variations simultanément. Cela permet de:
- Comparer différentes stratégies
- Identifier les alternatives
- Comprendre la complexité de la position

### Analyse Continue
L'analyse se poursuit tant que le moteur est actif et que vous jouez des coups. Parfait pour:
- Entraînement
- Analyse post-partie
- Vérification de tactiques

### Configuration du Temps
L'analyse est limitée à 2 secondes par position par défaut, ce qui offre un bon équilibre entre vitesse et précision.

## Interprétation des Évaluations

### Évaluation en Centipawns
- `0.00` = Position égale
- `+1.00` = Avantage d'un pion pour les blancs
- `-0.50` = Léger avantage pour les noirs
- `+3.00` = Avantage décisif pour les blancs

### Mat (Checkmate)
- `M5` = Mat forcé en 5 coups
- Plus le nombre est petit, plus le mat est proche
- Le bord de l'évaluation devient vert (blanc) ou rouge (noir)

### Profondeur d'Analyse
- **Profondeur 15-20**: Analyse rapide, suffisante pour la plupart des positions
- **Profondeur 25-30**: Analyse approfondie
- **Profondeur 35+**: Analyse très profonde pour positions complexes

## Dépannage

### Le moteur ne démarre pas
1. Vérifiez que le chemin vers l'exécutable est correct
2. Assurez-vous que le fichier `.exe` existe
3. Vérifiez que le protocole UCI est sélectionné
4. Testez le moteur dans une invite de commande: `stockfish.exe`

### L'analyse est lente
- Normal pour des positions complexes
- Stockfish calcule des millions de positions
- Augmentez le temps d'analyse si nécessaire

### Erreur "Engine not found"
Le fichier `.exe` a été déplacé ou supprimé:
1. Reconfigurez le moteur
2. Vérifiez l'emplacement du fichier

## Moteurs Compatibles

### UCI (Universal Chess Interface)
- ✅ Stockfish (gratuit, le plus fort)
- ✅ Komodo (commercial)
- ✅ Leela Chess Zero (gratuit, neural network)
- ✅ Houdini (commercial)
- ✅ Fire (gratuit)
- ✅ Ethereal (gratuit)

### Configuration Multiple
Vous pouvez configurer plusieurs moteurs et basculer entre eux:
1. Configurez tous vos moteurs
2. Menu **Moteur → Sélectionner le moteur**
3. Choisissez celui à utiliser

## Raccourcis Clavier

- `Ctrl+Shift+E` - Démarrer le moteur
- Menu Moteur pour toutes les options

## Conseils d'Utilisation

1. **Entraînement**: Jouez vos coups d'abord, puis comparez avec le moteur
2. **Analyse**: Laissez le moteur analyser longuement les positions critiques
3. **Ouvertures**: Utilisez l'analyse pour comprendre les idées derrière les coups
4. **Finales**: Les moteurs excellent dans les finales complexes

## Architecture Technique

### EngineManager
Classe Python gérant la communication asynchrone avec les moteurs UCI:
- Communication bidirectionnelle
- Threading pour éviter le blocage de l'interface
- Gestion des timeouts et erreurs

### Protocole UCI
Standard universel pour les moteurs d'échecs:
- `uci` - Initialisation
- `isready` - Vérification
- `position` - Envoi de la position
- `go` - Démarrage de l'analyse
- `stop` - Arrêt de l'analyse

### Stockage de Configuration
Les moteurs sont sauvegardés dans `engines_config.json`:
```json
{
  "engines": [
    {
      "name": "Stockfish 16",
      "path": "C:/Chess/stockfish.exe",
      "protocol": "UCI",
      "options": {}
    }
  ]
}
```

