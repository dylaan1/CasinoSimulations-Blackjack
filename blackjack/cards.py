from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import random

SUITS = ["hearts", "diamonds", "clubs", "spades"]
RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        if self.rank in ["J", "Q", "K"]:
            return 10
        if self.rank == "A":
            return 11
        return int(self.rank)

@dataclass
class Shoe:
    num_decks: int
    penetration: float = 0.75
    _cards: List[Card] = field(default_factory=list, init=False)
    _discard: List[Card] = field(default_factory=list, init=False)
    drawn_counts: dict = field(default_factory=lambda: {rank:0 for rank in RANKS}, init=False)

    def __post_init__(self) -> None:
        self.shuffle()

    def shuffle(self) -> None:
        self._cards = [Card(rank, suit) for rank in RANKS for suit in SUITS] * self.num_decks
        random.shuffle(self._cards)
        self._discard.clear()
        # Reset counts of drawn cards on shuffle
        self.drawn_counts = {rank: 0 for rank in RANKS}

    def draw(self) -> Card:
        """Draw a card from the shoe.

        If the shoe is empty, reshuffle the discard pile. If there are still
        no cards available after reshuffling (e.g., the shoe was initialized
        with zero decks), a descriptive exception is raised instead of the
        default ``IndexError``.
        """

        if not self._cards:
            # Try to reshuffle the shoe when out of cards.
            self.shuffle()
            if not self._cards:
                # After reshuffling there are still no cards available
                raise RuntimeError("Cannot draw from an empty shoe")

        card = self._cards.pop()
        self._discard.append(card)
        self.drawn_counts[card.rank] += 1
        return card

    @property
    def penetration_reached(self) -> bool:
        used = len(self._discard)
        total = self.num_decks * 52
        return used / total >= self.penetration
