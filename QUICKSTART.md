# 🎯 QUICK START - Configuration Multi-PC

## Pour ce Mini PC (Récepteur) - 3 commandes

```powershell
# 1. Configurer (une seule fois)
.\setup_mini_pc.ps1

# 2. Démarrer le récepteur (à chaque session)
loadtester-receiver --udp-port 5202 --tcp-port 5201 --interval 5 --output receiver_log.csv

# 3. Noter votre IP et la donner à l'autre PC
ipconfig
```

## Pour l'Autre PC (Émetteur) - 2 commandes

```powershell
# 1. Configurer avec l'IP du Mini PC (une seule fois)
.\setup_pc_principal.ps1

# 2. Lancer les tests (interface graphique recommandée)
loadtester-gui
```

## 🔒 Sécurité Git

✅ **Tous les fichiers de config locale sont protégés** - Vous pouvez :
- Créer `config/mini_pc_local.yaml`
- Créer `config/pc_principal_local.yaml`
- Modifier ces fichiers avec vos IPs réelles
- Ils ne seront JAMAIS commitables

## 📚 Documentation Complète

| Fichier | Pour qui ? | Contenu |
|---------|-----------|---------|
| `SCRIPTS_README.md` | Les deux PC | Guide détaillé des scripts |
| `SETUP_MINI_PC.md` | Mini PC | Instructions complètes récepteur |
| `AI_CONTEXT.md` | IA autre PC | Contexte pour l'IA |
| `README.md` | Les deux PC | Documentation principale |

---

**C'est tout ! Les scripts font le reste automatiquement** 🚀
