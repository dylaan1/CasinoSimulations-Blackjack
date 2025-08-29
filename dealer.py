 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a//dev/null b/blackjack/dealer.py
index 0000000000000000000000000000000000000000..ba8cc20622c37d15e035321e717eb2b3289f22bb 100644
--- a//dev/null
+++ b/blackjack/dealer.py
@@ -0,0 +1,21 @@
+from __future__ import annotations
+from dataclasses import dataclass
+from .cards import Shoe
+from .hand import Hand
+
+@dataclass
+class Dealer:
+    hit_soft_17: bool = False
+
+    def play(self, shoe: Shoe) -> Hand:
+        hand = Hand()
+        hand.add_card(shoe.draw())
+        hand.add_card(shoe.draw())
+        while True:
+            value = hand.best_value
+            soft = len(hand.values) > 1 and value != min(hand.values)
+            if value < 17 or (value == 17 and soft and self.hit_soft_17):
+                hand.add_card(shoe.draw())
+                continue
+            break
+        return hand
 
EOF
)
