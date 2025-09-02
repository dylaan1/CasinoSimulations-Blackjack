from __future__ import annotations
import sqlite3
import random
from dataclasses import asdict
from typing import List

from .settings import SimulationSettings
from .cards import Shoe, Card
from .player import Player, PlayerSettings
from .dealer import Dealer
from .strategy import BasicStrategy
from .hand import Hand


class Simulator:
    def __init__(self, settings: SimulationSettings):
        self.settings = settings
        self.conn = sqlite3.connect(self.settings.database)
        self._init_db()
        cur = self.conn.cursor()
        cur.execute("SELECT COALESCE(MAX(sim), 0) FROM results")
        self.sim_number = cur.fetchone()[0] + 1

    def _init_db(self) -> None:
        cur = self.conn.cursor()

        cur.execute(
            "CREATE TABLE IF NOT EXISTS bankroll (trial INTEGER, hand INTEGER, bankroll REAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS summary (trial INTEGER, hands_played INTEGER, bankroll REAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS card_distribution (trial INTEGER, card TEXT, count INTEGER)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS temp_bankroll (trial INTEGER, hand INTEGER, bankroll REAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS temp_summary (trial INTEGER, hands_played INTEGER, bankroll REAL)"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS temp_card_distribution (trial INTEGER, card TEXT, count INTEGER)"
        )

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                sim INTEGER,
                trial INTEGER,
                decks INTEGER,
                penetration REAL,
                payout TEXT,
                soft17 TEXT,
                das INTEGER,
                rsa INTEGER,
                surrender INTEGER,
                hands INTEGER,
                wager REAL,
                open_bankroll REAL,
                close_bankroll REAL,
                cards TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS temp_results (
                sim INTEGER,
                trial INTEGER,
                decks INTEGER,
                penetration REAL,
                payout TEXT,
                soft17 TEXT,
                das INTEGER,
                rsa INTEGER,
                surrender INTEGER,
                hands INTEGER,
                wager REAL,
                open_bankroll REAL,
                close_bankroll REAL,
                cards TEXT
            )
            """
        )

        cur.execute("CREATE TABLE IF NOT EXISTS bankroll (trial INTEGER, hand INTEGER, bankroll REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS summary (trial INTEGER, hands_played INTEGER, bankroll REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS card_distribution (trial INTEGER, card TEXT, count INTEGER)")

        self.conn.commit()

    def _format_round(
        self, initial_cards: List[Card], player_hands: List[Hand], dealer_hand: Hand
    ) -> str:
        player_repr: str
        if len(player_hands) == 1:
            hand_obj = player_hands[0]
            base = ''.join(c.rank for c in initial_cards)
            if hand_obj.surrendered:
                player_repr = f"{base}|x"
            else:
                extra = ''
                if len(hand_obj.cards) > 2:
                    extra_cards = hand_obj.cards[2:]
                    is_double = hand_obj.bet > self.settings.bet_amount
                    if is_double:
                        extra += 'd' + extra_cards[0].rank
                    else:
                        extra += ''.join(c.rank for c in extra_cards)
                player_repr = base + '|' + extra
                player_repr += '_' if hand_obj.is_bust else 's'
        else:
            base = ''.join(c.rank for c in initial_cards)
            parts = []
            for h in player_hands:
                seg_cards = h.cards[1:]
                if h.bet > self.settings.bet_amount and len(seg_cards) >= 2:
                    seg = 'v' + seg_cards[0].rank + 'd' + seg_cards[1].rank
                else:
                    seg = 'v' + ''.join(c.rank for c in seg_cards)
                seg += '_' if h.is_bust else 's'
                parts.append(seg)
            player_repr = base + '|' + '_'.join(parts)

        dealer_base = dealer_hand.cards[0].rank
        extra = ''.join(c.rank for c in dealer_hand.cards[1:])
        dealer_repr = dealer_base + '|' + extra
        dealer_repr += '_' if dealer_hand.is_bust else 's'
        return f"Player Hand: {player_repr}, Dealer Hand: {dealer_repr}"

    def run(self) -> None:
        if self.settings.seed is not None:
            random.seed(self.settings.seed)
        strat = BasicStrategy.from_json(
            self.settings.strategy_file, allow_surrender=self.settings.allow_surrender
        )
        for trial in range(1, self.settings.trials + 1):
            shoe = Shoe(self.settings.num_decks, penetration=self.settings.penetration)
            player_settings = PlayerSettings(
                bankroll=self.settings.bankroll,
                blackjack_payout=self.settings.blackjack_payout,
                double_after_split=self.settings.double_after_split,
                resplit_aces=self.settings.resplit_aces,
                allow_surrender=self.settings.allow_surrender,
                bet_amount=self.settings.bet_amount,
            )
            player = Player(player_settings, strat)
            dealer = Dealer(hit_soft_17=self.settings.hit_soft_17)
            hands_played = 0
            cur = self.conn.cursor()
            while (
                hands_played < self.settings.hands_per_game
                and player_settings.bankroll >= player_settings.bet_amount
            ):
                if shoe.penetration_reached:
                    shoe.shuffle()
                bankroll_before = player_settings.bankroll
                player_settings.bankroll -= player_settings.bet_amount
                player_hand = Hand(bet=player_settings.bet_amount)
                dealer_hand = Hand()
                player_hand.add_card(shoe.draw())
                dealer_hand.add_card(shoe.draw())
                player_hand.add_card(shoe.draw())
                dealer_hand.add_card(shoe.draw())

                initial_cards = list(player_hand.cards)
                player_hands = player.play(shoe, dealer_hand.cards[0].rank, player_hand)
                if any(not h.is_bust and not h.surrendered for h in player_hands):
                    dealer.play(dealer_hand, shoe)
                for h in player_hands:
                    change = self.resolve_hand(h, dealer_hand, player_settings)
                    player_settings.bankroll += change
                hands_played += len(player_hands)

                cur.execute(
                    "INSERT INTO temp_bankroll VALUES (?,?,?)",
                    (trial, hands_played, player_settings.bankroll),
                )

                layout = self._format_round(initial_cards, player_hands, dealer_hand)
                cur.execute(
                    "INSERT INTO temp_results VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (
                        self.sim_number,
                        trial,
                        self.settings.num_decks,
                        self.settings.penetration,
                        "3:2" if self.settings.blackjack_payout == 1.5 else "6:5",
                        "H17" if self.settings.hit_soft_17 else "S17",
                        int(self.settings.double_after_split),
                        int(self.settings.resplit_aces),
                        int(self.settings.allow_surrender),
                        len(player_hands),
                        self.settings.bet_amount,
                        bankroll_before,
                        player_settings.bankroll,
                        layout,
                    ),
                )
            cur.execute(
                "INSERT INTO temp_summary VALUES (?,?,?)",
                (trial, hands_played, player_settings.bankroll),
            )
            for card, count in shoe.drawn_counts.items():
                cur.execute(
                    "INSERT INTO temp_card_distribution VALUES (?,?,?)",
                    (trial, card, count),
                )
            self.conn.commit()

    def save_results(self) -> None:
        """Persist temporary tables into permanent storage."""
        cur = self.conn.cursor()
        cur.execute("INSERT INTO bankroll SELECT * FROM temp_bankroll")
        cur.execute("INSERT INTO summary SELECT * FROM temp_summary")
        cur.execute("INSERT INTO card_distribution SELECT * FROM temp_card_distribution")
        cur.execute("INSERT INTO results SELECT * FROM temp_results")
        cur.execute("DELETE FROM temp_bankroll")
        cur.execute("DELETE FROM temp_summary")
        cur.execute("DELETE FROM temp_card_distribution")
        cur.execute("DELETE FROM temp_results")
        self.conn.commit()

    def discard_results(self) -> None:
        """Remove any data from the temporary tables."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM temp_bankroll")
        cur.execute("DELETE FROM temp_summary")
        cur.execute("DELETE FROM temp_card_distribution")
        cur.execute("DELETE FROM temp_results")
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    def resolve_hand(self, hand, dealer_hand, settings: PlayerSettings) -> float:
        if hand.surrendered:
            return hand.bet  # half wager already deducted
        if hand.is_bust:
            return 0
        dealer_bust = dealer_hand.is_bust
        if hand.is_blackjack and not dealer_hand.is_blackjack:
            return hand.bet * (1 + settings.blackjack_payout)
        if dealer_hand.is_blackjack and not hand.is_blackjack:
            return 0
        if dealer_bust:
            return hand.bet * 2
        player_value = hand.best_value
        dealer_value = dealer_hand.best_value
        if player_value > dealer_value:
            return hand.bet * 2
        if player_value < dealer_value:
            return 0
        return hand.bet
