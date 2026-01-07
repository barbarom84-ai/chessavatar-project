# Guide d'utilisation des Thèmes Chessmaster

## 🎨 Accéder aux 55 thèmes Chessmaster

### Menu Principal
```
Apparence → 🎨 Thèmes Chessmaster... (Ctrl+Shift+T)
```

---

## 📋 Interface du sélecteur

### Zone Gauche : Filtre et Liste
- **Dropdown "Catégorie"** : Filtrer par type
  - Tous (55 thèmes)
  - 🪵 Bois (4)
  - 🔩 Métal (6)
  - 💎 Verre (6)
  - 🗿 Marbre/Céramique (4)
  - 🏛️ Historiques (13)
  - 🎨 Modernes (4)
  - 🎭 Cartoon (5)
  - 📏 2D/Plats (11)
  - 👑 Staunton Officiels (2)

- **Liste scrollable** : Tous les thèmes de la catégorie

### Zone Droite : Aperçu
- **Nom du thème** en grand
- **Description** détaillée
- **Image d'aperçu BMP** (500x500px)
  - Directement depuis Chessmaster
  - Qualité originale

### Boutons
- **Annuler** : Fermer sans changer
- **Appliquer** : Sélectionner le thème

---

## 🎯 Thèmes Recommandés

### Classiques
- **Staunton Official** - Tournois FIDE
- **Staunton Wood** - Bois traditionnel
- **Classic Wood** - Élégant et sobre

### Prestige
- **Lewis Chessmen** ⭐ - Pièces vikings iconiques (XIIe siècle)
- **HOS Capablanca** - Hommage au champion
- **HOS Reykjavik** - Championnat du monde 1972

### Fun
- **Raving Rabbids** 🐰 - Les lapins crétins !
- **Fairytale** 🧚 - Contes de fées
- **Cartoon 3D** - Personnages colorés

### Artistiques
- **Stained Glass** - Vitrail magnifique
- **Neon** - Effet lumineux
- **Bauhaus** - Design moderniste
- **Egyptian** - Pharaons et hiéroglyphes

### 2D Minimaux
- **Expert** - Simple et rapide
- **Newspaper** - Style journal
- **Chalkboard** - Tableau noir

---

## ⚙️ Configuration Actuelle

### Fichiers utilisés
```
C:\Program Files (x86)\Ubisoft\Chessmaster Grandmaster Edition\
└── Data\Dat\
    ├── *.dat (55 fichiers) - Modèles 3D
    └── BMP\*.bmp (55 aperçus) - Images prévisualisations
```

### Thème sauvegardé
- Fichier : `chessmaster_themes.json`
- Contenu : Dernier thème sélectionné
- Chargement : Au démarrage de l'application

---

## 🔜 Prochaines fonctionnalités

### Phase 2 (en cours)
- ✅ Menu d'accès intégré
- ✅ Dialog de sélection avec aperçus
- ✅ Sauvegarde des préférences
- 📝 Extraction des textures des fichiers .dat
- 📝 Conversion en format utilisable (SVG/PNG)
- 📝 Application visuelle sur l'échiquier

### Phase 3 (planifiée)
- 📝 Prévisualisation en temps réel
- 📝 Thèmes personnalisés utilisateur
- 📝 Import/Export de thèmes
- 📝 Galerie de screenshots

---

## 💡 Astuces

### Performance
- **Thèmes 2D** : Plus légers, chargement rapide
- **Thèmes 3D** : Plus lourds, visuels riches
- **Rabbids** : Le plus gros (51 MB) mais unique !

### Découverte
- **Parcourez toutes les catégories** : Il y a des pépites !
- **Historiques** : Collection de prestige
- **House of Staunton** : 10 designs exclusifs

### Compatibilité
- Nécessite Chessmaster Grandmaster Edition installé
- Fonctionne avec installation standard
- Détection automatique du chemin

---

## 🐛 Dépannage

### "Chessmaster not found"
**Solution** : Vérifier le chemin d'installation
```python
# Dans core/chessmaster_themes.py, ligne 17
chessmaster_path = r"C:\Program Files (x86)\Ubisoft\Chessmaster Grandmaster Edition"
```

### "Aperçu non disponible"
**Cause** : Fichier BMP manquant ou corrompu
**Solution** : Le thème reste sélectionnable

### Thème ne s'applique pas
**État actuel** : Normal - extraction .dat en développement
**Prochaine version** : Application complète

---

## 📊 Statistiques

| Catégorie | Nombre | Taille | Popularité |
|-----------|--------|--------|------------|
| 2D/Plats | 11 | ~2 MB | ⭐⭐⭐⭐⭐ |
| Historiques | 13 | ~2.5 MB | ⭐⭐⭐⭐ |
| Cartoon | 5 | ~16 MB | ⭐⭐⭐ |
| Verre | 6 | ~2 MB | ⭐⭐⭐⭐ |
| Bois | 4 | ~2 MB | ⭐⭐⭐⭐⭐ |
| Métal | 6 | ~2.5 MB | ⭐⭐⭐⭐ |
| **Total** | **55** | **181 MB** | - |

---

## 🎮 Raccourci clavier

**Ctrl+Shift+T** → Ouvre le sélecteur de thèmes Chessmaster

---

Profitez de cette collection unique de 55 thèmes professionnels ! 🎨✨

