"""Interface graphique Tkinter pour tester progressivement les niveaux de charge."""

from __future__ import annotations

import asyncio
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import FullConfig, GlobalConfig, TierConfig
from .runner import LoadTestRunner
from .report import TierReportRow


@dataclass
class LevelDefinition:
    """Définition d'un niveau de test."""
    level: int
    name: str
    protocol: str
    target_mbps: float
    connections: int
    duration_s: int
    packet_size: int


# Niveaux prédéfinis progressifs
PREDEFINED_LEVELS = [
    LevelDefinition(1, "Niveau 1 - Léger", "UDP", 5, 1, 10, 512),
    LevelDefinition(2, "Niveau 2 - Faible", "UDP", 10, 2, 15, 512),
    LevelDefinition(3, "Niveau 3 - Modéré", "TCP", 20, 2, 15, 1024),
    LevelDefinition(4, "Niveau 4 - Moyen", "UDP", 30, 3, 20, 1024),
    LevelDefinition(5, "Niveau 5 - Élevé", "TCP", 40, 4, 20, 1024),
    LevelDefinition(6, "Niveau 6 - Intense", "UDP", 50, 5, 25, 1024),
    LevelDefinition(7, "Niveau 7 - Très Intense", "TCP", 60, 6, 25, 1024),
    LevelDefinition(8, "Niveau 8 - Extrême", "UDP", 80, 8, 30, 1024),
    LevelDefinition(9, "Niveau 9 - Critique", "TCP", 100, 10, 30, 1024),
    LevelDefinition(10, "Niveau 10 - Maximum", "UDP", 120, 12, 30, 1024),
]


