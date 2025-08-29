diff --git a//dev/null b/blackjack/hand.py
index 0000000000000000000000000000000000000000..9c4f196ee06779b9a451740661d826bc4868c4ce 100644
--- a//dev/null
+++ b/blackjack/hand.py
@@ -0,0 +1,42 @@
+from __future__ import annotations
+from dataclasses import dataclass, field
+from typing import List
+from .cards import Card
+
+@dataclass
+class Hand:
+    cards: List[Card] = field(default_factory=list)
+    bet: float = 0.0
+    is_split_aces: bool = False
+    is_split: bool = False
+
+    def add_card(self, card: Card) -> None:
+        self.cards.append(card)
+
+    @property
+    def values(self) -> List[int]:
+        total = sum(card.value for card in self.cards)
+        aces = sum(1 for card in self.cards if card.rank == "A")
+        values = [total]
+        while total > 21 and aces:
+            total -= 10
+            aces -= 1
+            values.append(total)
+        return values
+
+    @property
+    def best_value(self) -> int:
+        valid = [v for v in self.values if v <= 21]
+        return max(valid) if valid else min(self.values)
+
+    @property
+    def is_blackjack(self) -> bool:
+        return len(self.cards) == 2 and self.best_value == 21
+
+    @property
+    def is_bust(self) -> bool:
+        return min(self.values) > 21
+
+    @property
+    def can_split(self) -> bool:
+        return len(self.cards) == 2 and self.cards[0].rank == self.cards[1].rank
