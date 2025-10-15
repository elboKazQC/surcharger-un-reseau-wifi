# ✅ CONFIGURATION MINI PC - PRÊT !

## 📍 Informations de ce Mini PC

**IP WiFi à utiliser :** `10.136.136.137`  
**IP Ethernet (alternative) :** `10.10.249.20`

## 🎯 Ce qui est PRÊT sur ce Mini PC

✅ Projet installé (`wifi-loadtester 0.1.0`)  
✅ Environnement virtuel activé (`.venv`)  
✅ Commande `loadtester-receiver` disponible  
✅ Fichiers de protection git créés (`.gitignore`)

## 🚀 Démarrer le Récepteur (sur CE Mini PC)

```powershell
# Activer l'environnement virtuel (si pas déjà fait)
.\.venv\Scripts\Activate.ps1

# Démarrer le récepteur
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv
```

Le récepteur affichera les statistiques toutes les 5 secondes.  
Pour arrêter : `Ctrl+C`

## 📝 Sur VOTRE AUTRE PC (PC Principal)

### 1. Mettre à jour le code

```powershell
# Aller dans le dossier du projet
cd C:\path\to\surcharger-un-reseau-wifi

# Récupérer les nouveaux fichiers
git pull

# Installer/Mettre à jour le projet
pip install -e .
```

### 2. Créer votre fichier de config local

Créer : `config/pc_principal_local.yaml`

```yaml
global:
  target_host: 10.136.136.137  # IP WiFi du Mini PC
  ping_host: 10.136.136.137
  safety_max_mbps: 150
  output_dir: reports
  use_iperf_if_available: true

tiers:
  - name: test_connexion
    protocol: UDP
    target_bandwidth_mbps: 5
    connections: 1
    duration_s: 10
    packet_size: 512
  
  - name: palier_leger
    protocol: UDP
    target_bandwidth_mbps: 10
    connections: 2
    duration_s: 20
    packet_size: 512
```

### 3. Tester la connectivité

```powershell
# Tester le ping
ping 10.136.136.137

# Tester le port UDP
Test-NetConnection -ComputerName 10.136.136.137 -Port 5202
```

### 4. Lancer les tests

```powershell
# Option 1 : Interface graphique (recommandée)
loadtester-gui

# Option 2 : Ligne de commande
loadtester --config config/pc_principal_local.yaml

# Option 3 : Test de stress
loadtester-stress --host 10.136.136.137 --start-mbps 5 --step-mbps 10 --max-mbps 150
```

## 🔥 Configurer le Firewall (sur CE Mini PC)

Si le trafic ne passe pas, ouvrir PowerShell en **Administrateur** et exécuter :

```powershell
New-NetFirewallRule -DisplayName "LoadTester UDP" -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow
New-NetFirewallRule -DisplayName "LoadTester TCP" -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow
```

## 📊 Workflow Complet

1. **Sur Mini PC** : Démarrer le récepteur → Il attend du trafic
2. **Sur PC Principal** : Lancer les tests → Génère le trafic
3. **Observer** : Les deux PC affichent les statistiques
4. **Rapports** : PC Principal génère les CSV dans `reports/`

## 🔒 Fichiers Protégés (ne seront PAS commités)

- `config/pc_principal_local.yaml` (votre config sur l'autre PC)
- `config/mini_pc_local.yaml` (si vous en créez un ici)
- `receiver_log.csv` (logs de ce Mini PC)
- `receiver_*.csv` (tous les logs)

## 💡 Notes Importantes

- **Utilisez l'IP WiFi** : `10.136.136.137` (les deux PC doivent être sur le même réseau WiFi)
- **Si problème réseau** : Vérifiez que les deux PC sont sur le même réseau
- **Environnement virtuel** : N'oubliez pas d'activer `.venv` sur chaque PC
- **Le récepteur doit tourner** avant de lancer les tests depuis l'autre PC

---

## 🎯 Pour l'IA sur l'autre PC

Dites simplement :

> "Je veux configurer ce PC pour envoyer du trafic vers mon Mini PC récepteur à l'IP 10.136.136.137. Le récepteur écoute sur les ports UDP 5202 et TCP 5201."

Tous les fichiers de documentation sont dans le repo :
- `README.md` - Documentation principale
- `AI_CONTEXT.md` - Contexte complet pour l'IA
- `QUICKSTART.md` - Démarrage rapide
- `SETUP_MINI_PC.md` - Guide détaillé Mini PC

---

**✅ RÉSUMÉ : Votre Mini PC est prêt ! Il ne reste qu'à :**
1. Commiter les changements (si vous voulez)
2. Démarrer le récepteur ici
3. Aller sur l'autre PC, faire `git pull`, et configurer
