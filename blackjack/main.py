import argparse
from pathlib import Path

from .settings import SimulationSettings, DEFAULT_STRATEGY_FILE
from .simulator import Simulator

def parse_args() -> tuple[SimulationSettings, bool]:
    parser = argparse.ArgumentParser(description="Blackjack simulator")
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--hands", type=int, default=100)
    parser.add_argument("--bankroll", type=float, default=1000.0)
    parser.add_argument("--payout", type=float, default=1.5)
    parser.add_argument("--das", action="store_true")
    parser.add_argument("--resplit-aces", action="store_true")
    parser.add_argument("--bet", type=float, default=1.0, help="Base wager per hand")
    parser.add_argument("--decks", type=int, default=6)
    parser.add_argument("--h17", action="store_true", help="Dealer hits on soft 17")
    parser.add_argument("--penetration", type=float, default=0.75)
    parser.add_argument("--strategy", type=str, default=str(DEFAULT_STRATEGY_FILE))
    parser.add_argument("--database", type=str, default="simulation.db")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--no-save", action="store_true", help="Do not save simulation results")
    args = parser.parse_args()
    if not Path(args.strategy).is_file():
        parser.error(f"Strategy file '{args.strategy}' not found.")
    settings = SimulationSettings(
        trials=args.trials,
        hands_per_game=args.hands,
        bankroll=args.bankroll,
        blackjack_payout=args.payout,
        double_after_split=args.das,
        resplit_aces=args.resplit_aces,
        bet_amount=args.bet,
        num_decks=args.decks,
        hit_soft_17=args.h17,
        penetration=args.penetration,
        strategy_file=args.strategy,
        database=args.database,
        seed=args.seed,
    )
    return settings, args.no_save


def run_cli():
    settings, no_save = parse_args()
    sim = Simulator(settings)
    sim.run()
    if not no_save:
        sim.save_results()
    sim.close()

if __name__ == "__main__":
    run_cli()

def main():
    settings, _ = parse_args()
    sim = Simulator(settings)
    sim.run()

if __name__ == "__main__":
    main()

