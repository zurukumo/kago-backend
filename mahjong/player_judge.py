from __future__ import annotations

from typing import TYPE_CHECKING

from .agari import Agari
from .const import Const

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


# TODO フリテンツモしない
class PlayerJudge:
    def __init__(self, game: Game, player: Player):
        self.game = game
        self.player = player

    def can_tsumoho(self):
        if self.game.teban != self.player.position:
            # print('手番じゃない')
            return False
        if self.player.calc_shanten() >= 0:
            # print('和了ってない')
            return False
        # TODO パオ
        if Agari(self.player, self.game).score_movements == [0, 0, 0, 0]:
            # print('役無し')
            return False

        return True

    def can_dahai(self, dahai):
        if self.game.teban != self.player.position:
            # print('手番じゃない')
            return False
        if self.game.state not in [Const.NOTICE1_STATE, Const.DAHAI_STATE]:
            # print('ステート異常')
            return False
        if dahai not in self.player.tehai:
            # print('手牌に打牌する牌がない')
            return False
        if self.player.is_riichi_completed and dahai != self.game.last_tsumo:
            # print('リーチ後にツモ切りしてない')
            return False
        if self.player.is_riichi_declared and not self.player.is_riichi_completed and self.player.calc_shanten(remove=[dahai]) > 0:
            # print('聴牌しないリーチ宣言牌')
            return False

        return True

    def can_riichi_declare(self, dahai):
        if self.game.teban != self.player.position:
            # print('手番じゃない')
            return False
        if self.player.is_riichi_completed:
            # print('リーチしている')
            return False
        if self.game.state not in [Const.TSUMO_STATE, Const.NOTICE1_STATE, Const.DAHAI_STATE]:
            # print('ステート異常')
            return False
        huuro_types = [huuro['type'] for huuro in self.player.huuro]
        if len(huuro_types) - huuro_types.count('ankan') != 0:
            # print('門前じゃない')
            return False
        if self.player.score < 1000:
            # print('1000点ない')
            return False
        if self.player.calc_shanten(remove=[dahai]) > 0:
            # print('テンパってない')
            return False

        return True

    def can_ankan(self, ankan):
        if self.game.teban != self.player.position:
            # print('手番じゃない')
            return False
        if self.game.state != Const.TSUMO_STATE and self.game.state != Const.NOTICE1_STATE:
            # print('ステート以上')
            return False
        if self.game.n_kan >= 4:
            # print('カンの個数が4以上')
            return False
        if len(self.game.yama) <= 0:
            # print('山に牌がない')
            return False
        if len(ankan) != 4:
            # print('牌の数が4つじゃない')
            return False
        if len(set(ankan)) != 4:
            # print('牌番号に同じものがある')
            return False
        if len(set([i // 4 for i in ankan])) != 1:
            # print('牌を4で割った商が全て同じじゃない')
            return False
        for i in ankan:
            if i not in self.player.tehai:
                # print('手牌に含まれていない牌がある')
                return False
        if self.player.is_riichi_completed:
            shanten1 = self.player.calc_shanten(remove=[self.game.last_tsumo])
            shanten2 = self.player.calc_shanten(remove=ankan)
            machi1 = self.get_yuko(remove=[self.game.last_tsumo])
            machi2 = self.get_yuko(remove=ankan)
            if shanten1 != shanten2 or machi1 != machi2:
                print('リーチ後に待ちの変わる暗槓')
                return False

        return True

    def can_ronho(self):
        if self.game.teban == self.player.position:
            # print('捨てた本人')
            return False
        if self.player.calc_shanten(add=[self.game.last_dahai]) >= 0:
            # print('和了ってない')
            return False
        # TODO パオ
        if Agari(self.player, self.game).score_movements == [0, 0, 0, 0]:
            # print('役無し')
            return False

        return True

    def can_pon(self, pais, pai):
        if self.game.teban == self.player.position:
            # print('捨てた本人')
            return False
        if self.player.is_riichi_completed:
            # print('リーチしている')
            return False
        if self.game.state != Const.DAHAI_STATE and self.game.state != Const.NOTICE2_STATE:
            # print('ステート異常')
            return False
        if pai not in pais:
            # print('鳴いた牌が含まれていない')
            return False
        if self.game.last_dahai != pai:
            # print('鳴いた牌が最後の打牌と不一致')
            return False
        if len(pais) != 3:
            # print('牌の数が3つじゃない')
            return False
        for i in range(3):
            if pais[i] != pai and pais[i] not in self.player.tehai:
                # print('手牌に含まれていない牌がある')
                return False
        if not pais[0] // 4 == pais[1] // 4 == pais[2] // 4:
            # print('同じじゃない', pais, pai, self.player.tehai)
            return False
        if len(set(pais)) != 3:
            # print('牌番号に同じものがある')
            return False

        return True

    def can_chi(self, pais, pai):
        if (self.game.teban + 1) % 4 != self.player.position:
            # print('次の手番じゃない')
            return False
        if self.player.is_riichi_completed:
            # print('リーチしている')
            return False
        if self.game.state != Const.DAHAI_STATE and self.game.state != Const.NOTICE2_STATE:
            # print('ステート異常')
            return False
        if pai not in pais:
            # print('鳴いた牌が含まれていない')
            return False
        if self.game.last_dahai != pai:
            # print('鳴いた牌が最後の打牌と不一致')
            return False
        if len(pais) != 3:
            # print('牌の数が3つじゃない')
            return False
        for i in range(3):
            if pais[i] != pai and pais[i] not in self.player.tehai:
                # print('手牌に含まれていない牌がある')
                return False
        pais.sort()
        if pais[2] // 4 - pais[1] // 4 != 1 or pais[1] // 4 - pais[0] // 4 != 1:
            # print('連続していない', pais, pai)
            return False
        if pais[0] >= 4 * 27:
            # print('字牌')
            return False
        if pais[0] // (4 * 9) != pais[2] // (4 * 9):
            # print('複数の種類の牌がある')
            return False
        if len(set(pais)) != 3:
            # print('牌番号に同じものがある')
            return False

        return True
