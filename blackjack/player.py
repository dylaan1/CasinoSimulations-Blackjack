from __future__ import annotations
from dataclasses import dataclass
from typing import List
from .hand import Hand
from .cards import Shoe
from .strategy import BasicStrategy

@dataclass
class PlayerSettings:
    bankroll: float
    blackjack_payout: float = 1.5
    double_after_split: bool = True
    resplit_aces: bool = False

@dataclass
class Player:
    settings: PlayerSettings
    strategy: BasicStrategy

    def play(self, shoe: Shoe, dealer_up: str) -> List[Hand]:
        initial = Hand(bet=1.0)
        initial.add_card(shoe.draw())
        initial.add_card(shoe.draw())
        hands = [initial]
        i = 0
        while i < len(hands):
            hand = hands[i]
            if self.settings.bankroll < hand.bet:
                break
            self._play_hand(hand, shoe, dealer_up, hands)
            i += 1
        return hands

    def _play_hand(self, hand: Hand, shoe: Shoe, dealer_up: str, hands: List[Hand]) -> None:
        # Surrender decision
        can_double = not hand.is_split or self.settings.double_after_split
        action = self.strategy.decide((hand.cards[0].rank, hand.cards[1].rank), dealer_up, {
            "can_double": can_double,
            "can_split": hand.can_split,
            "can_surrender": True,
        })
        if action == "surrender":
            hand.bet /= 2
            return
        while True:
            if hand.is_blackjack or hand.is_bust:
                return
            can_double = (len(hand.cards) == 2 and (not hand.is_split or self.settings.double_after_split))
            action = self.strategy.decide((hand.cards[0].rank, hand.cards[1].rank), dealer_up, {
                "can_double": can_double,
                "can_split": hand.can_split,
                "can_surrender": False,
            })
            if action == "stand":
                return
            if action == "double" and len(hand.cards) == 2 and self.settings.bankroll >= hand.bet:
                self.settings.bankroll -= hand.bet
                hand.bet *= 2
                hand.add_card(shoe.draw())
                return
            if action == "split" and hand.can_split:
                if hand.cards[0].rank == "A" and hand.is_split_aces and not self.settings.resplit_aces:
                    action = "hit"  # treat as hit
                else:
                    new_hand = Hand(cards=[hand.cards.pop()], bet=hand.bet, is_split_aces=(hand.cards[0].rank == "A"), is_split=True)
                    hand.add_card(shoe.draw())
                    new_hand.add_card(shoe.draw())
                    hands.append(new_hand)
                    continue
            hand.add_card(shoe.draw())
