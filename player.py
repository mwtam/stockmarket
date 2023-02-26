from offer import Direction, Offer
from collections import deque
import random

class Player:
    def __init__(self, player_id, money, n_stock):
        self.player_id = player_id
        self.money = money
        self.n_stock = n_stock

        self.outstanding_offer = set()

        self.ex = None
        # A player may want to decide according to the ex's state.
        # A common consideration is the final price.
        # Player should not change ex's state directly.
        # call assign_ex to assign one

    def assign_ex(self, ex):
        self.ex = ex

    def __repr__(self):
        return f"ID:{self.player_id}\t${self.money:,.2f}\tN:{self.n_stock}"

    def deal_done(self, offer, direction, n_stock, price):
        if offer in self.outstanding_offer:
            # No any check. Assume the caller is right.

            # When a deal is done, the offer always become smaller.
            offer.n_stock -= n_stock

            money = round(n_stock * price, 2)
            if direction == Direction.BUY:
                self.n_stock += n_stock
                self.money -= money
                self.money = round(self.money, 2)

            if direction == Direction.SELL:
                self.n_stock -= n_stock
                self.money += money
                self.money = round(self.money, 2)

            if offer.n_stock == 0:
                self.outstanding_offer.remove(offer)

            return True
        # If add checking, return False means the deal is wrong and nothing is changed here.
        return False

    def decide(self):
        raise NotImplementedError

class Puppet(Player):
    def assign_decisions(self, decisions):
        self.decisions = decisions
        # a deque of offers
        # for someone to control the decisions of this player

    def decide(self):
        """
        Return a list of offers.
        If no action, return an empty list.
        """
        if not self.decisions:
            return []

        my_offer = self.decisions.popleft()
        self.outstanding_offer.add(my_offer)
        return [my_offer]


class RandomWalker(Player):
    def __init__(self, player_id, money, n_stock):
        super().__init__(player_id, money, n_stock)
        self.price_direction = 0.5

    def decide(self):
        direction = random.choice((Direction.BUY, Direction.SELL))
        final_price = self.ex.final_price

        #if final_price > 200:
        if final_price > 125:
            #self.price_direction = -0.1
            self.price_direction = -0.5
        #elif final_price < 50:
        elif final_price < 75:
            #self.price_direction = 0.1
            self.price_direction = 0.5

        price = round(random.gauss(final_price+self.price_direction, 2), 1)
        n_stock = int(random.gauss(20, 6))
        offer = Offer(self.player_id, direction, n_stock, price)

        # Add a new offer
        my_offers = [offer]

        # Cancel all old offers
        my_offers.extend(self.outstanding_offer)
        self.outstanding_offer.clear()

        # Record the new offer
        self.outstanding_offer.add(offer)

        return my_offers

class ValueInvestor(Player):
    #def __init__(self, player_id, money, n_stock):
    #    super().__init__(player_id, money, n_stock)
    #    self.idle_count = 0

    def decide(self):

        final_price = self.ex.final_price

        offer = None

        n_stock = 500

        if final_price < 80 and self.money > final_price * n_stock:
            offer = Offer(self.player_id, Direction.BUY, n_stock, final_price)
            #offer = Offer(self.player_id, Direction.BUY, n_stock, 80)

        if final_price > 120 and self.n_stock > n_stock:
            offer = Offer(self.player_id, Direction.SELL, n_stock, final_price)
            #offer = Offer(self.player_id, Direction.SELL, n_stock, 120)

        if offer:
            # Add a new offer
            my_offers = [offer]

            # Cancel all old offers
            my_offers.extend(self.outstanding_offer)
            self.outstanding_offer.clear()

            # Record the new offer
            self.outstanding_offer.add(offer)

            return my_offers

        # Do nothing
        return []

class TrendFollower(Player):
    def __init__(self, player_id, money, n_stock):
        super().__init__(player_id, money, n_stock)
        self.five_ticks = deque([], 5)
        self.ten_ticks = deque([], 10)

    def decide(self):
        final_price = self.ex.final_price
        self.five_ticks.append(final_price)
        self.ten_ticks.append(final_price)

        if len(self.five_ticks) < 5 or len(self.ten_ticks) < 10:
            return []

        # Have enough data, start trading
        n_stock = 1
        direction = None
        if sum(self.five_ticks) > sum(self.ten_ticks) / 2:
            # Gain risk slow, release risk fast
            if self.n_stock > 0:
                n_stock = 1000
            else:
                n_stock = 3000
            direction = Direction.BUY
        elif sum(self.five_ticks) < sum(self.ten_ticks) / 2:
            if self.n_stock > 0:
                n_stock = 3000
            else:
                n_stock = 1000
            direction = Direction.SELL
        else:
            direction = None

        # Risk position control
        n_stock_max = 3_000
        if direction == Direction.BUY and self.n_stock > n_stock_max:
            direction = None
        if direction == Direction.SELL and self.n_stock < -1_000:
            direction = None

        # No direction. Cancel all offers if there is any.
        if not direction:
            cancel_offers = list(self.outstanding_offer)
            self.outstanding_offer.clear()
            return cancel_offers

        offer = Offer(self.player_id, direction, n_stock, final_price)

        # Add a new offer
        my_offers = [offer]

        # Cancel all old offers
        my_offers.extend(self.outstanding_offer)
        self.outstanding_offer.clear()

        # Record the new offer
        self.outstanding_offer.add(offer)

        return my_offers

