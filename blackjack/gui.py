import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd

try:  # pragma: no cover - fallback for direct execution
    from .settings import SimulationSettings
    from .simulator import Simulator
except ImportError:  # pragma: no cover
    from settings import SimulationSettings  # type: ignore
    from simulator import Simulator  # type: ignore


class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Simulator")
        self.sim = None

        # simulation setting variables
        self.bankroll = tk.DoubleVar(value=1000)
        self.trials = tk.IntVar(value=1)
        self.hands = tk.IntVar(value=6)
        self.bet = tk.DoubleVar(value=10)
        self.decks = tk.IntVar(value=6)
        self.payout = tk.StringVar(value="3:2")
        self.dealer = tk.StringVar(value="H17")
        self.das = tk.BooleanVar()
        self.rsa = tk.BooleanVar()
        self.surrender = tk.BooleanVar(value=True)
        self.strategy_file = tk.StringVar(value="BJ_basicStrategy.json")
        self.database = tk.StringVar(value="simulation.db")
        self.penetration = tk.DoubleVar(value=0.75)
        self.seed = tk.StringVar()

        self._build_widgets()

    def _build_widgets(self):
        fig = Figure(figsize=(6, 4))
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.table_frame = tk.Frame(self.root)
        self.table_frame.pack(fill=tk.BOTH, expand=True)
        self.table = ttk.Treeview(self.table_frame, show="headings")
        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        controls = tk.Frame(self.root)
        controls.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Button(controls, text="Run", command=self.run_simulation).pack(side=tk.LEFT)
        self.save_btn = tk.Button(controls, text="Save", command=self.save_results, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT)
        self.discard_btn = tk.Button(controls, text="Discard", command=self.discard_results, state=tk.DISABLED)
        self.discard_btn.pack(side=tk.LEFT)

        tk.Label(controls, text="Plot Trial").pack(side=tk.LEFT)
        self.plot_trial = tk.IntVar(value=1)
        self.plot_trial_spin = tk.Spinbox(
            controls,
            from_=1,
            to=1,
            textvariable=self.plot_trial,
            command=self.update_graph,
            width=5,
        )
        self.plot_trial_spin.pack(side=tk.LEFT)

        tk.Button(controls, text="Exit", command=self.exit_prompt).pack(side=tk.RIGHT)
        tk.Button(controls, text="Settings", command=self.open_settings).pack(side=tk.RIGHT)

    def open_settings(self):
        if hasattr(self, "settings_win") and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return
        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Settings")
        frame = tk.Frame(self.settings_win)
        frame.pack(padx=10, pady=10)

        tk.Label(frame, text="Bankroll").grid(row=0, column=0, sticky="e")
        tk.Entry(frame, textvariable=self.bankroll).grid(row=0, column=1)
        tk.Label(frame, text="Trials").grid(row=0, column=2, sticky="e")
        tk.Entry(frame, textvariable=self.trials).grid(row=0, column=3)

        tk.Label(frame, text="Hands").grid(row=1, column=0, sticky="e")

        tk.Label(frame, text="Hands/Trial").grid(row=1, column=0, sticky="e")

        tk.Spinbox(frame, from_=1, to=6, textvariable=self.hands, width=5).grid(row=1, column=1)
        tk.Label(frame, text="Bet").grid(row=1, column=2, sticky="e")
        tk.Spinbox(frame, from_=1, to=1000, textvariable=self.bet, width=5).grid(row=1, column=3)

        tk.Label(frame, text="Decks").grid(row=2, column=0, sticky="e")
        tk.Spinbox(frame, from_=1, to=12, textvariable=self.decks, width=5).grid(row=2, column=1)
        tk.Label(frame, text="Penetration").grid(row=2, column=2, sticky="e")
        tk.Spinbox(frame, from_=0.25, to=0.95, increment=0.01, textvariable=self.penetration, width=5).grid(row=2, column=3)

        tk.Label(frame, text="Payout").grid(row=3, column=0, sticky="e")
        ttk.Combobox(frame, textvariable=self.payout, values=["3:2", "6:5"], state="readonly").grid(row=3, column=1)
        tk.Label(frame, text="Dealer").grid(row=3, column=2, sticky="e")
        ttk.Combobox(frame, textvariable=self.dealer, values=["H17", "S17"], state="readonly").grid(row=3, column=3)

        tk.Checkbutton(frame, text="DAS", variable=self.das).grid(row=4, column=0)
        tk.Checkbutton(frame, text="RSA", variable=self.rsa).grid(row=4, column=1)
        tk.Checkbutton(frame, text="Surrender", variable=self.surrender).grid(row=4, column=2)

        tk.Label(frame, text="Strategy").grid(row=5, column=0, sticky="e")
        ttk.Entry(frame, textvariable=self.strategy_file).grid(row=5, column=1, columnspan=3, sticky="we")
        tk.Label(frame, text="Database").grid(row=6, column=0, sticky="e")
        ttk.Entry(frame, textvariable=self.database).grid(row=6, column=1, columnspan=3, sticky="we")

        tk.Label(frame, text="Seed").grid(row=7, column=0, sticky="e")
        ttk.Entry(frame, textvariable=self.seed).grid(row=7, column=1, columnspan=3, sticky="we")

        tk.Button(frame, text="Close", command=self.settings_win.destroy).grid(row=8, column=0, columnspan=4, pady=(10, 0))

    def run_simulation(self):
        if self.sim:
            self.sim.close()
        settings = SimulationSettings(
            trials=self.trials.get(),
            hands_per_game=self.hands.get(),
            bankroll=float(self.bankroll.get()),
            blackjack_payout=1.5 if self.payout.get() == "3:2" else 1.2,
            double_after_split=self.das.get(),
            resplit_aces=self.rsa.get(),
            allow_surrender=self.surrender.get(),
            bet_amount=float(self.bet.get()),
            num_decks=self.decks.get(),
            hit_soft_17=self.dealer.get() == "H17",
            penetration=float(self.penetration.get()),
            strategy_file=self.strategy_file.get(),
            database=self.database.get(),
            seed=int(self.seed.get()) if self.seed.get() else None,
        )
        self.sim = Simulator(settings)
        self.sim.run()
        self.plot_trial_spin.config(to=self.trials.get())
        self.plot_trial.set(1)
        self.update_graph()
        self.update_table()
        self.save_btn.config(state=tk.NORMAL)
        self.discard_btn.config(state=tk.NORMAL)

    def update_graph(self):
        if not self.sim:
            return
        trial = self.plot_trial.get()
        cur = self.sim.conn.cursor()
        cur.execute(
            "SELECT hand, bankroll FROM temp_bankroll WHERE trial=? ORDER BY hand",
            (trial,),
        )
        data = cur.fetchall()
        if not data:
            return
        hands, bankrolls = zip(*data)
        pl = [b - self.bankroll.get() for b in bankrolls]
        self.ax.clear()
        self.ax.set_xlabel("Total Hands Played")
        self.ax.set_ylabel("P/L")
        self.ax.set_xlim(0, max(hands))
        max_y = self.bankroll.get() * 20
        min_y = -self.bankroll.get()
        self.ax.set_ylim(min_y, max_y)
        self.ax.axhline(0, color="gray", linewidth=0.5)
        self.ax.plot(hands, pl)
        self.canvas.draw()

    def update_table(self):
        if not self.sim:
            return
        df = pd.read_sql_query("SELECT * FROM temp_results ORDER BY trial", self.sim.conn)
        self.table.delete(*self.table.get_children())
        if df.empty:
            return
        self.table["columns"] = list(df.columns)
        for col in df.columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=100, stretch=True)
        for _, row in df.iterrows():
            self.table.insert("", tk.END, values=list(row))

    def save_results(self):
        if self.sim:
            self.sim.save_results()
            self.sim.close()
            self.sim = None
            messagebox.showinfo("Saved", "Results saved")
            self.save_btn.config(state=tk.DISABLED)
            self.discard_btn.config(state=tk.DISABLED)
            self.update_table()

    def discard_results(self):
        if self.sim:
            self.sim.discard_results()
            self.sim.close()
            self.sim = None
            messagebox.showinfo("Discarded", "Results discarded")
            self.save_btn.config(state=tk.DISABLED)
            self.discard_btn.config(state=tk.DISABLED)
            self.update_table()

    def has_unsaved_data(self) -> bool:
        if not self.sim:
            return False
        cur = self.sim.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM temp_results")
        return cur.fetchone()[0] > 0

    def exit_prompt(self):
        if self.has_unsaved_data():
            win = tk.Toplevel(self.root)
            win.title("Exit")
            tk.Label(win, text="Save data to permanent tables before exiting?").pack(padx=10, pady=10)
            btn_frame = tk.Frame(win)
            btn_frame.pack(pady=5)
            tk.Button(btn_frame, text="Save", command=lambda: self._exit_and_save(win)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Don't Save", command=lambda: self._exit_without_save(win)).pack(side=tk.LEFT, padx=5)
        else:
            self._exit_without_save()

    def _exit_and_save(self, win=None):
        if win:
            win.destroy()
        if self.sim:
            self.save_results()
        self.root.destroy()

    def _exit_without_save(self, win=None):
        if win:
            win.destroy()
        if self.sim:
            self.sim.close()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
