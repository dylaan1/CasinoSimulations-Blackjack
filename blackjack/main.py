import argparse
from .settings import SimulationSettings
from .simulator import Simulator

def parse_args() -> SimulationSettings:
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
    parser.add_argument("--strategy", type=str, default="strategy.json")
    parser.add_argument("--database", type=str, default="simulation.db")
    args = parser.parse_args()
    return SimulationSettings(
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
    )

def main():
    settings = parse_args()
    sim = Simulator(settings)
    sim.run()

if __name__ == "__main__":
    main()
