from __future__ import annotations
import sqlite3
from dataclasses import asdict
from .settings import SimulationSettings
from .cards import Shoe
from .player import Player, PlayerSettings
from .dealer import Dealer
from .strategy import BasicStrategy

class Simulator:
    def __init__(self, settings: SimulationSettings):
        self.settings = settings
        self.conn = sqlite3.connect(self.settings.database)
        self._init_db()

    def _init_db(self) -> None:
        cur = self.conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS bankroll (trial INTEGER, hand INTEGER, bankroll REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS summary (trial INTEGER, hands_played INTEGER, bankroll REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS card_distribution (trial INTEGER, card TEXT, count INTEGER)")
        self.conn.commit()

    def run(self) -> None:
        strat = BasicStrategy.from_json(self.settings.strategy_file)
        for trial in range(1, self.settings.trials + 1):
            shoe = Shoe(self.settings.num_decks, penetration=self.settings.penetration)
            player_settings = PlayerSettings(bankroll=self.settings.bankroll,
                                            blackjack_payout=self.settings.blackjack_payout,
                                            double_after_split=self.settings.double_after_split,
                                            resplit_aces=self.settings.resplit_aces)
            player = Player(player_settings, strat)
            dealer = Dealer(hit_soft_17=self.settings.hit_soft_17)
            bankroll = player_settings.bankroll
            hands_played = 0
            cur = self.conn.cursor()
            while hands_played < self.settings.hands_per_game and bankroll > 0:
                dealer_hand = dealer.play(shoe)
                player_hands = player.play(shoe, dealer_hand.cards[0].rank)
                for hand in player_hands:
                    bankroll_change = self.resolve_hand(hand, dealer_hand, player_settings)
                    bankroll += bankroll_change
                hands_played += len(player_hands)
                cur.execute("INSERT INTO bankroll VALUES (?,?,?)", (trial, hands_played, bankroll))
            cur.execute("INSERT INTO summary VALUES (?,?,?)", (trial, hands_played, bankroll))
            for card, count in shoe.drawn_counts.items():
                cur.execute("INSERT INTO card_distribution VALUES (?,?,?)", (trial, card, count))
            self.conn.commit()
        self.conn.close()

    def resolve_hand(self, hand, dealer_hand, settings: PlayerSettings) -> float:
        if hand.bet == 0:
            return 0
        if hand.is_bust:
            return -hand.bet
        dealer_bust = dealer_hand.is_bust
        if hand.is_blackjack and not dealer_hand.is_blackjack:
            return hand.bet * settings.blackjack_payout
        if dealer_hand.is_blackjack and not hand.is_blackjack:
            return -hand.bet
        if dealer_bust:
            return hand.bet
        player_value = hand.best_value
        dealer_value = dealer_hand.best_value
        if player_value > dealer_value:
            return hand.bet
        if player_value < dealer_value:
            return -hand.bet
        return 0
