diff --git a//dev/null b/blackjack/settings.py
index 0000000000000000000000000000000000000000..710016b8ebca5877f4fb14cf4f4e570c326ac6f7 100644
--- a//dev/null
+++ b/blackjack/settings.py
@@ -0,0 +1,15 @@
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
+    num_decks: int = 6
+    hit_soft_17: bool = False
+    penetration: float = 0.75
+    strategy_file: str = "strategy.json"
+    database: str = "simulation.db"
