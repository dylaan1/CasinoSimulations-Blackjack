 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 35192f5f18507d70aaab5595458b4f1db72675c8..707742f4f8b89e5618b5125c8963fab8d96c87bd 100644
--- a/README.md
+++ b/README.md
@@ -1 +1,27 @@
-# casinosim1
+# Blackjack Simulator
+
+This project provides a configurable blackjack simulator for collecting statistics on player survival and card distributions.
+
+## Features
+- Modular number of decks.
+- Dealer hits or stands on soft 17.
+- Penetration-based shoe with automatic shuffle.
+- Optional double after split and re-split aces.
+- Surrender allowed before any action.
+- Results stored in SQLite for post-processing.
+- R script to generate line graphs of bankroll and card distributions.
+
+## Usage
+Run simulations via the CLI:
+
+```bash
+python -m blackjack.main --trials 10 --hands 50 --bankroll 500 --payout 1.5 --decks 6 --penetration 0.75 --strategy strategy.json --database simulation.db
+```
+
+After running, create graphs with R:
+
+```bash
+Rscript analysis.R simulation.db
+```
+
+The simulator expects a JSON basic strategy file. The provided `strategy.json` is a placeholder that stands on all hands.
 
EOF
)
