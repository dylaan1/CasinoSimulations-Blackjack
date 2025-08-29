diff --git a//dev/null b/blackjack/dealer.py
index 0000000000000000000000000000000000000000..ce3d7532796618daefc340e1ce2d53fc8094cf7a 100644
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
+            soft = value in hand.values[:-1]
+            if value < 17 or (value == 17 and soft and self.hit_soft_17):
+                hand.add_card(shoe.draw())
+                continue
+            break
+        return hand
