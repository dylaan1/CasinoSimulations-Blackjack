from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple
import json

Action = str  # 'hit', 'stand', 'double', 'split', 'surrender'

@dataclass
class BasicStrategy:
    table: Dict[str, Action]

    @classmethod
    def from_json(cls, path: str) -> "BasicStrategy":
        with open(path, "r", encoding="utf-8") as fh:
            table = json.load(fh)
        return cls(table)

    def decide(self, player_cards: Tuple[str, str], dealer_up: str, options: Dict[str, bool]) -> Action:
        key = f"{player_cards[0]}{player_cards[1]}_{dealer_up}"
        return self.table.get(key, "stand")
