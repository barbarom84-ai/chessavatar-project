# Guide d'exportation de la base de données Chessmaster

## Méthode 1 : Export depuis Chessmaster (Recommandé)

1. **Ouvrez Chessmaster Grandmaster Edition**

2. **Accédez à la base de données :**
   - Menu principal → "Database" ou "Base de données"

3. **Exportez vers PGN :**
   - Sélectionnez "Export" ou "Exporter"
   - Choisissez le format **PGN** (Portable Game Notation)
   - Sélectionnez toutes les parties ou filtrez (ex: parties de Grands Maîtres uniquement)

4. **Sauvegardez le fichier :**
   - Nom suggéré : `chessmaster_games.pgn`
   - Emplacement : Dans le dossier de ChessAvatar

5. **Intégration automatique :**
   - Placez le fichier PGN dans le projet
   - ChessAvatar détectera et importera automatiquement les parties

---

## Méthode 2 : Utiliser SCID (Alternative gratuite)

Si l'export depuis Chessmaster ne fonctionne pas :

1. **Téléchargez SCID** (Shane's Chess Information Database)
   - Site : http://scid.sourceforge.net/
   - Version Windows : SCID vs. PC

2. **Ouvrez la base Chessmaster dans SCID :**
   - File → Open Database
   - Sélectionnez le dossier contenant CMXDBase.*

3. **Exportez vers PGN :**
   - Tools → Export → Export all games to PGN
   - Sauvegardez comme `chessmaster_games.pgn`

---

## Informations détectées

Base de données trouvée : `C:\Program Files (x86)\Ubisoft\Chessmaster Grandmaster Edition\Data\Base de données`

**Taille totale : 259.5 MB**

Fichiers principaux :
- `CMXDBase.dbm` : 121.4 MB (mouvements des parties)
- `CMXDBase.dbn` : 64.5 MB (noms des joueurs)
- `CMXDBase.dbh` : 59.8 MB (headers/métadonnées)
- `CMXDBase.dbj` : 7.3 MB (données de jeu)
- `CMXDBase.dbg` : 2.3 MB (informations de partie)

**Estimation : ~150,000 à 500,000 parties historiques** 🏆

---

## Une fois le fichier PGN obtenu

Placez `chessmaster_games.pgn` dans le dossier du projet, puis :

```bash
python scripts/import_pgn_database.py chessmaster_games.pgn
```

L'application pourra alors :
- 📚 Rechercher des parties par joueur/ouverture
- 📊 Analyser des statistiques (taux de victoire par ouverture)
- 🎓 Afficher des parties de référence pendant le jeu
- 🤖 Entraîner des profils d'avatar basés sur des GM historiques

