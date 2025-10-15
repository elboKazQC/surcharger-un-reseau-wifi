# Script de configuration rapide pour Mini PC (Récepteur)
# Usage : .\setup_mini_pc.ps1

Write-Host "🖥️  Configuration du Mini PC comme Récepteur" -ForegroundColor Cyan
Write-Host "=" * 60

# Étape 1 : Identifier l'IP
Write-Host "`n📡 Étape 1/4 : Identification de l'IP du Mini PC" -ForegroundColor Yellow
Write-Host "Vos interfaces réseau :"
Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*"} | Format-Table InterfaceAlias, IPAddress

$ip = Read-Host "`nEntrez l'IP de ce Mini PC (ex: 192.168.1.100)"

# Étape 2 : Créer le fichier de config
Write-Host "`n📄 Étape 2/4 : Création du fichier de configuration local" -ForegroundColor Yellow

$configContent = @"
# Configuration locale du Mini PC (Récepteur)
# Ce fichier est ignoré par git - modifiez-le librement

receiver:
  udp_port: 5202
  tcp_port: 5201
  listen_ip: 0.0.0.0
  interval: 5
  output_file: receiver_log.csv

notes:
  mini_pc_ip: $ip
  config_date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
  usage: |
    Sur le PC émetteur, utilisez cette IP comme target_host:
    global:
      target_host: $ip
      ping_host: $ip
"@

$configPath = "config\mini_pc_local.yaml"
$configContent | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "✅ Fichier créé : $configPath" -ForegroundColor Green

# Étape 3 : Configurer le firewall
Write-Host "`n🔥 Étape 3/4 : Configuration du Firewall Windows" -ForegroundColor Yellow
Write-Host "Autorisation des ports 5201 (TCP) et 5202 (UDP)..."

try {
    # Supprimer les règles existantes si présentes
    Remove-NetFirewallRule -DisplayName "LoadTester UDP" -ErrorAction SilentlyContinue
    Remove-NetFirewallRule -DisplayName "LoadTester TCP" -ErrorAction SilentlyContinue
    
    # Créer nouvelles règles
    New-NetFirewallRule -DisplayName "LoadTester UDP" -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow | Out-Null
    New-NetFirewallRule -DisplayName "LoadTester TCP" -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow | Out-Null
    Write-Host "✅ Règles firewall créées avec succès" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erreur lors de la configuration du firewall (exécutez en tant qu'Administrateur)" -ForegroundColor Red
    Write-Host "   Vous pouvez le faire manuellement plus tard avec :" -ForegroundColor Yellow
    Write-Host "   New-NetFirewallRule -DisplayName 'LoadTester UDP' -Direction Inbound -Protocol UDP -LocalPort 5202 -Action Allow"
    Write-Host "   New-NetFirewallRule -DisplayName 'LoadTester TCP' -Direction Inbound -Protocol TCP -LocalPort 5201 -Action Allow"
}

# Étape 4 : Instructions finales
Write-Host "`n🚀 Étape 4/4 : Démarrage du récepteur" -ForegroundColor Yellow
Write-Host @"

Votre Mini PC est configuré comme récepteur !

📝 Configuration sauvegardée dans : config\mini_pc_local.yaml
🌐 IP du Mini PC : $ip
🔌 Ports : UDP 5202, TCP 5201

Pour démarrer le récepteur :
  loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv

Sur votre PC Principal, utilisez cette configuration :
  global:
    target_host: $ip
    ping_host: $ip

"@

Write-Host "=" * 60
Write-Host "✅ Configuration terminée !" -ForegroundColor Green

$start = Read-Host "`nVoulez-vous démarrer le récepteur maintenant ? (O/N)"
if ($start -eq "O" -or $start -eq "o") {
    Write-Host "`n🎯 Démarrage du récepteur... (Ctrl+C pour arrêter)" -ForegroundColor Cyan
    loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv
} else {
    Write-Host "`n💡 Démarrez le récepteur quand vous serez prêt avec la commande ci-dessus." -ForegroundColor Cyan
}
