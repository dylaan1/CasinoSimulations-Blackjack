 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/blackjack/dealer.py
index 0000000000000000000000000000000000000000..2c734055c4597eef825911021c6aa847bed10d81 100644
--- a//dev/null
+++ b/blackjack/dealer.py
@@ -0,0 +1,18 @@
+from __future__ import annotations
+from dataclasses import dataclass
+from .cards import Shoe
+from .hand import Hand
+
+@dataclass
+class Dealer:
+    hit_soft_17: bool = False
+
+    def play(self, hand: Hand, shoe: Shoe) -> Hand:
+        while True:
+            value = hand.best_value
+            soft = any(v <= 21 and v != value for v in hand.values)
+            if value < 17 or (value == 17 and soft and self.hit_soft_17):
+                hand.add_card(shoe.draw())
+                continue
+            break
+        return hand
 
EOF
)
