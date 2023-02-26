from offer import Direction, Offer
import uuid

def test_offer_repr():
    my_offer = Offer("dummy_player", Direction.BUY, 10, 100.0)
    assert isinstance(my_offer.offer_id, uuid.UUID)

def test_buy_offer_str():
    my_offer = Offer("dummy_player", Direction.BUY, 10, 100.0)

    offer_str = str(my_offer)

    assert len(offer_str.split()) == 5

    oracle = "Player:dummy_player Direction.BUY 10 @$100.00"
    assert offer_str[-len(oracle):] == oracle

def test_sell_offer_str():
    my_offer = Offer("dummy_player", Direction.SELL, 17, 243.4)
    offer_str = str(my_offer)

    assert len(offer_str.split()) == 5

    oracle = "Player:dummy_player Direction.SELL 17 @$243.40"
    assert offer_str[-len(oracle):] == oracle

