from __future__ import annotations
from dataclasses import dataclass
try:  # pragma: no cover - fallback for direct execution
    from .cards import Shoe
    from .hand import Hand
except ImportError:  # pragma: no cover
    from cards import Shoe  # type: ignore
    from hand import Hand  # type: ignore

@dataclass
class Dealer:
    hit_soft_17: bool = False

    def play(self, hand: Hand, shoe: Shoe) -> Hand:
        while True:
            value = hand.best_value
            soft = any(v <= 21 and v != value for v in hand.values)
            if value < 17 or (value == 17 and soft and self.hit_soft_17):
                hand.add_card(shoe.draw())
                continue
            break
        return hand
