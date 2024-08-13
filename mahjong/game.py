from typing import List, Optional

from .const import Const
from .game_action import GameAction
from .game_routine import GameRoutine
from .player import Player


# TODO 喰い替え禁止
class Game:
    def __init__(self):
        self.mode: int = Const.NORMAL_MODE
        self.players: List[Player] = []
        self.kyoku: int = 0
        self.honba: int = 0
        self.kyoutaku: int = 0
        self.teban: int = None
        self.last_teban: Optional[int] = None
        self.last_tsumo: Optional[int] = None
        self.last_dahai: Optional[int] = None
        self.yama: List[int] = []
        self.dora: List[int] = []
        self.rinshan: List[int] = []
        self.n_opened_dora: int = 0
        self.n_kan: int = 0
        self.pc: int = None
        self.tsumoho_decisions: dict = dict()
        self.ronho_decisions: dict = dict()
        self.riichi_decisions: dict = dict()
        self.ankan_decisions: dict = dict()
        self.minkan_decisions: dict = dict()
        self.pon_decisions: dict = dict()
        self.chi_decisions: dict = dict()
        self.dahai_decisions: dict = dict()
        self.prev_state: Optional[int] = None
        self.state: Optional[int] = None
        self.dummy: List[int] = []

        self.action = GameAction(self)
        self.routine = GameRoutine(self)

    def find_player(self, player_id):
        for player in self.players:
            if player.id == player_id:
                return player

    def make_dummy(self, original):
        if self.mode in [Const.VISIBLE_MODE, Const.AUTO_MODE]:
            return original
        return self.dummy[original]

    def make_dummies(self, original):
        if self.mode in [Const.VISIBLE_MODE, Const.AUTO_MODE]:
            return original
        return [self.dummy[o] for o in original]

    def make_simple(self, original):
        if original == 16:
            return 35
        if original == 52:
            return 36
        if original == 88:
            return 37
        return original // 4

    def prange(self):
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
