from exchange import Ex
from player import Puppet
from offer import Direction, Offer

import random
from collections import deque


def test_exchange_basic():
    ex = Ex()
    assert ex.add_player(Puppet("player_01", 1_000_000, 1_000))

def test_money_statistic():
    ex = Ex()

    total_money = 0

    for i in range(10):
        money = random.randrange(1_000_000, 2_000_000)
        total_money += money
        ex.add_player(Puppet(f"player_{i}", money, 1_000))

    assert total_money == ex.all_players_money()

def test_n_stock_statistic():
    ex = Ex()

    total_n_stock = 0

    for i in range(10):
        n_stock = random.randrange(1_000, 2_000)
        total_n_stock += n_stock
        ex.add_player(Puppet(f"player_{i}", 1_000_000, n_stock))

    assert total_n_stock == ex.all_players_n_stock()

def test_tick():
    ex = Ex()

    for i in range(10):
        money = random.randrange(1_000_000, 2_000_000)
        n_stock = random.randrange(1_000, 2_000)

        portfolio = {
            "player_id" : f"player_{i}",
            "money"     : money,
            "n_stock"   : n_stock,
        }

        p = Puppet(**portfolio)
        p.assign_decisions(deque([
                Offer(f"player_{i}", Direction.BUY, i, 100.0+i),
                Offer(f"player_{i}", Direction.SELL, i, 200.0+1),
        ]))
        ex.add_player(p)

    assert ex.offers == {}

    ex.tick()
    ex.print_offers()

    assert len(ex.offers) == 10

    ex.tick()
    ex.print_offers()

    assert len(ex.offers) == 20

    ex.tick()
    ex.print_offers()

    assert len(ex.offers) == 20

def get_standard_ex():
    ex = Ex()

    for i in range(1,3):
        portfolio = {
            "player_id" : f"player_{i}",
            "money"     : 1_000_000,
            "n_stock"   : 2_000,
        }

        p = Puppet(**portfolio)
        p.assign_decisions(deque())
        ex.add_player(p)

    return ex

def test_perfectly_matching_deal():
    ex = get_standard_ex()

    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.BUY, 10, 100.0)
    )
    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.SELL, 20, 200.0),
    )

    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.SELL, 10, 100.0),
    )
    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.BUY, 20, 200.0),
    )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()
    ex.dump()

    ex.deal()
    ex.tick()
    ex.deal()
    ex.tick()
    ex.deal()

    assert ex.players["player_1"].money == 1_000_000.0 - 10 * 100 + 20 * 200
    assert ex.players["player_2"].money == 1_000_000.0 + 10 * 100 - 20 * 200

    assert ex.players["player_1"].n_stock == 2_000 + 10 - 20
    assert ex.players["player_2"].n_stock == 2_000 - 10 + 20

    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

def test_perfect_price_diff_stock_deal():

    ex = get_standard_ex()

    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.BUY, 12, 100.0)
    )

    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.SELL, 8, 100.0)
    )
    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.SELL, 4, 100.0)
    )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()
    ex.dump()

    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0 - 12 * 100
    assert ex.players["player_2"].money == 1_000_000.0 + 12 * 100

    assert ex.players["player_1"].n_stock == 2_000 + 12
    assert ex.players["player_2"].n_stock == 2_000 - 12


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

    # Test again in reverse direction
    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.SELL, 12, 100.0)
    )

    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.BUY, 7, 100.0)
    )
    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.BUY, 5, 100.0)
    )

    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0
    assert ex.players["player_2"].money == 1_000_000.0

    assert ex.players["player_1"].n_stock == 2_000
    assert ex.players["player_2"].n_stock == 2_000


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

def test_deal_on_overlapped_prices():
    ex = get_standard_ex()

    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.BUY, 10, 100.7)
    )

    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.SELL, 10, 100.5)
    )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()
    ex.dump()

    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0 - 10 * 100.6
    assert ex.players["player_2"].money == 1_000_000.0 + 10 * 100.6

    assert ex.players["player_1"].n_stock == 2_000 + 10
    assert ex.players["player_2"].n_stock == 2_000 - 10


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()


def test_no_deal():
    ex = get_standard_ex()

    ex.players["player_1"].decisions.append(
        Offer("player_1", Direction.BUY, 10, 100.5)
    )

    ex.players["player_2"].decisions.append(
        Offer("player_2", Direction.SELL, 10, 100.7)
    )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()
    ex.dump()

    ex.tick()
    ex.deal()
    ex.print_offers()
    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0
    assert ex.players["player_2"].money == 1_000_000.0

    assert ex.players["player_1"].n_stock == 2_000
    assert ex.players["player_2"].n_stock == 2_000


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

