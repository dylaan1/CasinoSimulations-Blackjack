from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from .hand import Hand

Action = str  # 'hit', 'stand', 'double', 'split', 'surrender'


@dataclass
class BasicStrategy:
    """Implements a basic strategy matrix for blackjack.

    The rules are derived from the matrix provided in the project notes.  The
    decision engine works off the current hand state so that subsequent hits
    consider the new totals rather than only the first two cards.
    """

    @classmethod
    def from_json(cls, path: str) -> "BasicStrategy":  # pragma: no cover - kept for CLI compatibility
        return cls()

    def decide(self, hand: Hand, dealer_up: str, options: Dict[str, bool]) -> Action:
        """Return the recommended action for *hand* against *dealer_up*.

        Parameters in *options* indicate if doubling, splitting or surrendering
        are legal in the current context.
        """
        # Splits
        if options.get("can_split") and hand.can_split:
            r = hand.cards[0].rank
            if r in {"A", "8"}:
                return "split"
            split_rules = {
                "2": {"2", "3", "4", "5", "6"},
                "3": {"3", "4", "5", "6"},
                "4": {"5", "6"},
                "6": {"2", "3", "4", "5", "6"},
                "7": {"2", "3", "4", "5", "6", "7"},
                "9": {"2", "3", "4", "5", "6", "8", "9"},
            }
            if r in split_rules and dealer_up in split_rules[r]:
                return "split"

        total = hand.best_value
        soft = any(v <= 21 and v != total for v in hand.values)

        # Surrender
        if options.get("can_surrender") and not soft and len(hand.cards) == 2:
            if total == 15 and dealer_up == "10":
                return "surrender"
            if total == 16 and dealer_up in {"9", "10", "A"}:
                return "surrender"

        # Doubles (two-card hands only)
        if options.get("can_double") and len(hand.cards) == 2:
            if not soft:
                if total == 9 and dealer_up in {"3", "4", "5", "6"}:
                    return "double"
                if total == 10 and dealer_up in {"2", "3", "4", "5", "6", "7", "8", "9"}:
                    return "double"
                if total == 11:
                    return "double"
            else:
                if total == 13 and dealer_up in {"5", "6"}:
                    return "double"
                if total == 14 and dealer_up in {"5", "6"}:
                    return "double"
                if total == 15 and dealer_up in {"4", "5", "6"}:
                    return "double"
                if total == 16 and dealer_up in {"4", "5", "6"}:
                    return "double"
                if total == 17 and dealer_up in {"3", "4", "5", "6"}:
                    return "double"
                if total == 18 and dealer_up in {"2", "3", "4", "5", "6"}:
                    return "double"
                if total == 19 and dealer_up == "6":
                    return "double"

        # Stand / Hit logic
        if not soft:
            if total >= 17:
                return "stand"
            if total == 16 and dealer_up in {"2", "3", "4", "5", "6"}:
                return "stand"
            if total == 15 and dealer_up in {"2", "3", "4", "5", "6"}:
                return "stand"
            if total == 14 and dealer_up in {"2", "3", "4", "5", "6"}:
                return "stand"
            if total == 13 and dealer_up in {"2", "3", "4", "5", "6"}:
                return "stand"
            if total == 12 and dealer_up in {"4", "5", "6"}:
                return "stand"
            return "hit"
        else:
            if total >= 20:
                return "stand"
            if total == 19:
                if dealer_up == "6" and options.get("can_double") and len(hand.cards) == 2:
                    return "double"
                return "stand"
            if total == 18:
                if dealer_up in {"7", "8"}:
                    return "stand"
                if dealer_up in {"2", "3", "4", "5", "6"}:
                    return "stand"
                return "hit"
            if total == 17:
                return "hit"
            if total in {13, 14}:
                return "hit"
            if total in {15, 16}:
                return "hit"
            return "hit"

