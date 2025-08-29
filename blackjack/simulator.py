from __future__ import annotations
import sqlite3
from dataclasses import asdict
from .settings import SimulationSettings
from .cards import Shoe
from .player import Player, PlayerSettings
from .dealer import Dealer
from .strategy import BasicStrategy
from .hand import Hand

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
                                            resplit_aces=self.settings.resplit_aces,
                                            bet_amount=self.settings.bet_amount)
            player = Player(player_settings, strat)
            dealer = Dealer(hit_soft_17=self.settings.hit_soft_17)
            hands_played = 0
            cur = self.conn.cursor()
            while (hands_played < self.settings.hands_per_game and
                   player_settings.bankroll >= player_settings.bet_amount):
                if shoe.penetration_reached:
                    shoe.shuffle()
                player_settings.bankroll -= player_settings.bet_amount
                player_hand = Hand(bet=player_settings.bet_amount)
                dealer_hand = Hand()
                # deal sequence: player, dealer up, player, dealer hole
                player_hand.add_card(shoe.draw())
                dealer_hand.add_card(shoe.draw())
                player_hand.add_card(shoe.draw())
                dealer_hand.add_card(shoe.draw())

                player_hands = player.play(shoe, dealer_hand.cards[0].rank, player_hand)
                if any(not h.is_bust and not h.surrendered for h in player_hands):
                    dealer.play(dealer_hand, shoe)
                for hand in player_hands:
                    change = self.resolve_hand(hand, dealer_hand, player_settings)
                    player_settings.bankroll += change
                hands_played += len(player_hands)
                cur.execute("INSERT INTO bankroll VALUES (?,?,?)", (trial, hands_played, player_settings.bankroll))
            cur.execute("INSERT INTO summary VALUES (?,?,?)", (trial, hands_played, player_settings.bankroll))
            for card, count in shoe.drawn_counts.items():
                cur.execute("INSERT INTO card_distribution VALUES (?,?,?)", (trial, card, count))
            self.conn.commit()
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
