# 🖥️ Configuration du Mini PC comme Récepteur

## Configuration Rapide

### 1. Identifier l'IP du Mini PC
```powershell
ipconfig
# Notez l'adresse IPv4 de votre carte WiFi/Ethernet
```

### 2. Créer votre fichier de config local
Créer : `config/mini_pc_local.yaml`

```yaml
# Ce fichier ne sera JAMAIS commité (protégé par .gitignore)
receiver:
  udp_port: 5202
  tcp_port: 5201
  listen_ip: "0.0.0.0"
  
notes:
  mini_pc_ip: "192.168.X.X"  # Remplacer par votre IP réelle
  # Cette IP sera utilisée comme target_host sur l'autre PC
```

### 3. Démarrer le récepteur
```powershell
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv
```

Le récepteur va :
- ✅ Écouter sur les ports 5202 (UDP) et 5201 (TCP)
- ✅ Afficher les statistiques toutes les 5 secondes
- ✅ Enregistrer dans `receiver_log.csv` (ignoré par git)

### 4. Configuration sur l'Autre PC

Sur votre PC principal, créer : `config/pc_principal_local.yaml`

```yaml
global:
  target_host: 192.168.X.X  # IP du Mini PC (obtenue à l'étape 1)
  ping_host: 192.168.X.X
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
```

Puis lancer :
```bash
loadtester --config config/pc_principal_local.yaml
```

## 🔥 Firewall Windows

Si le trafic ne passe pas, autoriser les ports :

```powershell
# Sur le Mini PC (récepteur)
New-NetFirewallRule -DisplayName "LoadTester UDP" -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow
New-NetFirewallRule -DisplayName "LoadTester TCP" -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow
```

## 📊 Commandes Utiles

### Test de connectivité basique
```powershell
# Depuis le PC principal vers le Mini PC
ping 192.168.X.X
Test-NetConnection -ComputerName 192.168.X.X -Port 5202
```

### Arrêter le récepteur
`Ctrl+C` dans le terminal

### Voir les logs de réception
```powershell
cat receiver_log.csv | Select-Object -Last 20
```

## 🚨 Rappel Important

**TOUS les fichiers de config locale sont ignorés par git :**
- `config/*_local.yaml`
- `config/mini_pc.yaml`
- `config/pc_principal.yaml`
- `receiver_*.csv`

Vous pouvez créer et modifier ces fichiers librement sans risque de les commiter accidentellement !

## 💡 Pour l'IA sur l'Autre PC

Quand vous communiquez avec l'IA sur votre PC principal, mentionnez :

> "J'ai un Mini PC récepteur à l'IP 192.168.X.X qui écoute sur les ports 5202 (UDP) et 5201 (TCP). Je veux tester la charge réseau entre ce PC et le Mini PC."

L'IA comprendra automatiquement la configuration grâce au README mis à jour.
