from blackjack.player import Player, PlayerSettings
from blackjack.hand import Hand
from blackjack.cards import Card


class AlwaysSurrenderStrategy:
    def decide(self, hand, dealer_up, options):
        return 'surrender'


class DummyShoe:
    def draw(self):
        raise AssertionError('draw should not be called after surrender')


def resolve(hand, dealer_hand):
    if hand.surrendered:
        return hand.bet
    if hand.is_bust:
        return 0
    dealer_bust = dealer_hand.is_bust
    if dealer_bust:
        return hand.bet * 2
    player_value = hand.best_value
    dealer_value = dealer_hand.best_value
    if player_value > dealer_value:
        return hand.bet * 2
    if player_value < dealer_value:
        return 0
    return hand.bet


def test_surrender_payout_returns_half_bet():
    settings = PlayerSettings(bankroll=100)
    bet = 10
    settings.bankroll -= bet
    initial = Hand(cards=[Card('9', 'spades'), Card('7', 'hearts')], bet=bet)
    player = Player(settings=settings, strategy=AlwaysSurrenderStrategy())
    hands = player.play(DummyShoe(), dealer_up='6', initial=initial)
    hand = hands[0]
    assert hand.surrendered
    assert hand.bet == bet / 2
    dealer_hand = Hand(cards=[Card('10', 'clubs'), Card('7', 'diamonds')])
    payout = resolve(hand, dealer_hand)
    settings.bankroll += payout
    assert settings.bankroll == 95
