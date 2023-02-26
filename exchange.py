from offer import Direction, Offer
from collections import deque
import random
import uuid
from datetime import datetime
import os

class Ex:
    def __init__(self):
        self.players = {}
        self.offers = {}

        self.price2offer = {}
        self.price2offer[Direction.BUY] = {}
        self.price2offer[Direction.SELL] = {}

        self.n_tick = 0

        self.final_price = 100

        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = uuid.uuid4()
        self.output_file_name = f'deal_{now}_{run_id}.log'
        self.output_file = open(self.output_file_name, 'w')

    def __del__(self):
        self.output_file.close()

        try:
            os.remove('deal.log')
        except FileNotFoundError:
            pass

        os.symlink(self.output_file_name, 'deal.log')

    def add_player(self, player):
        self.players[player.player_id] = player
        player.assign_ex(self)
        return True

    def all_players_money(self):
        """
        For stat.
        If no dividends,
        the total money should be unchange.
        """
        total = 0
        for player_id, player in self.players.items():
            total += player.money

        return total

    def all_players_n_stock(self):
        """
        For stat.
        the total stock should be unchange.
        """
        total = 0
        for player_id, player in self.players.items():
            total += player.n_stock

        return total

    def tick(self):

        self.n_tick += 1

        #for _, player in self.players.items():
        # Access the players at random order

        players = list(self.players.values())
        random.shuffle(players)
        for player in players:
            decisions = player.decide()
            if decisions:
                self.add_offers(decisions)

    def add_offers(self, offers):
        for offer in offers:
            if offer.offer_id not in self.offers:
                self.offers[offer.offer_id] = offer
                self.price2offer[offer.direction].setdefault(offer.price, deque())
                self.price2offer[offer.direction][offer.price].append(offer.offer_id)
            else:
                # Same offer ID. It is a del instruction.
                del self.offers[offer.offer_id]
                # Do not handle the player side.
                # Since it is the player gave the del instruction,
                # assume a player would do the book keeping right.

    def dump(self):
        print("===== DUMP =====")
        print("offers")
        for k, v in self.offers.items():
            print(v)


        print("price2offer[Direction.BUY]")
        print(self.price2offer[Direction.BUY])
        print("price2offer[Direction.SELL]")
        print(self.price2offer[Direction.SELL])

        print(self.players)
        print(f"{self.final_price=}")

    def print_offers(self):
        """Helper for debug"""

        print(f"===== Tick: {self.n_tick} =====")

        print("BUY")

        for price, offer_ids in sorted(list(self.price2offer[Direction.BUY].items()), reverse=True):
            print("   ", price)
            for offer_id in offer_ids:
                if offer_id in self.offers:
                    print("       ",
                          self.offers[offer_id].player_id,
                          self.offers[offer_id].n_stock,
                          )
                else:
                    print(f"        {offer_id} deleted")

        print("SELL")
        for price, offer_ids in sorted(list(self.price2offer[Direction.SELL].items())):
            print("   ", price)
            for offer_id in offer_ids:
                if offer_id in self.offers:
                    print("       ",
                          self.offers[offer_id].player_id,
                          self.offers[offer_id].n_stock,
                          )
                else:
                    print(f"        {offer_id} deleted")

    def best_offers(self, direction):
        """
        return best offer
        "best" depends on the price. Buy and sell are opposite.
        If best_offer_ids is None, no deal is on the queue
        """

        best_price = -1
        best_offer_ids = None
        price2offer = self.price2offer[direction]

        while price2offer:
            if direction == Direction.BUY:
                # High priced buy offer first
                best_price = max(price2offer)
            elif direction == Direction.SELL:
                # Lower priced sell offer first
                best_price = min(price2offer)
            else:
                # Don't support
                pass

            if best_offer_ids := price2offer[best_price]:
                # Found. Leave the loop.
                break
            else:
                # There is a list, but it is empty. Delete it.
                del price2offer[best_price]
        else:
            # the loop exit due to price2offer is False (empty)
            best_price = -2 # not useful now. Just leave some trail.
            best_offer_ids = None

        return best_price, best_offer_ids

    def deal_one_pair(self, buy_offer, sell_offer):
        """
        Actually do the deal
        Only do one pair of offers. No more.
        """

        # Trust the deals are right.
        # Such as buy_offer is really buy and sell is really sell

        #print(buy_offer)
        #print(sell_offer)

        if buy_offer.price == sell_offer.price:
            deal_price = buy_offer.price
        elif buy_offer.price > sell_offer.price:
            deal_price = round((buy_offer.price + sell_offer.price) / 2, 1)
        else:
            # No deal
            return False
        deal_n_stock = min(buy_offer.n_stock, sell_offer.n_stock)

        buyer = self.players[buy_offer.player_id]
        seller = self.players[sell_offer.player_id]

        buyer_ok = buyer.deal_done(buy_offer, Direction.BUY, deal_n_stock, deal_price)
        seller_ok = seller.deal_done(sell_offer, Direction.SELL, deal_n_stock, deal_price)
        self.final_price = deal_price

        # Record deal
        self.output_file.write(f"{buyer}\t{seller}\t{deal_n_stock}\t{deal_price}\n")

        #print(f"{buyer_ok=} {seller_ok=}")
        return buyer_ok and seller_ok

    def pop_deleted_deals(self, offer_ids):
        while offer_ids and offer_ids[0] not in self.offers:
            offer_ids.popleft()


    def deal_one_price(self):
        """
        Find a best price and do all the deals that is suitable on this price.
        """

        deal_done = False

        best_buy_price, best_buy_offer_ids = (-1, None)
        best_sell_price, best_sell_offer_ids = (-1, None)

        while not (best_buy_offer_ids and best_sell_offer_ids):
            best_buy_price, best_buy_offer_ids = self.best_offers(Direction.BUY)

            best_sell_price, best_sell_offer_ids = self.best_offers(Direction.SELL)

            if not best_buy_offer_ids or not best_sell_offer_ids:
                # No deal
                return False

            # Pop the deleted deals.
            # If ended up all deals of buy or sell are pop-ed,
            # loop to find next best price
            self.pop_deleted_deals(best_buy_offer_ids)
            self.pop_deleted_deals(best_sell_offer_ids)

        #print("best_buy_price: ", best_buy_price)
        #print("best_buy_offer_ids: ", best_buy_offer_ids)

        #print("best_sell_price: ", best_sell_price)
        #print("best_sell_offer_ids: ", best_sell_offer_ids)

        while best_buy_offer_ids and best_sell_offer_ids:
            buy_offer = self.offers[best_buy_offer_ids[0]]
            sell_offer = self.offers[best_sell_offer_ids[0]]

            deal_done_once = self.deal_one_pair(buy_offer, sell_offer)

            if not deal_done_once:
                break

            # Some deal is done
            deal_done = deal_done or deal_done_once
            #print(f"deal_one_price: {deal_done=}")

            if buy_offer.n_stock == 0:
                # remove buy_offer
                buy_offer_id = best_buy_offer_ids.popleft()
                del self.offers[buy_offer_id]
                self.pop_deleted_deals(best_buy_offer_ids)
                if not best_buy_offer_ids:
                    del self.price2offer[Direction.BUY][best_buy_price]


            if sell_offer.n_stock == 0:
                # remove sell_offer
                sell_offer_id = best_sell_offer_ids.popleft()
                del self.offers[sell_offer_id]
                self.pop_deleted_deals(best_sell_offer_ids)
                if not best_sell_offer_ids:
                    del self.price2offer[Direction.SELL][best_sell_price]


        return deal_done

    def deal(self):
        # Keep finding best price and do deals until no more could be found.
        deal_done = False
        while self.deal_one_price():
            deal_done = True
        return deal_done

    def del_all_offers(self):
        for player_id, player in self.players.items():
            player.outstanding_offer.clear()

        self.offers.clear()
        self.price2offer[Direction.BUY].clear()
        self.price2offer[Direction.SELL].clear()

# TODO: Print or log something for analysis. Such as
# 1. The n_stock and money of all players
# 2. The final price
# Or, should it be done in a driver (who calls tick and deal) instead of inside Ex?

# TODO: Lint the code

# TODO (later): del out of range offers when the price moved too far away
