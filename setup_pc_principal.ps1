# Script de configuration rapide pour PC Principal (Émetteur)
# Usage : .\setup_pc_principal.ps1

Write-Host "🖥️  Configuration du PC Principal comme Émetteur" -ForegroundColor Cyan
Write-Host "=" * 60

# Identifier l'IP du Mini PC
Write-Host "`n📡 Configuration de la connexion vers le Mini PC" -ForegroundColor Yellow
$miniPcIp = Read-Host "Entrez l'IP du Mini PC récepteur (ex: 192.168.1.100)"

# Tester la connectivité
Write-Host "`n🔍 Test de connectivité vers $miniPcIp..." -ForegroundColor Yellow
$pingResult = Test-Connection -ComputerName $miniPcIp -Count 2 -Quiet

if ($pingResult) {
    Write-Host "✅ Le Mini PC est accessible (ping réussi)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Le Mini PC ne répond pas au ping" -ForegroundColor Red
    Write-Host "   Vérifiez que l'IP est correcte et que le Mini PC est allumé" -ForegroundColor Yellow
    $continue = Read-Host "Continuer quand même ? (O/N)"
    if ($continue -ne "O" -and $continue -ne "o") {
        exit
    }
}

# Créer le fichier de config
Write-Host "`n📄 Création du fichier de configuration local..." -ForegroundColor Yellow

$configContent = @"
# Configuration locale du PC Principal (Émetteur)
# Ce fichier est ignoré par git - modifiez-le librement

global:
  target_host: $miniPcIp
  ping_host: $miniPcIp
  safety_max_mbps: 150
  output_dir: reports
  use_iperf_if_available: true

tiers:
  # Test de connectivité basique
  - name: test_connexion
    protocol: UDP
    target_bandwidth_mbps: 5
    connections: 1
    duration_s: 10
    packet_size: 512
  
  # Palier léger
  - name: palier1_leger
    protocol: UDP
    target_bandwidth_mbps: 10
    connections: 2
    duration_s: 20
    packet_size: 512
  
  # Palier moyen
  - name: palier2_moyen
    protocol: UDP
    target_bandwidth_mbps: 30
    connections: 4
    duration_s: 30
    packet_size: 1024
  
  # Palier intensif TCP
  - name: palier3_intensif
    protocol: TCP
    target_bandwidth_mbps: 50
    connections: 4
    duration_s: 40
    packet_size: 1024

notes:
  mini_pc_ip: $miniPcIp
  config_date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
  reminder: Assurez-vous que le récepteur est démarré sur le Mini PC avant de lancer les tests
"@

$configPath = "config\pc_principal_local.yaml"
$configContent | Out-File -FilePath $configPath -Encoding UTF8
Write-Host "✅ Fichier créé : $configPath" -ForegroundColor Green

# Instructions finales
Write-Host "`n🚀 Configuration terminée !" -ForegroundColor Yellow
Write-Host @"

📝 Configuration sauvegardée dans : config\pc_principal_local.yaml
🎯 Cible : $miniPcIp (Mini PC)

Avant de lancer les tests, assurez-vous que :
  ✅ Le récepteur est démarré sur le Mini PC
  ✅ Le firewall du Mini PC autorise les ports 5201/5202
  ✅ Le ping vers $miniPcIp fonctionne

Commandes disponibles :
  
  1. Tests avec configuration personnalisée :
     loadtester --config config\pc_principal_local.yaml
  
  2. Interface graphique (plus facile) :
     loadtester-gui
  
  3. Test de stress progressif :
     loadtester-stress --host $miniPcIp --start-mbps 5 --step-mbps 10 --max-mbps 150
  
  4. Vérifier la connectivité :
     ping $miniPcIp
     Test-NetConnection -ComputerName $miniPcIp -Port 5202

"@

Write-Host "=" * 60
Write-Host "✅ Prêt à tester !" -ForegroundColor Green

$choice = Read-Host "`nQue voulez-vous faire ? [1] Interface GUI  [2] Tests CLI  [3] Test stress  [Q] Quitter"
switch ($choice) {
    "1" {
        Write-Host "`n🎨 Lancement de l'interface graphique..." -ForegroundColor Cyan
        loadtester-gui
    }
    "2" {
        Write-Host "`n⚙️  Lancement des tests CLI..." -ForegroundColor Cyan
        loadtester --config config\pc_principal_local.yaml
    }
    "3" {
        Write-Host "`n🔥 Lancement du test de stress..." -ForegroundColor Cyan
        loadtester-stress --host $miniPcIp --start-mbps 5 --step-mbps 10 --max-mbps 150 --duration 15
    }
    default {
        Write-Host "`n💡 Lancez les tests quand vous serez prêt avec les commandes ci-dessus." -ForegroundColor Cyan
    }
}
