from .agari import Agari


# TODO decisionsはGameじゃなくてPlayerに持たせたほうが良い
class PlayerAction:
    def open_dora(self):
        self.game.n_dora += 1

    def tsumoho(self):
        agari = Agari(self, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_dora:
                doras.append(self.game.dora[i])
                uradoras.append(self.game.dora[i + 5])
            else:
                doras.append(self.game.make_dummy(self.game.dora[i]))
                uradoras.append(self.game.make_dummy(self.game.dora[i + 5]))

        score_movements = agari.score_movements
        for player, score_movement in zip(self.game.players, score_movements):
            player.score += score_movement

        self.game.kyoutaku = 0
        if self.position == self.game.kyoku % 4:
            self.game.honba += 1
        else:
            self.game.honba = 0
        if self.position != self.game.kyoku % 4:
            self.game.kyoku += 1

        return {
            'tehai': self.tehai,
            'huuro': self.huuro,
            'yakus': yakus,
            'doras': doras,
            'uradoras': uradoras,
            'scores': [player.score for player in self.game.players],
            'score_movements': score_movements,
        }

    def tsumo(self, pai):
        self.tehai.append(pai)
        self.tehai.sort()
        self.game.last_tsumo = pai

    def ankan(self, pais):
        for i in pais:
            self.tehai.pop(self.tehai.index(i))
        self.huuro.append({'type': 'ankan', 'pais': pais, 'who': (self.game.teban - self.position) % 4,
                          'from_who': (self.game.teban - self.position) % 4})
        self.game.n_kan += 1
        self.game.pc += 10

    def riichi_declare(self):
        self.is_riichi_declared = True
        self.riichi_pc = self.game.pc

    def dahai(self, pai):
        self.tehai.pop(self.tehai.index(pai))
        self.kawa.append(pai)
        self.game.last_dahai = pai
        self.game.last_teban = self.game.teban
        self.game.pc += 1

    def riichi_complete(self):
        self.score -= 1000
        self.is_riichi_completed = True
        self.game.kyoutaku += 1

    def riichi(self, pai):
        if self.is_riichi_declared and self.riichi_pai not in self.kawa:
            self.riichi_pai = pai

    def ronho(self):
        agari = Agari(self, self.game)
        yakus = []
        for i in range(len(Agari.YAKU)):
            if agari.yaku[i] > 0:
                yakus.append({'name': Agari.YAKU[i], 'han': agari.yaku[i]})

        doras = []
        uradoras = []
        for i in range(5):
            if i < self.game.n_dora:
                doras.append(self.game.dora[i])
                if self.is_riichi_completed:
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
        if self.position == self.game.kyoku % 4:
            self.game.honba += 1
        else:
            self.game.honba = 0
        if self.position != self.game.kyoku % 4:
            self.game.kyoku += 1

        return {
            'tehai': self.tehai,
            'huuro': self.huuro,
            'yakus': yakus,
            'doras': doras,
            'uradoras': uradoras,
            'scores': [player.score for player in self.game.players],
            'score_movements': score_movements,
        }

    def pon(self, pais, pai):
        for i in pais:
            if i != pai:
                self.tehai.pop(self.tehai.index(i))
        self.huuro.append({'type': 'pon', 'pais': pais, 'pai': pai, 'who': (self.game.teban - self.position) % 4,
                          'from_who': (self.game.last_teban - self.position) % 4})
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.position
        self.game.pc += 10

    def chi(self, pais, pai):
        for i in pais:
            if i != pai:
                self.tehai.pop(self.tehai.index(i))
        self.huuro.append({'type': 'chi', 'pais': pais, 'pai': pai, 'who': (self.game.teban - self.position) % 4,
                          'from_who': (self.game.last_teban - self.position) % 4})
        self.game.players[self.game.last_teban].kawa.pop(
            self.game.players[self.game.last_teban].kawa.index(pai)
        )
        self.game.teban = self.position
        self.game.pc += 10

    def cancel(self):
        if self.game.teban == self.position:
            self.game.ankan_decisions[self.position] = None
            self.game.riichi_decisions[self.position] = False

        self.game.ronho_decisions[self.position] = False
        self.game.minkan_decisions[self.position] = [None, None]
        self.game.pon_decisions[self.position] = [None, None]
        self.game.chi_decisions[self.position] = [None, None]

    def reset_actions(self):
        self.actions = []

    def player_info(self, is_myself: bool):
        tehai = self.tehai if is_myself else self.game.make_dummies(self.tehai)
        kawa = self.kawa if is_myself else self.game.make_dummies(self.kawa)
        zikaze = '東南西北'[(self.position - self.game.kyoku) % 4]

        return {
            'tehai': tehai,
            'kawa': kawa,
            'huuro': self.huuro,
            'riichi_pai': self.riichi_pai,
            'score': self.score,
            'zikaze': zikaze,
            'is_riichi_completed': self.is_riichi_completed
        }

    def game_info(self):
        dora = self.game.dora[:self.game.n_dora] + self.game.make_dummies(self.game.dora[self.game.n_dora:5])
        n_yama = len(self.game.yama)

        return {
            'kyoku': self.game.kyoku,
            'honba': self.game.honba,
            'kyoutaku': self.game.kyoutaku,
            'dora': dora,
            'n_yama': n_yama,
        }
