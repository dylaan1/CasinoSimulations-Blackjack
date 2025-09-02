from dataclasses import dataclass
from pathlib import Path

DEFAULT_STRATEGY_FILE = Path(__file__).resolve().parent.parent / "BJ_basicStrategy.json"


@dataclass
class SimulationSettings:
    trials: int = 100
    hands_per_game: int = 100
    bankroll: float = 1000.0
    blackjack_payout: float = 1.5
    double_after_split: bool = True
    resplit_aces: bool = False
    allow_surrender: bool = True
    bet_amount: float = 1.0
    num_decks: int = 6
    hit_soft_17: bool = False
    penetration: float = 0.75
    strategy_file: str = str(DEFAULT_STRATEGY_FILE)
    database: str = "simulation.db"
    seed: int | None = None
