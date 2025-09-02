from blackjack.simulator import Simulator
from blackjack.settings import SimulationSettings
from blackjack.player import PlayerSettings
from blackjack.hand import Hand
from blackjack.cards import Card


def test_blackjack_payout_ratios():
    sim = Simulator(SimulationSettings(database=':memory:', blackjack_payout=1.5))
    ps = PlayerSettings(bankroll=0, blackjack_payout=1.5)
    hand = Hand(cards=[Card('A', 'spades'), Card('K', 'hearts')], bet=10)
    dealer_hand = Hand(cards=[Card('9', 'clubs'), Card('7', 'diamonds')])
    assert sim.resolve_hand(hand, dealer_hand, ps) == 10 * 2.5
    sim.close()

    sim6 = Simulator(SimulationSettings(database=':memory:', blackjack_payout=1.2))
    ps6 = PlayerSettings(bankroll=0, blackjack_payout=1.2)
    hand6 = Hand(cards=[Card('A', 'spades'), Card('K', 'hearts')], bet=10)
    dealer_hand6 = Hand(cards=[Card('9', 'clubs'), Card('7', 'diamonds')])
    assert sim6.resolve_hand(hand6, dealer_hand6, ps6) == 10 * 2.2
    sim6.close()