def test_multiple_deal():
    ex = get_standard_ex()

    for _ in range(10):
        ex.players["player_1"].decisions.append(
            Offer("player_1", Direction.BUY, 10, 12.3)
        )

        ex.players["player_2"].decisions.append(
            Offer("player_2", Direction.SELL, 10, 12.3)
        )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()

    print("===")
    ex.dump()

    print("===")
    for _ in range(10):
        ex.tick()
    ex.print_offers()

    print("===")
    ex.deal() # Expect all deals done in one call
    ex.print_offers()

    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0 - 100 * 12.3
    assert ex.players["player_2"].money == 1_000_000.0 + 100 * 12.3

    assert ex.players["player_1"].n_stock == 2_000 + 100
    assert ex.players["player_2"].n_stock == 2_000 - 100


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

def test_deal_until_no_more():
    ex = get_standard_ex()

    for i in range(1, 6):
        for j in range(1, 6):
            ex.players["player_1"].decisions.append(
                Offer("player_1", Direction.BUY, j, 23.4+i)
            )

            ex.players["player_2"].decisions.append(
                Offer("player_2", Direction.SELL, j, 23.4+i)
            )


    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()

    print("===")
    ex.dump()

    print("===")
    for _ in range(25):
        ex.tick()
    ex.print_offers()

    print("===")
    ex.deal() # Expect all deals done in one call
    ex.print_offers()

    print("===")
    ex.dump()

    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()


def test_multiple_deal():
    ex = get_standard_ex()

    for _ in range(10):
        ex.players["player_1"].decisions.append(
            Offer("player_1", Direction.BUY, 10, 12.3)
        )

        ex.players["player_2"].decisions.append(
            Offer("player_2", Direction.SELL, 10, 12.3)
        )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()

    print("===")
    ex.dump()

    print("===")
    for _ in range(10):
        ex.tick()
    ex.print_offers()

    print("===")
    ex.deal() # Expect all deals done in one call
    ex.print_offers()

    print("===")
    ex.dump()

    assert ex.players["player_1"].money == 1_000_000.0 - 100 * 12.3
    assert ex.players["player_2"].money == 1_000_000.0 + 100 * 12.3

    assert ex.players["player_1"].n_stock == 2_000 + 100
    assert ex.players["player_2"].n_stock == 2_000 - 100


    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

def test_del_deal():
    ex = get_standard_ex()

    for i in range(1, 6):
        for j in range(1, 6):
            ex.players["player_1"].decisions.append(
                Offer("player_1", Direction.BUY, j, 23.4+i)
            )
            ex.players["player_2"].decisions.append(
                Offer("player_2", Direction.SELL, j, 23.4+i)
            )

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()

    for _ in range(25):
        ex.tick()
    ex.print_offers()

    print("===")
    ex.dump()
    print("===")
    for o in list(ex.players["player_1"].outstanding_offer):
        print(o)
    ex.players["player_1"].decisions += list(ex.players["player_1"].outstanding_offer)
    for _ in range(7):
        ex.tick()

    ex.players["player_2"].decisions += list(ex.players["player_2"].outstanding_offer)
    for _ in range(7):
        ex.tick()

    ex.print_offers()
    #ex.dump()

    print("===")
    ex.deal() # Expect all deals done in one call
    ex.print_offers()

    assert all_n_stock == ex.all_players_n_stock()
    assert all_money == ex.all_players_money()

    ex.del_all_offers()
    ex.deal() # Expect all deals done in one call
    ex.print_offers()

def test_final_price():
    ex = get_standard_ex()

    for _ in range(100):
        price = round(random.gauss(100, 10), 1)

        ex.players["player_1"].decisions.append(
            Offer("player_1", Direction.BUY, 1, price)
        )
        ex.players["player_2"].decisions.append(
            Offer("player_2", Direction.SELL, 1, price)
        )
        ex.tick()
        ex.deal()
        assert ex.final_price == price

def test_invariant():
    # Make random deals and see if everything looks right.
    ex = get_standard_ex()

    all_n_stock = ex.all_players_n_stock()
    all_money = ex.all_players_money()

    final_price = 100
    deal_done_count = 0
    n_iter = 0
    while deal_done_count < 100:
        n_iter += 1
        assert n_iter < 1_000_000, "No 100 Deals out of 1,000,000? Odd."

        price = round(random.gauss(final_price, 2), 1)
        n_stock = int(random.gauss(20, 6))
        direction = random.choice([Direction.BUY, Direction.SELL])

        ex.players["player_1"].decisions.append(
            Offer("player_1", direction, n_stock, price)
        )

        price = round(random.gauss(final_price, 2), 1)
        n_stock = int(random.gauss(20, 6))
        direction = random.choice([Direction.BUY, Direction.SELL])
        ex.players["player_2"].decisions.append(
            Offer("player_2", direction, n_stock, price)
        )

        ex.tick()
        deal_done = False
        deal_done = deal_done or ex.deal()

        if deal_done:
            deal_done_count += 1
            final_price = ex.final_price
            #print(f"{final_price=}")

        assert all_n_stock == ex.all_players_n_stock()
        assert all_money == ex.all_players_money()

    ex.print_offers()
    print("="*10)
    ex.dump()

    assert deal_done_count > 0

