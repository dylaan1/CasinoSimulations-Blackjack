# Blackjack Simulator

A modular blackjack simulation engine for exploring different strategies and casino rules.

## Features

- **Modular architecture**
  - `cards` – card objects and a shoe that reshuffles on a configurable penetration.
  - `hand` – hand totals, soft/hard transitions, and split tracking.
  - `player` – bankroll bookkeeping and decision logic for hits, stands, doubles, splits, and surrender.
  - `dealer` – dealer behavior with optional hit-soft-17.
  - `strategy` – JSON-driven basic strategy matrix.
  - `simulator` – orchestrates games, records bankroll and card distributions, and writes results to SQLite.

- **Configurable rules via `SimulationSettings`**
  - Number of decks and shoe penetration.
  - Dealer hits or stands on soft 17.
  - Double after split toggle.
  - Resplitting aces limit.
  - Early surrender.
  - Blackjack payout ratio.
  - Per-hand bet amount and initial bankroll.

- **Strategy plug-ins**: point to any JSON basic strategy file; each defines `hard`, `soft`, and `pair` tables mapping player totals and dealer up-cards to actions.

- **Data output**: bankroll history, final summaries, and card distributions stored in SQLite for downstream analysis. A built-in Matplotlib plot visualizes bankroll progression for each trial.

- **Test mode**: run simulations without saving results to permanent tables to perform dry runs. Toggle via the GUI settings or the `--test-mode` CLI flag.

- **GUI**: a Tkinter interface lets you configure rules, run simulations, visualize bankroll progression for any trial via a "Plot Trial" selector, and optionally save or discard results stored in SQLite.

- **Quality checks**: unit tests cover soft-hand transitions, surrender payouts, split-ace restrictions, and bankroll updates after doubles/splits; GitHub Actions runs the test suite on each push or pull request.

## Usage

```bash
python -m blackjack
```

After installing with `pip install .`, a `blackjack-sim` application launcher is
registered. You can create a desktop shortcut to this script so that the GUI
opens like any other native app.

```bash
pip install .
blackjack-sim  # runs without a console window

```

For a dry run that leaves results only in the temporary tables, pass
`--test-mode` to the CLI:

```bash
python -m blackjack --test-mode
```


In the GUI, open **Settings** and check **Test Mode**. A red banner at the top of the window indicates when test mode is active.


### Visualization

The GUI uses Matplotlib to render a local line graph of profit/loss over the number of hands played. Results can also be queried directly from the SQLite database for custom analysis.

The simulator expects `BJ_basicStrategy.json` to contain three top-level objects: `hard`, `soft`, and `pair`. Each maps player totals (or pair ranks) and dealer up-cards to recommended actions (`hit`, `stand`, `double`, `split`, `surrender`).

## Testing

```bash
pytest
```

GitHub Actions automatically executes the same tests on every push and pull request.
