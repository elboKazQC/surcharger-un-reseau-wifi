# Guide pour l'IA - Configuration Multi-PC

## 🎯 Contexte du Projet

Ce projet permet de tester la charge réseau WiFi avec deux configurations possibles :

### Configuration 1 : PC Unique (Tests Locaux)
- Un seul PC qui génère du trafic vers lui-même ou vers un serveur distant

### Configuration 2 : Setup Émetteur/Récepteur (ACTUEL)
- **PC Principal** : Génère la charge réseau (émetteur)
- **Mini PC** : Reçoit et mesure le trafic (récepteur)

## 🔧 Architecture Actuelle

```
[PC Principal - Émetteur]  ----WiFi----> [Mini PC - Récepteur]
   - Génère trafic UDP/TCP             - Écoute ports 5202/5201
   - Mesure latence/ping               - Compte paquets reçus
   - Rapports dans reports/            - Log dans receiver_*.csv
   - Config: pc_principal_local.yaml   - Config: mini_pc_local.yaml
```

## 📁 Fichiers de Configuration

### Fichiers PROTÉGÉS (ignorés par git)
Ces fichiers contiennent des IPs/configs locales et ne sont JAMAIS commitées :
- `config/mini_pc_local.yaml` - Config du Mini PC récepteur
- `config/pc_principal_local.yaml` - Config du PC principal émetteur
- `config/*_local.yaml` - Toute config se terminant par _local.yaml
- `receiver_*.csv` - Tous les logs de réception
- `*_local.csv` - Tous les CSV locaux

### Fichiers COMMITABLES (templates/exemples)
- `config/example.yaml` - Exemple général
- `config/mini_pc_template.yaml` - Template pour Mini PC
- `config/pc_principal_template.yaml` - Template pour PC Principal

## 🚀 Commandes Typiques

### Sur le Mini PC (Récepteur)
```bash
# Démarrer le récepteur
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv

# Vérifier l'IP
ipconfig  # Windows

# Autoriser le firewall si nécessaire
New-NetFirewallRule -DisplayName "LoadTester UDP" -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow
New-NetFirewallRule -DisplayName "LoadTester TCP" -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow
```

### Sur le PC Principal (Émetteur)
```bash
# Tests avec config spécifique
loadtester --config config/pc_principal_local.yaml

# Interface graphique
loadtester-gui

# Test de stress progressif
loadtester-stress --host 192.168.X.X --start-mbps 5 --step-mbps 10 --max-mbps 150

# Test de connectivité
ping 192.168.X.X
Test-NetConnection -ComputerName 192.168.X.X -Port 5202
```

## 💬 Phrases Clés à Comprendre

Quand l'utilisateur dit :
- **"Je suis sur le mini PC"** → Il est sur le récepteur
- **"Je suis sur l'autre PC"** / **"PC principal"** → Il est sur l'émetteur
- **"Setup un receiver"** → Configurer ce PC comme récepteur
- **"Échanger avec l'autre PC"** → Communication émetteur ↔ récepteur

## 📊 Structure du Projet

```
src/loadtester/
├── cli.py          # Point d'entrée 'loadtester'
├── gui.py          # Point d'entrée 'loadtester-gui'
├── stress.py       # Point d'entrée 'loadtester-stress'
├── receiver.py     # Point d'entrée 'loadtester-receiver' ← IMPORTANT pour Mini PC
├── generator.py    # Génération de trafic
├── metrics.py      # Mesure latence/CPU/RAM
└── runner.py       # Orchestration des tests

config/
├── example.yaml               # Template général (commitable)
├── mini_pc_template.yaml      # Template Mini PC (commitable)
├── pc_principal_template.yaml # Template PC Principal (commitable)
└── *_local.yaml              # Configs locales (IGNORÉES par git)

reports/
└── *.csv           # Rapports générés (commitables ou non selon besoin)
```

## 🔐 Règles de Sécurité Git

### ✅ TOUJOURS ignorer :
- Fichiers avec IPs réelles
- Configs spécifiques à une machine
- Logs de réception personnels
- Pattern : `*_local.*`

### ✅ TOUJOURS commiter :
- Templates de configuration
- Code source
- Documentation
- Fichiers exemple avec IPs factices (ex: 192.168.1.10)

## 🎓 Exemples d'Interactions Utilisateur

### Exemple 1 : "Configure ce mini PC en récepteur"
```bash
# 1. Créer config locale
cp config/mini_pc_template.yaml config/mini_pc_local.yaml
# Éditer l'IP dans le fichier

# 2. Démarrer
loadtester-receiver --udp-port 5202 --tcp-port 5201
```

### Exemple 2 : "Je veux tester depuis l'autre PC"
→ L'utilisateur est sur le PC principal, il faut une config avec l'IP du Mini PC :
```yaml
# config/pc_principal_local.yaml
global:
  target_host: <IP_DU_MINI_PC>  # À obtenir de l'utilisateur
```

### Exemple 3 : "Ça ne marche pas entre les deux PC"
→ Vérifier :
1. Récepteur démarré sur Mini PC ?
2. IP correcte dans la config émetteur ?
3. Firewall autorise ports 5201/5202 ?
4. Ping fonctionne ?

## 🎯 Checklist de Setup Multi-PC

- [ ] Mini PC : IP identifiée (ipconfig)
- [ ] Mini PC : Firewall configuré (ports 5201/5202)
- [ ] Mini PC : `mini_pc_local.yaml` créé
- [ ] Mini PC : Récepteur démarré
- [ ] PC Principal : `pc_principal_local.yaml` créé avec bonne IP
- [ ] PC Principal : Test ping OK
- [ ] PC Principal : Lancement loadtester

## 📝 Notes Importantes

1. **Fichier receiver_test.csv** : Existe dans le workspace, sera ignoré par .gitignore
2. **Rapports dans reports/** : Pas ignorés par défaut (peuvent être commitées pour historique)
3. **Shell PowerShell** : Utiliser syntaxe Windows (`ipconfig`, `Test-NetConnection`)
4. **Python >=3.10** requis

## 🔄 Workflow Typique

1. **Setup Initial** (une fois)
   - Installer projet sur les 2 PC
   - Créer configs locales sur chaque PC
   - Configurer firewall

2. **Session de Test**
   - Démarrer récepteur sur Mini PC
   - Lancer tests depuis PC Principal
   - Analyser rapports

3. **Fin de Session**
   - Arrêter récepteur (Ctrl+C)
   - Sauvegarder rapports importants
   - Les configs locales restent pour prochaine fois
