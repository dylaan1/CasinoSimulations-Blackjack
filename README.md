# Blackjack Simulator

This project provides a configurable blackjack simulator for collecting statistics on player survival and card distributions.

## Features
- Modular number of decks.
- Dealer hits or stands on soft 17.
- Penetration-based shoe with automatic shuffle.
- Optional double after split and re-split aces.
- Surrender allowed before any action.
- Results stored in SQLite for post-processing.
- Python script to generate line graphs of bankroll and card distributions.

## Usage
Run simulations via the CLI:

```bash
python -m blackjack.main --trials 10 --hands 50 --bankroll 500 --payout 1.5 --decks 6 --penetration 0.75 --strategy strategy.json --database simulation.db
```

After running, create graphs with Python:

```bash
python analysis.py simulation.db
```

The simulator accepts a JSON basic strategy file. The included `strategy.json` is an empty example retained for compatibility; the engine uses a built-in basic strategy when no custom file is provided.

