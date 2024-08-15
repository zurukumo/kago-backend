from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

from kago_utils.hai import Hai136List
from kago_utils.shanten import Shanten

from .player_action import PlayerAction
from .player_judge import PlayerJudge
from .player_message import PlayerMessage
from .shanten import get_yuko

if TYPE_CHECKING:
    from .game import Game


class Player:
    id: int
    actions: List[Dict[str, Any]]

    position: int
    score: int
    tehai: List[int]
    kawa: List[int]
    huuro: List[Dict[str, Any]]
    riichi_pc: Optional[int]
    riichi_pai: Optional[int]
    is_riichi_declared: bool
    is_riichi_completed: bool

    game: Game
    action: PlayerAction
    judge: PlayerJudge
    message: PlayerMessage

    def __init__(self, id: int, game: Game):
        self.id = id
        self.actions = []

        self.position = 0
        self.score = 0
        self.tehai = []
        self.kawa = []
        self.huuro = []
        self.riichi_pc = None
        self.riichi_pai = None
        self.is_riichi_declared = False
        self.is_riichi_completed = False

        self.game = game
        self.action = PlayerAction(game=game, player=self)
        self.judge = PlayerJudge(game=game, player=self)
        self.message = PlayerMessage(game=game, player=self)

    # 汎用関数
    def prange(self) -> List[Tuple[int, Player]]:
        return [(i % 4, self.game.players[i % 4]) for i in range(self.position, self.position + 4)]

    def calc_shanten(self, add: List[int] = [], remove: List[int] = []) -> int:
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        # TODO: utilsに型を追加
        return int(Shanten.calculate_shanten(jun_tehai, len(self.huuro)))

    def get_yuko(self, add: List[int] = [], remove: List[int] = []) -> List[int]:
        jun_tehai = Hai136List(self.tehai) + Hai136List(add) - Hai136List(remove)
        return get_yuko(jun_tehai, n_huuro=len(self.huuro))