class LoadTesterGUI:
    """Interface graphique principale."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("WiFi Load Tester - Test Progressif AMR")
        self.root.geometry("900x700")
        
        # Configuration par défaut
        self.target_host = tk.StringVar(value="192.168.1.10")
        self.safety_max = tk.StringVar(value="150")
        self.current_level = 0
        self.test_running = False
        self.last_result: Optional[TierReportRow] = None
        self.results_history: list[TierReportRow] = []
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configure l'interface utilisateur."""
        # Frame configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=10)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(config_frame, text="Hôte cible:").grid(row=0, column=0, sticky="w", padx=5)
        ttk.Entry(config_frame, textvariable=self.target_host, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(config_frame, text="Limite sécurité (Mbps):").grid(row=0, column=2, sticky="w", padx=5)
        ttk.Entry(config_frame, textvariable=self.safety_max, width=10).grid(row=0, column=3, padx=5)
        
        # Frame des niveaux
        levels_frame = ttk.LabelFrame(self.root, text="Niveaux de Test", padding=10)
        levels_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Créer grille de boutons (2 colonnes)
        self.level_buttons = []
        for i, level_def in enumerate(PREDEFINED_LEVELS):
            row = i // 2
            col = i % 2
            
            btn_frame = ttk.Frame(levels_frame)
            btn_frame.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            
            btn = ttk.Button(
                btn_frame,
                text=f"🚀 {level_def.name}",
                command=lambda lv=level_def: self._run_level(lv),
                width=35
            )
            btn.pack(side="left", fill="x", expand=True)
            
            # Label pour status
            status_label = ttk.Label(btn_frame, text="⚪", font=("Arial", 12))
            status_label.pack(side="left", padx=5)
            
            self.level_buttons.append((btn, status_label))
        
        # Configurer expansion des colonnes
        levels_frame.columnconfigure(0, weight=1)
        levels_frame.columnconfigure(1, weight=1)
        
        # Frame résultats en temps réel
        results_frame = ttk.LabelFrame(self.root, text="Résultats du dernier test", padding=10)
        results_frame.pack(fill="x", padx=10, pady=5)
        
        self.results_text = tk.Text(results_frame, height=8, wrap="word", font=("Consolas", 9))
        self.results_text.pack(fill="both", expand=True)
        self.results_text.insert("1.0", "Aucun test lancé.\n")
        self.results_text.config(state="disabled")
        
        # Frame boutons d'action
        action_frame = ttk.Frame(self.root, padding=5)
        action_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(action_frame, text="📊 Voir rapport complet", command=self._show_full_report).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🔥 Mode Stress", command=self._open_stress_dialog).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🔄 Réinitialiser", command=self._reset).pack(side="left", padx=5)
        ttk.Button(action_frame, text="❌ Quitter", command=self.root.quit).pack(side="right", padx=5)
        
        # Barre de statut
        self.status_var = tk.StringVar(value="Prêt - Cliquez sur un niveau pour commencer")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
    
    def _run_level(self, level_def: LevelDefinition):
        """Lance le test pour un niveau donné."""
        if self.test_running:
            messagebox.showwarning("Test en cours", "Un test est déjà en cours d'exécution.")
            return
        
        # Vérifier limite de sécurité
        try:
            safety_limit = float(self.safety_max.get())
            if level_def.target_mbps > safety_limit:
                if not messagebox.askyesno(
                    "Dépassement limite",
                    f"Ce niveau ({level_def.target_mbps} Mbps) dépasse la limite de sécurité ({safety_limit} Mbps).\n\nContinuer quand même?"
                ):
                    return
        except ValueError:
            messagebox.showerror("Erreur", "Limite de sécurité invalide.")
            return
        
        self.test_running = True
        self.current_level = level_def.level
        self._update_button_status(level_def.level - 1, "running")
        self.status_var.set(f"⏳ Test en cours: {level_def.name}...")
        
        # Lancer le test dans un thread séparé
        thread = threading.Thread(target=self._run_test_thread, args=(level_def,), daemon=True)
        thread.start()
    
    def _run_test_thread(self, level_def: LevelDefinition):
        """Exécute le test dans un thread séparé."""
        try:
            # Créer config temporaire
            global_cfg = GlobalConfig(
                target_host=self.target_host.get(),
                ping_host=self.target_host.get(),
                safety_max_mbps=float(self.safety_max.get()),
                output_dir="reports",
                use_iperf_if_available=True,
            )
            
            tier = TierConfig(
                name=level_def.name,
                protocol=level_def.protocol,
                target_bandwidth_mbps=level_def.target_mbps,
                connections=level_def.connections,
                duration_s=level_def.duration_s,
                packet_size=level_def.packet_size,
            )
            
            full_cfg = FullConfig(global_cfg, [tier])
            runner = LoadTestRunner(full_cfg, dry_run=False, internal_only=False)
            
            # Exécuter dans event loop asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            reporter = loop.run_until_complete(runner.run())
            loop.close()
            
            # Récupérer le résultat
            if reporter.rows:
                result = reporter.rows[0]
                self.last_result = result
                self.results_history.append(result)
                
                # Mettre à jour l'UI depuis le thread principal
                self.root.after(0, lambda: self._display_result(level_def, result))
            else:
                self.root.after(0, lambda: self._display_error(level_def, "Aucun résultat retourné"))
        
        except Exception as e:
            self.root.after(0, lambda: self._display_error(level_def, str(e)))
        
        finally:
            self.test_running = False
    
    def _display_result(self, level_def: LevelDefinition, result: TierReportRow):
        """Affiche les résultats dans l'interface."""
        # Déterminer le statut (succès/warning/échec)
        status = self._analyze_result(result)
        
        self._update_button_status(level_def.level - 1, status)
        
        # Mise à jour texte résultats
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        
        report_lines = [
            f"{'='*70}",
            f"  {level_def.name} - Résultats",
            f"{'='*70}",
            f"",
            f"⚙️  Configuration:",
            f"   • Protocole: {result.protocol}",
            f"   • Débit cible: {result.target_mbps:.1f} Mbps",
            f"   • Débit atteint: {result.achieved_mbps:.1f} Mbps ({result.achieved_mbps/result.target_mbps*100:.0f}%)",
            f"",
            f"📊 Métriques réseau:",
            f"   • Latence moyenne: {result.latency_ms_avg:.2f} ms",
            f"   • Gigue (jitter): {result.jitter_ms:.2f} ms",
            f"   • Perte de paquets: {result.packet_loss_pct:.1f}%",
            f"",
            f"💻 Ressources système:",
            f"   • CPU: {result.cpu_pct_avg:.1f}%",
            f"   • RAM: {result.mem_pct_avg:.1f}%",
            f"",
        ]
        
        # Ajout d'alertes si problèmes détectés
        warnings = []
        if result.packet_loss_pct > 5:
            warnings.append(f"⚠️  ATTENTION: Perte de paquets élevée ({result.packet_loss_pct:.1f}%)")
        if result.latency_ms_avg > 100:
            warnings.append(f"⚠️  ATTENTION: Latence élevée ({result.latency_ms_avg:.0f} ms)")
        if result.achieved_mbps < result.target_mbps * 0.7:
            warnings.append(f"⚠️  ATTENTION: Débit insuffisant (seulement {result.achieved_mbps/result.target_mbps*100:.0f}% de la cible)")
        if result.jitter_ms > 30:
            warnings.append(f"⚠️  ATTENTION: Gigue importante ({result.jitter_ms:.1f} ms)")
        
        if warnings:
            report_lines.append("🚨 ALERTES:")
            for w in warnings:
                report_lines.append(f"   {w}")
            report_lines.append("")
        else:
            report_lines.append("✅ Aucun problème détecté - Réseau stable")
        
        self.results_text.insert("1.0", "\n".join(report_lines))
        self.results_text.config(state="disabled")
        
        # Mise à jour statut
        if status == "error":
            self.status_var.set(f"❌ {level_def.name} - Système en difficulté!")
            messagebox.showwarning(
                "Difficultés détectées",
                f"Le niveau {level_def.level} montre des difficultés significatives!\n\n" +
                "\n".join(warnings)
            )
        elif status == "warning":
            self.status_var.set(f"⚠️  {level_def.name} - Problèmes détectés")
        else:
            self.status_var.set(f"✅ {level_def.name} - Complété avec succès")
    
    def _display_error(self, level_def: LevelDefinition, error: str):
        """Affiche une erreur."""
        self._update_button_status(level_def.level - 1, "error")
        self.status_var.set(f"❌ Erreur lors du test {level_def.name}")
        
        self.results_text.config(state="normal")
        self.results_text.delete("1.0", "end")
        self.results_text.insert("1.0", f"❌ ERREUR:\n\n{error}")
        self.results_text.config(state="disabled")
        
        messagebox.showerror("Erreur", f"Erreur lors du test:\n{error}")

    # ------------------ Stress Mode ------------------
    def _open_stress_dialog(self):
        if self.test_running:
            messagebox.showwarning("Occupé", "Attendez la fin du test courant.")
            return
        win = tk.Toplevel(self.root)
        win.title("Mode Stress - Paramètres")
        vars_ = {
            'start': tk.StringVar(value='5'),
            'step': tk.StringVar(value='10'),
            'maxv': tk.StringVar(value='150'),
            'duration': tk.StringVar(value='15'),
            'protocol': tk.StringVar(value='BOTH'),
            'connections': tk.StringVar(value='4'),
        }
        labels = [
            ("Débit initial (Mbps)", 'start'),
            ("Incrément (Mbps)", 'step'),
            ("Débit max (Mbps)", 'maxv'),
            ("Durée palier (s)", 'duration'),
            ("Protocol (UDP/TCP/BOTH)", 'protocol'),
            ("Connexions", 'connections'),
        ]
        for i,(lab,key) in enumerate(labels):
            ttk.Label(win, text=lab).grid(row=i, column=0, sticky='w', padx=5, pady=2)
            ttk.Entry(win, textvariable=vars_[key], width=12).grid(row=i, column=1, padx=5, pady=2)
        ttk.Button(win, text="Démarrer", command=lambda: (win.destroy(), self._start_stress(vars_))).grid(row=len(labels), column=0, columnspan=2, pady=10)

    def _start_stress(self, vars_):
        try:
            start = float(vars_['start'].get())
            step = float(vars_['step'].get())
            maxv = float(vars_['maxv'].get())
            duration = int(vars_['duration'].get())
            protocol = vars_['protocol'].get().upper()
            connections = int(vars_['connections'].get())
        except ValueError:
            messagebox.showerror("Erreur", "Paramètres invalides")
            return
        self.status_var.set("⏳ Stress en cours...")
        self.test_running = True
        thread = threading.Thread(target=self._run_stress_thread, args=(start, step, maxv, duration, protocol, connections), daemon=True)
        thread.start()

    def _run_stress_thread(self, start, step, maxv, duration, protocol, connections):
        from .stress import parse_args as stress_parse_args, stress, write_report
        import types, logging
        # Construire un objet args minimal
        args = types.SimpleNamespace(
            host=self.target_host.get(),
            ping_host=self.target_host.get(),
            start_mbps=start,
            step_mbps=step,
            max_mbps=maxv,
            duration=duration,
            protocol=protocol,
            connections=connections,
            packet_size=1024,
            loss_threshold=10.0,
            latency_threshold=200.0,
            min_ratio=0.6,
            output_dir='reports',
            no_iperf=True,
        )
        logging.getLogger().setLevel(logging.INFO)
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(stress(args))
            path = write_report(results, args.output_dir)
            loop.close()
            # Synthèse
            summary = [f"Stress test terminé. Rapport: {path}"]
            for r in results:
                summary.append(f"Lvl{r.level} {r.protocol} target={r.target_mbps} achieved={r.achieved_mbps:.1f} latency={r.latency_ms:.1f} loss={r.loss_pct:.1f}% status={r.status}")
            text = "\n".join(summary)
            self.root.after(0, lambda: self._stress_done(text))
        except Exception as e:
            self.root.after(0, lambda: self._stress_done(f"Erreur stress: {e}"))
        finally:
            self.test_running = False

    def _stress_done(self, text: str):
        self.results_text.config(state='normal')
        self.results_text.delete('1.0', 'end')
        self.results_text.insert('1.0', text + "\n")
        self.results_text.config(state='disabled')
        self.status_var.set("✅ Stress terminé")
    
    def _analyze_result(self, result: TierReportRow) -> str:
        """Analyse le résultat et retourne le statut (success/warning/error)."""
        # Critères d'échec critique
        if (result.packet_loss_pct > 10 or 
            result.latency_ms_avg > 200 or 
            result.achieved_mbps < result.target_mbps * 0.5):
            return "error"
        
        # Critères d'avertissement
        if (result.packet_loss_pct > 3 or 
            result.latency_ms_avg > 80 or 
            result.jitter_ms > 30 or
            result.achieved_mbps < result.target_mbps * 0.8):
            return "warning"
        
        return "success"
    
    def _update_button_status(self, index: int, status: str):
        """Met à jour le statut visuel d'un bouton."""
        if 0 <= index < len(self.level_buttons):
            _, status_label = self.level_buttons[index]
            if status == "running":
                status_label.config(text="⏳", foreground="blue")
            elif status == "success":
                status_label.config(text="✅", foreground="green")
            elif status == "warning":
                status_label.config(text="⚠️", foreground="orange")
            elif status == "error":
                status_label.config(text="❌", foreground="red")
    
    def _show_full_report(self):
        """Affiche un rapport complet de tous les tests."""
        if not self.results_history:
            messagebox.showinfo("Rapport", "Aucun test effectué pour le moment.")
            return
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Rapport Complet")
        report_window.geometry("800x600")
        
        text = tk.Text(report_window, wrap="word", font=("Consolas", 9))
        scrollbar = ttk.Scrollbar(report_window, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        text.pack(fill="both", expand=True)
        
        # Générer rapport
        lines = [
            "="*80,
            " RAPPORT COMPLET DES TESTS",
            "="*80,
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Nombre de tests: {len(self.results_history)}",
            "",
        ]
        
        for i, result in enumerate(self.results_history, 1):
            lines.extend([
                f"\n{'='*80}",
                f"Test #{i}: {result.tier_name}",
                f"{'='*80}",
                f"Protocole: {result.protocol}",
                f"Cible: {result.target_mbps:.1f} Mbps | Atteint: {result.achieved_mbps:.1f} Mbps",
                f"Latence: {result.latency_ms_avg:.2f} ms | Gigue: {result.jitter_ms:.2f} ms",
                f"Perte: {result.packet_loss_pct:.1f}% | CPU: {result.cpu_pct_avg:.1f}% | RAM: {result.mem_pct_avg:.1f}%",
            ])
        
        text.insert("1.0", "\n".join(lines))
        text.config(state="disabled")
    
    def _reset(self):
        """Réinitialise l'interface."""
        if messagebox.askyesno("Réinitialiser", "Voulez-vous effacer tous les résultats?"):
            self.results_history.clear()
            self.last_result = None
            self.current_level = 0
            
            for _, status_label in self.level_buttons:
                status_label.config(text="⚪", foreground="black")
            
            self.results_text.config(state="normal")
            self.results_text.delete("1.0", "end")
            self.results_text.insert("1.0", "Résultats réinitialisés.\n")
            self.results_text.config(state="disabled")
            
            self.status_var.set("Prêt - Cliquez sur un niveau pour commencer")


def main():
    """Point d'entrée de l'interface graphique."""
    root = tk.Tk()
    app = LoadTesterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
