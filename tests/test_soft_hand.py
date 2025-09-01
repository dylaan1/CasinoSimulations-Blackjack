from blackjack.hand import Hand
from blackjack.cards import Card


def test_soft_hand_value_transitions():
    hand = Hand(cards=[Card('A', 'spades'), Card('5', 'hearts')])
    assert hand.values == [6, 16]
    assert hand.best_value == 16

    hand.add_card(Card('10', 'clubs'))
    assert hand.values == [16, 26]
    assert hand.best_value == 16

    hand.add_card(Card('5', 'diamonds'))
    assert hand.values == [21, 31]
    assert hand.best_value == 21
