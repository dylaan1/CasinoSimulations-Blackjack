import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from .settings import SimulationSettings
from .simulator import Simulator


class SimulatorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Blackjack Simulator")
        self.sim = None
        self._build_widgets()

    def _build_widgets(self):
        fig = Figure(figsize=(6, 4))
        self.ax = fig.add_subplot(111)
        self.ax.set_xlabel("Hands Played")
        self.ax.set_ylabel("Bankroll")
        self.ax.set_ylim(0, 100)
        self.canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        controls = tk.Frame(self.root)
        controls.pack(side=tk.BOTTOM, fill=tk.X)

        tk.Label(controls, text="Bankroll").grid(row=0, column=0)
        self.bankroll = tk.IntVar(value=1000)
        tk.Spinbox(controls, from_=0, to=100000, increment=100, textvariable=self.bankroll).grid(row=0, column=1)

        tk.Label(controls, text="Trials").grid(row=0, column=2)
        self.trials = tk.IntVar(value=1)
        tk.Spinbox(controls, from_=1, to=1000, textvariable=self.trials).grid(row=0, column=3)

        tk.Label(controls, text="Hands/Trial").grid(row=0, column=4)
        self.hands = tk.IntVar(value=6)
        tk.Spinbox(controls, from_=1, to=6, textvariable=self.hands).grid(row=0, column=5)

        tk.Label(controls, text="Bet").grid(row=1, column=0)
        self.bet = tk.IntVar(value=10)
        tk.Spinbox(controls, from_=1, to=1000, textvariable=self.bet).grid(row=1, column=1)

        tk.Label(controls, text="Decks").grid(row=1, column=2)
        self.decks = tk.IntVar(value=6)
        tk.Spinbox(controls, from_=1, to=12, textvariable=self.decks).grid(row=1, column=3)

        tk.Label(controls, text="Payout").grid(row=1, column=4)
        self.payout = tk.StringVar(value="3:2")
        ttk.Combobox(controls, textvariable=self.payout, values=["3:2", "6:5"], state="readonly").grid(row=1, column=5)

        tk.Label(controls, text="Dealer").grid(row=2, column=0)
        self.dealer = tk.StringVar(value="H17")
        ttk.Combobox(controls, textvariable=self.dealer, values=["H17", "S17"], state="readonly").grid(row=2, column=1)

        self.das = tk.BooleanVar()
        tk.Checkbutton(controls, text="DAS", variable=self.das).grid(row=2, column=2)

        self.rsa = tk.BooleanVar()
        tk.Checkbutton(controls, text="RSA", variable=self.rsa).grid(row=2, column=3)

        tk.Button(controls, text="Run", command=self.run_simulation).grid(row=2, column=4)
        self.save_btn = tk.Button(controls, text="Save", command=self.save_results, state=tk.DISABLED)
        self.save_btn.grid(row=2, column=5)
        self.discard_btn = tk.Button(controls, text="Discard", command=self.discard_results, state=tk.DISABLED)
        self.discard_btn.grid(row=2, column=6)

    def run_simulation(self):
        settings = SimulationSettings(
            trials=self.trials.get(),
            hands_per_game=self.hands.get(),
            bankroll=float(self.bankroll.get()),
            blackjack_payout=1.5 if self.payout.get() == "3:2" else 1.2,
            double_after_split=self.das.get(),
            resplit_aces=self.rsa.get(),
            bet_amount=float(self.bet.get()),
            num_decks=self.decks.get(),
            hit_soft_17=self.dealer.get() == "H17",
            penetration=0.75,
            strategy_file="strategy.json",
            database="simulation.db",
        )
        self.sim = Simulator(settings)
        self.sim.run()
        self.update_graph()
        self.save_btn.config(state=tk.NORMAL)
        self.discard_btn.config(state=tk.NORMAL)

    def update_graph(self):
        cur = self.sim.conn.cursor()
        cur.execute("SELECT hand, bankroll FROM temp_bankroll ORDER BY hand")
        data = cur.fetchall()
        if not data:
            return
        hands, bankrolls = zip(*data)
        self.ax.clear()
        self.ax.set_xlabel("Hands Played")
        self.ax.set_ylabel("Bankroll")
        self.ax.set_xlim(0, max(hands))
        self.ax.set_ylim(0, max(bankrolls) * 1.1)
        self.ax.plot(hands, bankrolls)
        self.canvas.draw()

    def save_results(self):
        if self.sim:
            self.sim.save_results()
            messagebox.showinfo("Saved", "Results saved")
            self.save_btn.config(state=tk.DISABLED)
            self.discard_btn.config(state=tk.DISABLED)

    def discard_results(self):
        if self.sim:
            self.sim.discard_results()
            messagebox.showinfo("Discarded", "Results discarded")
            self.save_btn.config(state=tk.DISABLED)
            self.discard_btn.config(state=tk.DISABLED)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    gui = SimulatorGUI()
    gui.run()
