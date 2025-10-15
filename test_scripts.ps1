# Test de syntaxe des scripts PowerShell
# Ce script vérifie que les scripts setup sont syntaxiquement corrects

Write-Host "🔍 Vérification de la syntaxe des scripts..." -ForegroundColor Cyan
Write-Host ""

$scripts = @(
    "setup_mini_pc.ps1",
    "setup_pc_principal.ps1"
)

$allOk = $true

foreach ($script in $scripts) {
    Write-Host "Vérification de $script... " -NoNewline
    
    if (Test-Path $script) {
        try {
            # Tenter de parser le script
            $null = Get-Command ".\$script" -ErrorAction Stop
            Write-Host "✅ OK" -ForegroundColor Green
        } catch {
            Write-Host "❌ ERREUR" -ForegroundColor Red
            Write-Host "   $($_.Exception.Message)" -ForegroundColor Yellow
            $allOk = $false
        }
    } else {
        Write-Host "❌ FICHIER INTROUVABLE" -ForegroundColor Red
        $allOk = $false
    }
}

Write-Host ""
if ($allOk) {
    Write-Host "✅ Tous les scripts sont valides !" -ForegroundColor Green
} else {
    Write-Host "❌ Des erreurs ont été détectées" -ForegroundColor Red
}
