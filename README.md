# Outil de surcharge réseau WiFi pour tests AMR

Ce projet fournit un utilitaire en ligne de commande pour générer une charge réseau graduelle (paliers) et mesurer différents indicateurs: latence, gigue, perte de paquets (UDP), débit réel, ressources CPU/RAM locales.

## Objectifs

1. Définir des paliers de test configurables (débit cible, protocole, connexions, durée).
2. Appliquer la charge progressivement et surveiller les métriques.
3. Générer un rapport CSV + résumé console.
4. Support optionnel d'`iperf3` (si installé) ou générateur interne.
5. Mode `--dry-run` pour valider la configuration sans envoyer de trafic.

## Installation (environnement Python >=3.10)

```bash
pip install -e .
```

## Configuration

Créer un fichier YAML (ex: `config/example.yaml`):

```yaml
global:
  target_host: 192.168.1.10          # Hôte distant pour le trafic
  ping_host: 192.168.1.10            # Hôte à ping
  safety_max_mbps: 150               # Plafond total sécurité
  output_dir: reports
  use_iperf_if_available: true       # Essayer iperf3 si dispo

tiers:
  - name: palier1
    protocol: UDP                    # UDP ou TCP
    target_bandwidth_mbps: 10
    connections: 2
    duration_s: 20
    packet_size: 512                 # Octets (UDP) / chunk (TCP)
  - name: palier2
    protocol: UDP
    target_bandwidth_mbps: 30
    connections: 4
    duration_s: 30
    packet_size: 512
  - name: palier3
    protocol: TCP
    target_bandwidth_mbps: 50
    connections: 4
    duration_s: 40
    packet_size: 1024
```

## Utilisation

### Mode Interface Graphique (GUI) - NOUVEAU! 🎨

Lancer l'interface graphique interactive pour tester les niveaux progressifs:

```bash
loadtester-gui
```

L'interface vous permet de:
- Cliquer sur des boutons "Niveau 1" à "Niveau 10" pour tester progressivement
- Voir les résultats en temps réel avec indicateurs visuels (✅ succès, ⚠️ avertissement, ❌ problème)
- Recevoir des alertes quand le système commence à avoir des difficultés
- Visualiser un rapport complet de tous les tests effectués

### Mode Ligne de Commande (CLI)

```bash
loadtester --config config/example.yaml
```

Options principales:

```
--config <fichier>   Fichier YAML de configuration
--dry-run            Affiche ce qui serait exécuté
--output <dossier>   Surcharge du dossier de sortie
--internal-only      Ignore iperf3 même si présent
--log-level LEVEL    DEBUG, INFO, WARNING...
```

### Mode Stress Automatique (escalade jusqu'à échec)

Lance un test qui augmente progressivement le débit jusqu'à atteindre un critère d'arrêt (perte, latence, ratio de débit insuffisant):

```bash
loadtester-stress --host 192.168.1.10 --start-mbps 5 --step-mbps 10 --max-mbps 150 \
  --duration 15 --protocol BOTH --loss-threshold 10 --latency-threshold 200 --min-ratio 0.6
```

Paramètres clés:
- `--start-mbps` : Débit initial.
- `--step-mbps` : Incrément par palier.
- `--max-mbps` : Plafond absolu.
- `--duration` : Durée (s) de chaque palier.
- `--protocol` : UDP | TCP | BOTH.
- Seuils arrêt: `--loss-threshold`, `--latency-threshold`, `--min-ratio`.

Un rapport CSV est généré dans `reports/` (préfixe `stress_`).

### Récepteur (Receiver) pour mesurer réception réelle

Démarrer un récepteur UDP/TCP qui compte octets et détecte pertes (UDP avec numéros de séquence):

```bash
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv
```

Affiche toutes les `interval` secondes: paquets reçus, pertes estimées (si séquences manquantes), débit effectif.

### Avertissement Sécurité

Le mode stress et le générateur peuvent saturer un réseau local. N'utiliser que sur un environnement contrôlé (lab) et avec autorisation. Ne jamais utiliser sur un réseau tiers sans consentement.

## Rapport

Un fichier CSV est généré contenant: timestamp_start, tier_name, protocol, target_mbps, achieved_mbps, latency_ms_avg, jitter_ms, packet_loss_pct, cpu_pct_avg, mem_pct_avg.

## Limites / Prochaines étapes

- Générateur interne simple (améliorer la précision du contrôle de débit)
- Support iperf3 partiel (à étoffer mesure jitter/UDP via iperf JSON)
- Ajouter plus de tests unitaires

## Licence

MIT
