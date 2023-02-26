#!/usr/bin/env python3

from offer import Direction, Offer
from player import RandomWalker, ValueInvestor, TrendFollower
from exchange import Ex

def add_players(ex):
    for i in range(1,21):
        portfolio = {
            "player_id" : f"rand_{i}",
            "money"     : 0,
            "n_stock"   : 0,
            #"money"     : 1_000_000 + i,
            #"n_stock"   : 2_000 + i,
        }
        p = RandomWalker(**portfolio)
        ex.add_player(p)

    portfolio = {
        "player_id" : f"val_1",
        "money"     : 1_000_000_000,
        "n_stock"   : 2_000,
    }
    p = ValueInvestor(**portfolio)
    ex.add_player(p)

    #portfolio = {
    #    "player_id" : f"trend_1",
    #    "money"     : 1_000_000,
    #    "n_stock"   : 2_000,
    #}
    #p = TrendFollower(**portfolio)
    #ex.add_player(p)

def main():
    ex = Ex()
    add_players(ex)

    all_n_stock_before = ex.all_players_n_stock()
    all_money_before = ex.all_players_money()

    no_deal_count = 0
    for _ in range(10000):
        ex.tick()
        #ex.print_offers()
        d = ex.deal()
        if not d:
            no_deal_count += 1

    all_n_stock_after = ex.all_players_n_stock()
    all_money_after = ex.all_players_money()

    # For code checking
    print(f"{no_deal_count=}")
    print(f"{all_n_stock_before=} {all_n_stock_after=}")
    print(f"{all_money_before=} {all_money_after=}")


if __name__ == "__main__":
    main()
