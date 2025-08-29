import sys
import sqlite3
from collections import defaultdict

try:
    import matplotlib.pyplot as plt
except ImportError as exc:  # pragma: no cover - runtime environment may lack matplotlib
    raise SystemExit("matplotlib is required to run this script") from exc

def main(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Bankroll history
    bankroll_data = cur.execute("SELECT trial, hand, bankroll FROM bankroll").fetchall()
    trials = defaultdict(list)
    for trial, hand, bankroll in bankroll_data:
        trials[trial].append((hand, bankroll))

    plt.figure()
    for trial, points in trials.items():
        points.sort()
        hands, bankrolls = zip(*points)
        plt.plot(hands, bankrolls, label=f"Trial {trial}")
    plt.xlabel("Hand")
    plt.ylabel("Bankroll")
    plt.legend()
    plt.tight_layout()
    plt.savefig("bankroll.png")

    # Card distribution
    dist_data = cur.execute("SELECT trial, card, count FROM card_distribution").fetchall()
    cards = sorted({row[1] for row in dist_data})
    trial_groups = defaultdict(lambda: defaultdict(int))
    for trial, card, count in dist_data:
        trial_groups[trial][card] = count

    x = range(len(cards))
    width = 0.8 / max(1, len(trial_groups))
    plt.figure()
    for i, (trial, counts) in enumerate(sorted(trial_groups.items())):
        heights = [counts.get(card, 0) for card in cards]
        offset = (i - (len(trial_groups) - 1) / 2) * width
        positions = [xi + offset for xi in x]
        plt.bar(positions, heights, width=width, label=f"Trial {trial}")
    plt.xticks(list(x), cards)
    plt.xlabel("Card")
    plt.ylabel("Count")
    plt.legend()
    plt.tight_layout()
    plt.savefig("distribution.png")

    conn.close()

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "simulation.db"
    main(path)
