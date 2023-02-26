from enum import Enum
import uuid

class Direction(Enum):
    BUY = 1
    SELL = -1

class Offer():
    def __init__(self, player_id, direction, n_stock, price):
        self.player_id = player_id
        self.direction = direction
        self.n_stock   = n_stock
        self.price     = price
        self.offer_id  = uuid.uuid4() # TODO: Should use UUID4? It is just random

    def __repr__(self):
        return str(self.offer_id)

    def __str__(self):
        return f"ID:{self.offer_id} Player:{self.player_id} {self.direction} {self.n_stock} @${self.price:.2f}"

