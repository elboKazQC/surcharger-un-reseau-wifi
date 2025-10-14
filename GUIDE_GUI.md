# Guide d'Utilisation - Interface Graphique

## Lancement

Pour lancer l'interface graphique:

```bash
# Activer l'environnement virtuel (si nécessaire)
source .venv/Scripts/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows cmd

# Lancer l'interface
loadtester-gui
```

Ou directement avec Python:

```bash
python -m loadtester.gui
```

## Description de l'Interface

L'interface est divisée en plusieurs sections:

### 1. Configuration (en haut)
- **Hôte cible**: L'adresse IP de l'appareil à tester (AMR, routeur, etc.)
- **Limite sécurité (Mbps)**: Plafond maximum autorisé pour éviter une surcharge dangereuse

### 2. Niveaux de Test (milieu)
10 boutons de niveau prédéfinis, organisés sur 2 colonnes:

| Niveau | Nom | Protocole | Débit | Connexions | Durée | Indicateur |
|--------|-----|-----------|-------|------------|-------|------------|
| 1 | Léger | UDP | 5 Mbps | 1 | 10s | ⚪ Non testé |
| 2 | Faible | UDP | 10 Mbps | 2 | 15s | ✅ Succès |
| 3 | Modéré | TCP | 20 Mbps | 2 | 15s | ⚠️ Avertissement |
| 4 | Moyen | UDP | 30 Mbps | 3 | 20s | ⏳ En cours |
| 5 | Élevé | TCP | 40 Mbps | 4 | 20s | ❌ Échec |
| 6 | Intense | UDP | 50 Mbps | 5 | 25s | |
| 7 | Très Intense | TCP | 60 Mbps | 6 | 25s | |
| 8 | Extrême | UDP | 80 Mbps | 8 | 30s | |
| 9 | Critique | TCP | 100 Mbps | 10 | 30s | |
| 10 | Maximum | UDP | 120 Mbps | 12 | 30s | |

**Indicateurs visuels:**
- ⚪ Non testé (état initial)
- ⏳ Test en cours
- ✅ Succès (aucun problème)
- ⚠️ Avertissement (problèmes mineurs détectés)
- ❌ Échec (difficultés importantes)

### 3. Résultats du dernier test (bas)
Affiche les métriques détaillées:
- ⚙️ **Configuration**: protocole, débit cible vs atteint
- 📊 **Métriques réseau**: latence, gigue, perte de paquets
- 💻 **Ressources système**: utilisation CPU et RAM
- 🚨 **Alertes**: avertissements si problèmes détectés

### 4. Boutons d'action (tout en bas)
- **📊 Voir rapport complet**: Affiche l'historique de tous les tests
- **🔄 Réinitialiser**: Efface tous les résultats et recommence à zéro
- **❌ Quitter**: Ferme l'application

### 5. Barre de statut (pied de page)
Affiche l'état actuel: "Prêt", "Test en cours...", "Complété", etc.

## Scénarios d'Utilisation

### Scénario 1: Test Progressif Standard
1. Configurer l'hôte cible (ex: `192.168.1.100`)
2. Cliquer sur **Niveau 1** et attendre la fin
3. Vérifier les résultats (✅ = OK)
4. Cliquer sur **Niveau 2**, puis 3, 4...
5. Continuer jusqu'à voir ⚠️ ou ❌

### Scénario 2: Test Rapide d'un Niveau Spécifique
1. Cliquer directement sur le niveau souhaité (ex: **Niveau 5**)
2. Observer les métriques en temps réel
3. Analyser le rapport

### Scénario 3: Identification du Point de Rupture
1. Tester progressivement chaque niveau
2. Noter à quel niveau les alertes apparaissent:
   - ⚠️ Premier signe de difficulté
   - ❌ Point de rupture du réseau
3. Utiliser "Voir rapport complet" pour comparer

## Interprétation des Résultats

### ✅ Succès
- Perte de paquets < 3%
- Latence < 80 ms
- Gigue < 30 ms
- Débit atteint ≥ 80% de la cible

**Action**: Le réseau supporte bien ce niveau, vous pouvez passer au suivant.

### ⚠️ Avertissement
- Perte de paquets: 3-10%
- Latence: 80-200 ms
- Gigue: 30-50 ms
- Débit atteint: 70-80% de la cible

**Action**: Le réseau commence à montrer des signes de stress. Monitorer attentivement.

### ❌ Échec
- Perte de paquets > 10%
- Latence > 200 ms
- Débit atteint < 70% de la cible

**Action**: Le réseau est en difficulté à ce niveau. C'est le point de rupture identifié!

## Alertes Automatiques

L'interface affiche des pop-ups automatiques quand:
- Un niveau dépasse la limite de sécurité configurée
- Un test montre des difficultés critiques (❌)
- Une erreur survient pendant le test

## Rapport CSV

Même en mode GUI, un fichier CSV est généré dans `reports/` avec toutes les métriques pour analyse ultérieure ou import dans Excel/Python.

## Conseils Pratiques

1. **Commencer bas**: Toujours commencer par Niveau 1 ou 2 pour établir une baseline
2. **Attendre entre tests**: Laisser le réseau se stabiliser 10-20 secondes entre chaque niveau
3. **Limite de sécurité**: Ajuster selon votre équipement (routeur domestique: 50-100 Mbps, pro: 100-500 Mbps)
4. **Tests multiples**: Refaire les tests 2-3 fois pour confirmer les résultats
5. **Conditions similaires**: Tester dans les mêmes conditions (heure, charge réseau, distance)

## Dépannage

### La fenêtre ne s'ouvre pas
```bash
# Vérifier que Tkinter est installé
python -c "import tkinter"

# Sur Linux, installer si nécessaire:
sudo apt-get install python3-tk
```

### "Connexion refusée" lors du test
- Vérifier que l'hôte cible est accessible: `ping <adresse>`
- Pour tests locaux, utiliser `127.0.0.1`
- Vérifier le firewall

### Résultats incohérents
- Fermer autres applications réseau (téléchargements, streaming)
- Se rapprocher du point d'accès WiFi
- Utiliser câble Ethernet si possible pour la machine de test

## Personnalisation

Pour modifier les niveaux prédéfinis, éditer `src/loadtester/gui.py`:

```python
PREDEFINED_LEVELS = [
    LevelDefinition(1, "Mon Niveau Custom", "TCP", 15, 3, 20, 1024),
    # ...
]
```

## Exportation des Résultats

Les rapports CSV peuvent être ouverts avec:
- Microsoft Excel
- Google Sheets
- Python (pandas): `pd.read_csv('reports/report_*.csv')`
- LibreOffice Calc

Format des colonnes:
```
timestamp_start, tier_name, protocol, target_mbps, achieved_mbps,
latency_ms_avg, jitter_ms, packet_loss_pct, cpu_pct_avg, mem_pct_avg
```
