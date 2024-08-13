from __future__ import annotations

from typing import TYPE_CHECKING

from .agari import Agari

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


# TODO decisionsはGameじゃなくてPlayerに持たせたほうが良い
class PlayerAction:
    def __init__(self, game: Game, player: Player):
        self.game = game
        self.player = player

    def start_game(self, position: int):
        self.player.position = position
        self.player.score = 25000

    def start_kyoku(self):
        self.player.tehai = []
        self.player.kawa = []
        self.player.huuro = []
        self.player.riichi_pai = None
        self.player.is_riichi_declared = False
        self.player.is_riichi_completed = False

    def open_dora(self):
        self.game.n_opened_dora += 1

    def tsumoho(self):
        agari = Agari(self.player, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_opened_dora:
                doras.append(self.game.dora[i])
                uradoras.append(self.game.dora[i + 5])
            else:
                doras.append(self.game.make_dummy(self.game.dora[i]))
                uradoras.append(self.game.make_dummy(self.game.dora[i + 5]))

        score_movements = agari.score_movements
        for player, score_movement in zip(self.game.players, score_movements):
            player.score += score_movement

        self.game.kyoutaku = 0
        if self.player.position == self.game.kyoku % 4:
            self.game.honba += 1
        else:
            self.game.honba = 0
        if self.player.position != self.game.kyoku % 4:
            self.game.kyoku += 1

        return {
            'tehai': self.player.tehai,
            'huuro': self.player.huuro,
            'yakus': yakus,
            'doras': doras,
            'uradoras': uradoras,
            'scores': [player.score for player in self.game.players],
            'score_movements': score_movements,
        }

    def tsumo(self, pai):
        self.player.tehai.append(pai)
        self.player.tehai.sort()
        self.game.last_tsumo = pai

    def ankan(self, pais):
        for i in pais:
            self.player.tehai.pop(self.player.tehai.index(i))
        self.player.huuro.append({
            'type': 'ankan',
            'pais': pais,
            'who': (self.game.teban - self.player.position) % 4,
            'from_who': (self.game.teban - self.player.position) % 4
        })
        self.game.n_kan += 1
        self.game.pc += 10

    def riichi_declare(self):
        self.player.is_riichi_declared = True
        self.player.riichi_pc = self.game.pc

    def dahai(self, pai):
        self.player.tehai.pop(self.player.tehai.index(pai))
        self.player.kawa.append(pai)
        self.game.last_dahai = pai
        self.game.last_teban = self.game.teban
        self.game.pc += 1

    def riichi_complete(self):
        self.player.score -= 1000
        self.player.is_riichi_completed = True
        self.game.kyoutaku += 1

    def riichi(self, pai):
        if self.player.is_riichi_declared and self.player.riichi_pai not in self.player.kawa:
            self.player.riichi_pai = pai

    def ronho(self):
        agari = Agari(self.player, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_opened_dora:
                doras.append(self.game.dora[i])
                if self.player.is_riichi_completed:
                    uradoras.append(self.game.dora[i + 5])
                else:
                    uradoras.append(self.game.make_dummy(self.game.dora[i + 5]))

            else:
                doras.append(self.game.make_dummy(self.game.dora[i]))
                uradoras.append(self.game.make_dummy(self.game.dora[i + 5]))

        score_movements = agari.score_movements
        for player, score_movement in zip(self.game.players, score_movements):
            player.score += score_movement

        self.game.kyoutaku = 0
        if self.player.position == self.game.kyoku % 4:
            self.game.honba += 1
        else:
            self.game.honba = 0
        if self.player.position != self.game.kyoku % 4:
            self.game.kyoku += 1

        return {
            'tehai': self.player.tehai,
            'huuro': self.player.huuro,
            'yakus': yakus,
            'doras': doras,
            'uradoras': uradoras,
            'scores': [player.score for player in self.game.players],
            'score_movements': score_movements,
        }

    def pon(self, pais, pai):
        for i in pais:
            if i != pai:
                self.player.tehai.pop(self.player.tehai.index(i))
        self.player.huuro.append({
            'type': 'pon',
            'pais': pais,
            'pai': pai,
            'who': (self.game.teban - self.player.position) % 4,
            'from_who': (self.game.last_teban - self.player.position) % 4
        })
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.player.position
        self.game.pc += 10

    def chi(self, pais, pai):
        for i in pais:
            if i != pai:
                self.player.tehai.pop(self.player.tehai.index(i))
        self.player.huuro.append({
            'type': 'chi',
            'pais': pais,
            'pai': pai,
            'who': (self.game.teban - self.player.position) % 4,
            'from_who': (self.game.last_teban - self.player.position) % 4
        })
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.player.position
        self.game.pc += 10

    def cancel(self):
        if self.game.teban == self.player.position:
            self.game.ankan_decisions[self.player.position] = None
            self.game.riichi_decisions[self.player.position] = False

        self.game.ronho_decisions[self.player.position] = False
        self.game.minkan_decisions[self.player.position] = [None, None]
        self.game.pon_decisions[self.player.position] = [None, None]
        self.game.chi_decisions[self.player.position] = [None, None]

    def reset_actions(self):
        self.player.actions = []

    def player_info(self, is_myself: bool):
        tehai = self.player.tehai if is_myself else self.game.make_dummies(self.player.tehai)
        kawa = self.player.kawa if is_myself else self.game.make_dummies(self.player.kawa)
        zikaze = '東南西北'[(self.player.position - self.game.kyoku) % 4]

        return {
            'tehai': tehai,
            'kawa': kawa,
            'huuro': self.player.huuro,
            'riichi_pai': self.player.riichi_pai,
            'score': self.player.score,
            'zikaze': zikaze,
            'is_riichi_completed': self.player.is_riichi_completed
        }
