from offer import Offer, Direction
from player import Puppet, RandomWalker, TrendFollower
from exchange import Ex
from collections import deque

def test_player_init():
    portfolio = {
        "player_id" : "dummy_player",
        "money"     : 1_000_000.0,
        "n_stock"   : 1_000,
    }

    player = Puppet(**portfolio)
    player.assign_decisions(deque([
        Offer("dummy_player", Direction.BUY, 13, 100.0),
        Offer("dummy_player", Direction.SELL, 7, 99.0),
    ]))

    assert player.player_id == "dummy_player"
    assert player.money == 1_000_000.0
    assert player.n_stock == 1_000

def test_player_decide_type():
    portfolio = {
        "player_id" : "dummy_player",
        "money"     : 1_000_000.0,
        "n_stock"   : 1_000,
    }

    player = Puppet(**portfolio)
    player.assign_decisions(deque([
        Offer("dummy_player", Direction.BUY, 13, 100.0),
        Offer("dummy_player", Direction.SELL, 7, 99.0),
    ]))

    decisions = player.decide()
    assert isinstance(decisions, list)
    assert isinstance(decisions[0], Offer)

def test_player_ack_buy_done():
    portfolio = {
        "player_id" : "dummy_player",
        "money"     : 1_000_000.0,
        "n_stock"   : 1_000,
    }

    player = Puppet(**portfolio)
    player.assign_decisions(deque([
        Offer("dummy_player", Direction.BUY, 13, 100.0),
        Offer("dummy_player", Direction.SELL, 7, 99.0),
    ]))

    # The base player by default give a buy,
    # then a sell of some parameters.
    # It is by design for testing. 
    offer_buy_list = player.decide()
    offer_sell_list = player.decide()

    assert len(offer_buy_list) == 1
    assert len(offer_sell_list) == 1

    offer_buy = offer_buy_list[0]
    offer_sell = offer_sell_list[0]

    assert offer_buy.direction == Direction.BUY

    # Initial condition
    assert len(player.outstanding_offer) == 2
    assert offer_buy.n_stock == 13


    # Modify
    assert player.deal_done(offer_buy, Direction.BUY, 1, 100)

    # Modified condition
    assert offer_buy.n_stock == 12

    assert player.money == 1_000_000.0 - 1*100
    assert player.n_stock == 1_000 + 1
    assert len(player.outstanding_offer) == 2

    # Modify again
    assert player.deal_done(offer_buy, Direction.BUY, 12, 99)
    assert offer_buy.n_stock == 0

    # Modified condition
    assert player.money == 1_000_000.0 - 1*100 - 12*99
    assert player.n_stock == 1_000 + 1 + 12
    assert len(player.outstanding_offer) == 1


    # Initial before a sell is done
    assert offer_sell.direction == Direction.SELL
    assert offer_sell.n_stock == 7
    assert len(player.outstanding_offer) == 1

    # Modify
    assert player.deal_done(offer_sell, Direction.SELL, 1, 99)

    # Modified condition
    assert offer_sell.n_stock == 6

    assert player.money == 1_000_000.0 - 1*100 - 12*99 + 1*99
    assert player.n_stock == 1_000 + 1 + 12 - 1
    assert len(player.outstanding_offer) == 1

    # Modify again
    assert player.deal_done(offer_sell, Direction.SELL, 6, 100)

    # Modified condition
    assert offer_sell.n_stock == 0

    assert player.money == 1_000_000.0 - 1*100 - 12*99 + 1*99 + 6*100
    assert player.n_stock == 1_000 + 1 + 12 - 1 - 6
    assert len(player.outstanding_offer) == 0

def test_random_walker():
    portfolio = {
        "player_id" : "random_player",
        "money"     : 1_000_000.0,
        "n_stock"   : 1_000,
    }

    player = RandomWalker(**portfolio)

    ex = Ex() # Dummy. Will no use.

    player.assign_ex(ex)

    for _ in range(10):
        offer = player.decide()
        assert (set(player.outstanding_offer) - set(offer)) == set()
        assert len(player.outstanding_offer) == 1

def test_trend_follower():
    portfolio = {
        "player_id" : "trend_player",
        "money"     : 1_000_000.0,
        "n_stock"   : 1_000,
    }

    player = TrendFollower(**portfolio)

    ex = Ex() # Only use the final price. Init to 100 by default.

    player.assign_ex(ex)

    # No offers when not enough data
    for i in range(9):
        offers = player.decide()
        assert offers == [], f"{i=}"
        assert len(player.outstanding_offer) == 0, f"{i=}"

    # No offers when the trend is unclear
    # (the final price doesn't move)
    for i in range(10):
        offers = player.decide()
        assert offers == [], f"{i=}"
        assert len(player.outstanding_offer) == 0, f"{i=}"

    # Make the trend goes up
    ex.final_price = 150
    offers = player.decide()

    for i in range(3):
        offers = player.decide()

        assert len(offers) == 2, f"{i=}"
        assert len(player.outstanding_offer) == 1, f"{i=}"

        for offer in offers:
            assert offer.direction == Direction.BUY, f"{i=}"

    # Make the trend unclear again
    for i in range(10):
        offers = player.decide()

    for i in range(10):
        offers = player.decide()
        assert offers == [], f"{i=}"
        assert len(player.outstanding_offer) == 0, f"{i=}"

    # Make the trend goes down
    ex.final_price = 50
    offers = player.decide()

    for i in range(3):
        offers = player.decide()

        assert len(offers) == 2, f"{i=}"
        assert len(player.outstanding_offer) == 1, f"{i=}"

        for offer in offers:
            assert offer.direction == Direction.SELL, f"{i=}"

