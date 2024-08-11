from kago_utils.hai import Hai136List
from kago_utils.shanten import Shanten

from .shanten import get_yuko


class PlayerBase:
    def __init__(self, id, game):
        self.id = id
        self.game = game
        self.actions = {}

    # 汎用関数
    def prange(self):
        return [[i % 4, self.game.players[i % 4]] for i in range(self.position, self.position + 4)]

    def calc_shanten(self, add=[], remove=[]):
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        return Shanten.calculate_shanten(jun_tehai, len(self.huuro))

    def get_yuko(self, add=[], remove=[]):
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        return get_yuko(jun_tehai, n_huuro=len(self.huuro))
