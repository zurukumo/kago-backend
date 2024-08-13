from __future__ import annotations

from time import sleep
from typing import TYPE_CHECKING

from .const import Const
from .kago import Kago

if TYPE_CHECKING:
    from .game import Game


# TODO ダブロン検証
class GameRoutine:
    def __init__(self, game: Game):
        self.game = game

    def next(self):
        # sleep(10)

        # 行動のリセット
        for player in self.game.players:
            player.action.reset_actions()

        # 局開始状態
        if self.game.state == Const.KYOKU_START_STATE:
            if self.game.kyoku >= 8 or any(player.score < 0 for player in self.game.players):
                for player in self.game.players:
                    player.message.syukyoku_message()
                self.prev_state = Const.KYOKU_START_STATE
                self.game.state = Const.SYUKYOKU_STATE
                return True

            self.game.action.start_kyoku()
            for player in self.game.players:
                player.message.start_kyoku_message()

            self.prev_state = self.game.state
            self.game.state = Const.TSUMO_STATE
            return True

        # ツモ状態
        elif self.game.state == Const.TSUMO_STATE:
            if len(self.game.yama) == 0:
                self.prev_state = Const.TSUMO_STATE
                self.game.state = Const.RYUKYOKU_STATE
                return True

            # ツモ(暗槓のときは手番を増やさない)
            if self.prev_state != Const.NOTICE1_STATE:
                self.game.teban = (self.game.teban + 1) % 4
            tsumo = self.game.yama.pop()
            self.game.players[self.game.teban].action.tsumo(tsumo)

            # 選択を格納
            self.game.tsumoho_decisions = dict()
            self.game.ankan_decisions = dict()
            self.game.riichi_decisions = dict()

            # 送信
            for player in self.game.players:
                player.message.tsumo_message(tsumo)
            self.game.players[self.game.teban].message.tsumoho_notice_message()
            self.game.players[self.game.teban].message.riichi_notice_message()
            self.game.players[self.game.teban].message.ankan_notice_message()

            # AIの選択を格納
            player = self.game.players[self.game.teban]
            if isinstance(player, Kago):
                self.game.tsumoho_decisions[player.position] = player.decide_tsumoho()
                self.game.riichi_decisions[player.position] = player.decide_riichi()
                self.game.ankan_decisions[player.position] = player.decide_ankan()

            self.prev_state = Const.TSUMO_STATE
            self.game.state = Const.NOTICE1_STATE
            return True

        # 通知1受信状態
        elif self.game.state == Const.NOTICE1_STATE:
            if len(self.game.tsumoho_decisions) != 1 or len(self.game.riichi_decisions) != 1 or len(self.game.ankan_decisions) != 1:
                return False

            self.game.dahai_decisions = dict()

            # ツモの決定
            who, tf = list(self.game.tsumoho_decisions.items())[0]
            if tf:
                tsumoho = self.game.players[int(who)].action.tsumoho()
                for player in self.game.players:
                    player.message.tsumoho_message(tsumoho)

                self.prev_state = Const.NOTICE1_STATE
                self.game.state = Const.NOTICE3_STATE
                return True

            # 暗槓の決定
            who, pais = list(self.game.ankan_decisions.items())[0]
            if pais is not None:
                self.game.players[int(who)].action.ankan(pais)
                self.game.players[int(who)].action.open_dora()

                for player in self.game.players:
                    player.message.ankan_message(pais)
                    player.message.open_dora_message()

                self.prev_state = Const.NOTICE1_STATE
                self.game.state = Const.TSUMO_STATE
                return True

            # リーチの決定
            who, tf = list(self.game.riichi_decisions.items())[0]
            if tf:
                self.game.players[int(who)].action.riichi_declare()
                for player in self.game.players:
                    player.message.riichi_declare_notice_message()

                self.prev_state = Const.NOTICE1_STATE
                self.game.state = Const.DAHAI_STATE
                return True

            self.prev_state = Const.NOTICE1_STATE
            self.game.state = Const.DAHAI_STATE
            return True

        # 打牌受信状態
        elif self.game.state == Const.DAHAI_STATE:
            # AIの選択を格納
            player = self.game.players[self.game.teban]
            if player.position not in self.game.dahai_decisions and isinstance(player, Kago):
                self.game.dahai_decisions[player.position] = player.decide_dahai()

            if len(self.game.dahai_decisions) != 1:
                return False

            who, pai = list(self.game.dahai_decisions.items())[0]

            # 打牌
            self.game.players[int(who)].action.dahai(pai)
            self.game.players[int(who)].action.riichi(pai)

            # 選択を格納
            self.game.ronho_decisions = dict()
            self.game.pon_decisions = dict()
            self.game.chi_decisions = dict()

            # 送信
            for player in self.game.players:
                player.message.dahai_message(pai)
                if pai in [player.riichi_pai for player in self.game.players]:
                    player.message.riichi_bend_message(pai)

                player.message.ronho_notice_message()
                player.message.pon_notice_message()
                player.message.chi_notice_message()

            # AIの選択を格納
            for player in self.game.players:
                if isinstance(player, Kago):
                    self.game.ronho_decisions[player.position] = player.decide_ronho()
                    self.game.pon_decisions[player.position] = [player.decide_pon(), self.game.last_dahai]
                    self.game.chi_decisions[player.position] = [player.decide_chi(), self.game.last_dahai]

            self.prev_state = Const.DAHAI_STATE
            self.game.state = Const.NOTICE2_STATE
            return True

        # 通知2受信状態
        elif self.game.state == Const.NOTICE2_STATE:
            if len(self.game.ronho_decisions) != 4 or len(self.game.pon_decisions) != 4 or len(self.game.chi_decisions) != 4:
                return False

            # ロン決定
            for who, tf in self.game.ronho_decisions.items():
                if not tf:
                    continue
                ronho = self.game.players[int(who)].action.ronho()
                for player in self.game.players:
                    player.message.ronho_message(ronho)

                self.prev_state = Const.NOTICE2_STATE
                self.game.state = Const.NOTICE3_STATE
                return True

            # ロンじゃなければリーチ成立
            player = self.game.players[self.game.teban]
            if player.is_riichi_declared and not player.is_riichi_completed:
                player.action.riichi_complete()
                for player in self.game.players:
                    player.message.riichi_complete_message()

            # ポン決定
            for who, (pais, pai) in self.game.pon_decisions.items():
                if pais is not None:
                    self.game.players[int(who)].action.pon(pais, pai)
                    for player in self.game.players:
                        player.message.pon_message(pais, pai)

                    self.game.dahai_decisions = dict()
                    self.prev_state = Const.NOTICE2_STATE
                    self.game.state = Const.DAHAI_STATE
                    return True

            # チー決定
            for who, (pais, pai) in self.game.chi_decisions.items():
                if pais is not None:
                    self.game.players[int(who)].action.chi(pais, pai)
                    for player in self.game.players:
                        player.message.chi_message(pais, pai)

                    self.game.dahai_decisions = dict()
                    self.prev_state = Const.NOTICE2_STATE
                    self.game.state = Const.DAHAI_STATE
                    return True

            self.prev_state = Const.NOTICE2_STATE
            self.game.state = Const.TSUMO_STATE
            return True

        # 通知3状態受信状態(和了や流局から次局へ)
        elif self.game.state == Const.NOTICE3_STATE:
            if self.game.mode == Const.AUTO_MODE:
                self.game.action.next_kyoku()
                return True

        # 流局状態
        elif self.game.state == Const.RYUKYOKU_STATE:
            ryukyoku = self.game.action.ryukyoku()
            for player in self.game.players:
                player.message.ryukyoku_message(ryukyoku)

            self.prev_state = Const.RYUKYOKU_STATE
            self.game.state = Const.NOTICE3_STATE
            return True

        # 終局状態
        elif self.game.state == Const.SYUKYOKU_STATE:
            pass
