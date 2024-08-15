from typing import Any, Dict, List, Optional, Tuple

from .const import Const
from .game_action import GameAction
from .game_routine import GameRoutine
from .player import Player


# TODO 喰い替え禁止
class Game:
    action: GameAction
    routine: GameRoutine

    mode: int
    players: List[Player]
    kyoku: int
    honba: int
    kyoutaku: int
    teban: int
    last_teban: Optional[int]
    last_tsumo: Optional[int]
    last_dahai: Optional[int]
    yama: List[int]
    dora: List[int]
    rinshan: List[int]
    n_opened_dora: int
    n_kan: int
    pc: int
    tsumoho_decisions: Dict[int, bool]
    ronho_decisions: Dict[int, bool]
    riichi_decisions: Dict[int, bool]
    ankan_decisions: Dict[int, Any]
    minkan_decisions: Dict[int, Tuple[Optional[int], Optional[int]]]
    pon_decisions: Dict[int, Tuple[Optional[List[int]], Optional[int]]]
    chi_decisions: Dict[int, Tuple[Optional[List[int]], Optional[int]]]
    dahai_decisions: Dict[int, int]
    prev_state: Optional[str]
    state: Optional[str]
    dummy: List[int]

    def __init__(self) -> None:
        self.action = GameAction(self)
        self.routine = GameRoutine(self)

    def find_player(self, player_id: int) -> Player:
        for player in self.players:
            if player.id == player_id:
                return player

        raise ValueError(f'Player {player_id} not found')

    def make_dummy(self, original: int) -> int:
        if self.mode in [Const.VISIBLE_MODE, Const.AUTO_MODE]:
            return original
        return self.dummy[original]

    def make_dummies(self, original: List[int]) -> List[int]:
        if self.mode in [Const.VISIBLE_MODE, Const.AUTO_MODE]:
            return original
        return [self.dummy[o] for o in original]

    def make_simple(self, original: int) -> int:
        if original == 16:
            return 35
        if original == 52:
            return 36
        if original == 88:
            return 37
        return original // 4

    def prange(self) -> List[Player]:
        return [self.players[i % 4] for i in range(self.teban, self.teban + 4)]
