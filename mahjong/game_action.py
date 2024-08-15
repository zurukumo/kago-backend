
from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any, Dict, List

from .const import Const
from .human import Human
from .kago import Kago

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


class GameAction:
    game: Game

    def __init__(self, game: Game):
        self.game = game

    def start_game(self, mode: int) -> None:
        self.game.mode = mode

        # Player関連
        if mode == Const.AUTO_MODE:
            self.game.players = [
                Kago(id=0, game=self.game),
                Kago(id=1, game=self.game),
                Kago(id=2, game=self.game),
                Kago(id=3, game=self.game)
            ]
        else:
            self.game.players = [
                Human(id=0, game=self.game),
                Kago(id=1, game=self.game),
                Kago(id=2, game=self.game),
                Kago(id=3, game=self.game)
            ]

        # 半荘関連
        self.game.kyoku = 0
        self.game.honba = 0
        self.game.kyoutaku = 0
        random.shuffle(self.game.players)
        for i, player in enumerate(self.game.players):
            player.action.start_game(position=i)

        self.game.prev_state = Const.INITIAL_STATE
        self.game.state = Const.KYOKU_START_STATE

    def start_kyoku(self) -> None:
        # 各プレイヤーの手牌・河・副露の初期化
        for player in self.game.players:
            player.action.start_kyoku()

        # 手番設定(最初は1引く)
        self.game.teban = (self.game.kyoku - 1) % 4

        # ダミーデータ生成
        self.game.dummy = [136 + i for i in range(136)]
        random.shuffle(self.game.dummy)

        # 山生成
        self.game.yama = [i for i in range(136)]
        random.shuffle(self.game.yama)

        # ドラ生成
        self.game.dora = []
        for _ in range(10):
            self.game.dora.append(self.game.yama.pop())
        self.game.n_opened_dora = 1

        # 嶺上生成
        self.game.rinshan = []
        for _ in range(4):
            self.game.rinshan.append(self.game.yama.pop())

        # 配牌
        for player in self.game.players:
            for _ in range(13):
                tsumo = self.game.yama.pop()
                player.action.tsumo(tsumo)

        # 最後の打牌・手番
        self.game.last_tsumo = None
        self.game.last_dahai = None
        self.game.last_teban = None

        # カンの個数
        self.game.n_kan = 0

        # プログラムカウンター
        self.game.pc = 0

        # 通知
        self.game.tsumoho_decisions = dict()
        self.game.ronho_decisions = dict()
        self.game.riichi_decisions = dict()
        self.game.ankan_decisions = dict()
        self.game.minkan_decisions = dict()
        self.game.pon_decisions = dict()
        self.game.chi_decisions = dict()
        self.game.dahai_decisions = dict()

        # 状態
        self.game.prev_state = self.game.state
        self.game.state = Const.KYOKU_START_STATE

    def tsumoho(self, player: Player) -> None:
        if player.judge.can_tsumoho():
            self.game.tsumoho_decisions[player.position] = True
            self.game.ankan_decisions[player.position] = None
            self.game.riichi_decisions[player.position] = False

    def ankan(self, pais: List[int], player: Player) -> None:
        if player.judge.can_ankan(pais):
            self.game.tsumoho_decisions[player.position] = False
            self.game.ankan_decisions[player.position] = pais
            self.game.riichi_decisions[player.position] = False

    def riichi_declare(self, player: Player) -> None:
        for i in player.tehai:
            if player.judge.can_riichi_declare(i):
                self.game.tsumoho_decisions[player.position] = False
                self.game.ankan_decisions[player.position] = None
                self.game.riichi_decisions[player.position] = True
                break

    def dahai(self, dahai: int, player: Player) -> None:
        if player.judge.can_dahai(dahai):
            self.game.dahai_decisions[player.position] = dahai

    def ronho(self, player: Player) -> None:
        if player.judge.can_ronho():
            self.game.ronho_decisions[player.position] = True
            self.game.pon_decisions[player.position] = (None, None)
            self.game.chi_decisions[player.position] = (None, None)

    def pon(self, pais: List[int], pai: int, player: Player) -> None:
        if player.judge.can_pon(pais, pai):
            self.game.ronho_decisions[player.position] = False
            self.game.pon_decisions[player.position] = (pais, pai)
            self.game.chi_decisions[player.position] = (None, None)

    def chi(self, pais: List[int], pai: int, player: Player) -> None:
        if player.judge.can_chi(pais, pai):
            self.game.ronho_decisions[player.position] = False
            self.game.pon_decisions[player.position] = (None, None)
            self.game.chi_decisions[player.position] = (pais, pai)

    def ryukyoku(self) -> Dict[str, Any]:
        is_tenpais = []
        for player in self.game.players:
            is_tenpais.append(bool(player.calc_shanten() <= 0))

        n_tenpai = is_tenpais.count(True)
        scores = []
        score_movements = []
        for i, player in enumerate(self.game.players):
            if is_tenpais[i] and n_tenpai == 1:
                score_movements.append(3000)
            if is_tenpais[i] and n_tenpai == 2:
                score_movements.append(1500)
            if is_tenpais[i] and n_tenpai == 3:
                score_movements.append(1000)
            if not is_tenpais[i] and n_tenpai == 1:
                score_movements.append(-1000)
            if not is_tenpais[i] and n_tenpai == 2:
                score_movements.append(-1500)
            if not is_tenpais[i] and n_tenpai == 3:
                score_movements.append(-3000)
            if n_tenpai == 0 or n_tenpai == 4:
                score_movements.append(0)

            player.score += score_movements[i]
            scores.append(player.score)

        self.game.honba += 1
        if not is_tenpais[self.game.kyoku % 4]:
            self.game.kyoku += 1

        return {
            'scores': scores,
            'score_movements': score_movements
        }

    def game_info(self) -> Dict[str, Any]:
        dora = self.game.dora[:self.game.n_opened_dora] + \
            self.game.make_dummies(self.game.dora[self.game.n_opened_dora:5])
        n_yama = len(self.game.yama)

        return {
            'kyoku': self.game.kyoku,
            'honba': self.game.honba,
            'kyoutaku': self.game.kyoutaku,
            'dora': dora,
            'n_yama': n_yama,
        }

    def next_kyoku(self) -> None:
        if self.game.state == Const.NOTICE3_STATE:
            self.game.state = Const.KYOKU_START_STATE
