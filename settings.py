 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/blackjack/settings.py
index 0000000000000000000000000000000000000000..48dc6723d570a6291ff2f6e07efc541de821978d 100644
--- a//dev/null
+++ b/blackjack/settings.py
@@ -0,0 +1,16 @@
+from dataclasses import dataclass
+
+@dataclass
+class SimulationSettings:
+    trials: int = 100
+    hands_per_game: int = 100
+    bankroll: float = 1000.0
+    blackjack_payout: float = 1.5
+    double_after_split: bool = True
+    resplit_aces: bool = False
+    bet_amount: float = 1.0
+    num_decks: int = 6
+    hit_soft_17: bool = False
+    penetration: float = 0.75
+    strategy_file: str = "strategy.json"
+    database: str = "simulation.db"
 
EOF
)
