# 🚀 Scripts de Configuration Rapide

Ces scripts PowerShell facilitent la configuration initiale de vos PC pour les tests de charge réseau.

## 📋 Scripts Disponibles

### 1. `setup_mini_pc.ps1` - Configuration du Récepteur
Configure automatiquement le Mini PC comme récepteur de trafic réseau.

**Ce qu'il fait :**
- ✅ Détecte automatiquement votre IP
- ✅ Crée le fichier `config/mini_pc_local.yaml`
- ✅ Configure les règles firewall Windows
- ✅ Option de démarrer le récepteur immédiatement

**Utilisation :**
```powershell
# Méthode 1 : Exécution directe (recommandée)
# Clic droit sur le fichier → Exécuter avec PowerShell (en tant qu'Administrateur)

# Méthode 2 : Depuis PowerShell
.\setup_mini_pc.ps1

# Si erreur d'exécution de script :
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_mini_pc.ps1
```

### 2. `setup_pc_principal.ps1` - Configuration de l'Émetteur
Configure automatiquement le PC principal comme générateur de charge.

**Ce qu'il fait :**
- ✅ Demande l'IP du Mini PC récepteur
- ✅ Teste la connectivité (ping)
- ✅ Crée le fichier `config/pc_principal_local.yaml`
- ✅ Propose de lancer les tests (GUI, CLI ou Stress)

**Utilisation :**
```powershell
# Méthode 1 : Exécution directe
# Clic droit sur le fichier → Exécuter avec PowerShell

# Méthode 2 : Depuis PowerShell
.\setup_pc_principal.ps1

# Si erreur d'exécution de script :
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup_pc_principal.ps1
```

## 🔄 Workflow Complet

### Première Utilisation

**Sur le Mini PC (Récepteur) :**
1. Exécuter `setup_mini_pc.ps1` (en tant qu'administrateur)
2. Noter l'IP affichée
3. Laisser le récepteur tourner

**Sur le PC Principal (Émetteur) :**
1. Exécuter `setup_pc_principal.ps1`
2. Entrer l'IP du Mini PC (obtenue à l'étape précédente)
3. Lancer les tests (GUI recommandée)

### Utilisations Suivantes

**Sur le Mini PC :**
```powershell
# Simplement relancer le récepteur
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv
```

**Sur le PC Principal :**
```powershell
# Interface graphique (plus simple)
loadtester-gui

# Ou tests CLI
loadtester --config config\pc_principal_local.yaml

# Ou test de stress
loadtester-stress --host <IP_MINI_PC> --start-mbps 5 --step-mbps 10 --max-mbps 150
```

## ⚠️ Résolution de Problèmes

### "Impossible d'exécuter ce script"
```powershell
# Autoriser l'exécution pour cette session uniquement
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Puis réessayer
.\setup_mini_pc.ps1
```

### "Erreur lors de la configuration du firewall"
Le script nécessite des droits administrateur pour configurer le firewall.

**Solution :**
1. Clic droit sur PowerShell → Exécuter en tant qu'administrateur
2. Naviguer vers le dossier : `cd C:\Users\SWARM\Documents\GitHub\surcharger-un-reseau-wifi`
3. Relancer le script

**OU configurer manuellement :**
```powershell
# Ouvrir PowerShell en administrateur
New-NetFirewallRule -DisplayName "LoadTester UDP" -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow
New-NetFirewallRule -DisplayName "LoadTester TCP" -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow
```

### Le Mini PC ne répond pas au ping
1. Vérifier que le Mini PC est allumé et connecté au réseau
2. Vérifier l'IP : `ipconfig` sur le Mini PC
3. Vérifier que les deux PC sont sur le même réseau
4. Désactiver temporairement le pare-feu pour tester

### Le trafic ne passe pas
1. **Sur le Mini PC :** Vérifier que le récepteur est démarré
2. **Sur les deux PC :** Vérifier les règles firewall
3. **Test basique :** 
   ```powershell
   # Depuis le PC Principal
   Test-NetConnection -ComputerName <IP_MINI_PC> -Port 5202
   ```

## 📝 Fichiers Générés

Ces fichiers sont **automatiquement ignorés par git** :

| Fichier | PC | Description |
|---------|-----|-------------|
| `config/mini_pc_local.yaml` | Mini PC | Configuration du récepteur |
| `config/pc_principal_local.yaml` | PC Principal | Configuration de l'émetteur |
| `receiver_log.csv` | Mini PC | Logs de réception |
| `reports/*.csv` | PC Principal | Rapports de tests |

Vous pouvez les modifier librement sans risque de commit accidentel !

## 🎯 Commandes de Vérification

### Vérifier la configuration actuelle
```powershell
# Voir votre IP
ipconfig

# Voir les règles firewall
Get-NetFirewallRule -DisplayName "LoadTester*"

# Tester la connectivité
ping <IP_DESTINATION>
Test-NetConnection -ComputerName <IP_DESTINATION> -Port 5202
```

### Nettoyer et recommencer
```powershell
# Supprimer la config locale (si vous voulez recommencer)
Remove-Item config\mini_pc_local.yaml
Remove-Item config\pc_principal_local.yaml

# Supprimer les règles firewall
Remove-NetFirewallRule -DisplayName "LoadTester UDP"
Remove-NetFirewallRule -DisplayName "LoadTester TCP"

# Relancer le script de setup
.\setup_mini_pc.ps1  # ou setup_pc_principal.ps1
```

## 💡 Astuces

1. **Toujours démarrer le récepteur en premier** sur le Mini PC
2. **Utiliser l'interface GUI** (`loadtester-gui`) pour débuter - c'est plus visuel
3. **Noter l'IP du Mini PC** quelque part pour ne pas avoir à la chercher à chaque fois
4. **Les configs locales restent entre les sessions** - pas besoin de refaire le setup à chaque fois

## 🔗 Documentation Complète

- `README.md` - Documentation principale du projet
- `SETUP_MINI_PC.md` - Guide détaillé pour le Mini PC
- `AI_CONTEXT.md` - Guide pour l'IA (utile pour comprendre l'architecture)
- `GUIDE_GUI.md` - Guide d'utilisation de l'interface graphique
