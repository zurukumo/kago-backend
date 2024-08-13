from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple

from kago_utils.hai import Hai136List
from kago_utils.shanten import Shanten

from .player_action import PlayerAction
from .player_judge import PlayerJudge
from .player_message import PlayerMessage
from .shanten import get_yuko

if TYPE_CHECKING:
    from .game import Game


class Player:
    def __init__(self, id, game: Game):
        self.id = id
        self.actions: List[dict] = []

        self.position: int = 0
        self.score: int = 0
        self.tehai: List[int] = []
        self.kawa: List[int] = []
        self.huuro: List[dict] = []
        self.riichi_pc: int | None = None
        self.riichi_pai: int | None = None
        self.is_riichi_declared: bool = False
        self.is_riichi_completed: bool = False

        self.game = game
        self.action = PlayerAction(game=game, player=self)
        self.judge = PlayerJudge(game=game, player=self)
        self.message = PlayerMessage(game=game, player=self)

    # 汎用関数
    def prange(self) -> List[Tuple[int, Player]]:
        return [(i % 4, self.game.players[i % 4]) for i in range(self.position, self.position + 4)]

    def calc_shanten(self, add=[], remove=[]):
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        return Shanten.calculate_shanten(jun_tehai, len(self.huuro))

    def get_yuko(self, add=[], remove=[]):
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        return get_yuko(jun_tehai, n_huuro=len(self.huuro))
