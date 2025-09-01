from blackjack.player import Player, PlayerSettings
from blackjack.hand import Hand
from blackjack.cards import Card


class DoubleStrategy:
    def decide(self, hand, dealer_up, options):
        if options.get('can_double') and len(hand.cards) == 2:
            return 'double'
        return 'stand'


class SplitStrategy:
    def decide(self, hand, dealer_up, options):
        if options.get('can_split') and hand.can_split:
            return 'split'
        return 'stand'


class MockShoe:
    def __init__(self, cards):
        self.cards = list(cards)
    def draw(self):
        return self.cards.pop(0)


def resolve(hand, dealer_hand):
    if hand.surrendered:
        return hand.bet
    if hand.is_bust:
        return 0
    if dealer_hand.is_bust:
        return hand.bet * 2
    pv = hand.best_value
    dv = dealer_hand.best_value
    if pv > dv:
        return hand.bet * 2
    if pv < dv:
        return 0
    return hand.bet


def test_bankroll_updated_after_double_win():
    settings = PlayerSettings(bankroll=100)
    bet = 10
    settings.bankroll -= bet
    initial = Hand(cards=[Card('5', 'hearts'), Card('6', 'clubs')], bet=bet)
    shoe = MockShoe([Card('9', 'spades')])
    player = Player(settings=settings, strategy=DoubleStrategy())
    hands = player.play(shoe, dealer_up='2', initial=initial)
    hand = hands[0]
    assert hand.bet == 2 * bet
    assert settings.bankroll == 80
    dealer_hand = Hand(cards=[Card('10', 'diamonds'), Card('8', 'clubs')])
    payout = resolve(hand, dealer_hand)
    settings.bankroll += payout
    assert settings.bankroll == 120


def test_bankroll_updated_after_split_win():
    settings = PlayerSettings(bankroll=100)
    bet = 10
    settings.bankroll -= bet
    initial = Hand(cards=[Card('8', 'spades'), Card('8', 'hearts')], bet=bet)
    shoe = MockShoe([Card('10', 'clubs'), Card('9', 'diamonds')])
    player = Player(settings=settings, strategy=SplitStrategy())
    hands = player.play(shoe, dealer_up='6', initial=initial)
    assert len(hands) == 2
    assert settings.bankroll == 80
    dealer_hand = Hand(cards=[Card('10', 'hearts'), Card('6', 'diamonds'), Card('8', 'spades')])
    payout = sum(resolve(h, dealer_hand) for h in hands)
    settings.bankroll += payout
    assert settings.bankroll == 120
