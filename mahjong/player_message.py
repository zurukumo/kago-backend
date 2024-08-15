from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from .game import Game
    from .player import Player


class PlayerMessage:
    game: Game
    player: Player

    def __init__(self, game: Game, player: Player):
        self.game = game
        self.player = player

    def start_kyoku_message(self) -> None:
        self.player.actions.append({
            'type': 'start_kyoku_message',
            'body': {
                'game_info': self.game.action.game_info(),
                'players_info': [player.action.player_info(i == self.player.position) for i, player in self.player.prange()]
            }
        })

    def tsumoho_message(self, tsumoho: Dict[str, Any]) -> None:
        tsumoho = tsumoho.copy()
        tsumoho['scores'] = [tsumoho['scores'][i] for i, _ in self.player.prange()]
        tsumoho['score_movements'] = [tsumoho['score_movements'][i] for i, _ in self.player.prange()]

        self.player.actions.append({
            'type': 'tsumoho_message',
            'body': tsumoho
        })

    def tsumo_message(self, pai: int) -> None:
        body = {
            'who': (self.game.teban - self.player.position) % 4,
            'n_yama': len(self.game.yama),
        }

        if self.game.teban == self.player.position:
            body['pai'] = pai
        else:
            body['dummy'] = self.game.make_dummy(pai)

        self.player.actions.append({
            'type': 'tsumo_message',
            'body': body
        })

    def dahai_message(self, pai: int) -> None:
        self.player.actions.append({
            'type': 'dahai_message',
            'body': {
                'pai': pai,
                'dummy': self.game.make_dummy(pai),
                'who': (self.game.teban - self.player.position) % 4
            }
        })

    def riichi_complete_message(self) -> None:
        self.player.actions.append({
            'type': 'riichi_complete_message',
            'body': {
                'who': (self.game.teban - self.player.position) % 4,
                'score': self.game.players[self.game.teban].score,
                'is_riichi_completed': self.game.players[self.game.teban].is_riichi_completed
            }
        })

    def riichi_bend_message(self, pai: int) -> None:
        self.player.actions.append({
            'type': 'riichi_bend_message',
            'body': {
                'who': (self.game.teban - self.player.position) % 4,
                'pai': pai,
                'voice': bool(not self.game.players[self.game.teban].is_riichi_completed)
            }
        })

    def ankan_message(self, pais: List[int]) -> None:
        self.player.actions.append({
            'type': 'ankan_message',
            'body': {
                'pais': pais,
                'dummies': self.game.make_dummies(pais),
                'who': (self.game.teban - self.player.position) % 4,
                'from_who': (self.game.teban - self.player.position) % 4
            }
        })

    def ronho_message(self, ronho: Dict[str, Any]) -> None:
        ronho = ronho.copy()
        ronho['scores'] = [ronho['scores'][i] for i, _ in self.player.prange()]
        ronho['score_movements'] = [ronho['score_movements'][i] for i, _ in self.player.prange()]

        self.player.actions.append({
            'type': 'ronho_message',
            'body': ronho
        })

    def pon_message(self, pais: List[int], pai: int) -> None:
        if self.game.last_teban is None:
            raise ValueError('last_teban is None')

        self.player.actions.append({
            'type': 'pon_message',
            'body': {
                'pai': pai,
                'pais': pais,
                'dummies': self.game.make_dummies(pais),
                'who': (self.game.teban - self.player.position) % 4,
                'from_who': (self.game.last_teban - self.player.position) % 4
            }
        })

    def chi_message(self, pais: List[int], pai: int) -> None:
        if self.game.last_teban is None:
            raise ValueError('last_teban is None')

        self.player.actions.append({
            'type': 'chi_message',
            'body': {
                'pai': pai,
                'pais': pais,
                'dummies': self.game.make_dummies(pais),
                'who': (self.game.teban - self.player.position) % 4,
                'from_who': (self.game.last_teban - self.player.position) % 4
            }
        })

    def open_dora_message(self) -> None:
        pai = self.game.dora[self.game.n_opened_dora - 1]
        self.player.actions.append({
            'type': 'open_dora_message',
            'body': {
                'pai': pai,
                'dummy': self.game.make_dummy(pai),
                'n_yama': len(self.game.yama)
            }
        })

    # TODO テンパイではリーチ棒情報が出ない
    def ryukyoku_message(self, ryukyoku: Dict[str, Any]) -> None:
        self.player.actions.append({
            'type': 'ryukyoku_message',
            'body': {
                'scores': [ryukyoku['scores'][i % 4] for i in range(self.player.position, self.player.position + 4)],
                'score_movements': [ryukyoku['score_movements'][i % 4] for i in range(self.player.position, self.player.position + 4)]
            }
        })

    # TODO トップの人にリーチ棒を
    def syukyoku_message(self) -> None:
        scores = [player.score for player in self.game.players]
        order_scores = sorted(scores, reverse=True)
        ranks = [order_scores.index(scores[i]) + 1 for i in range(4)]

        self.player.actions.append({
            'type': 'syukyoku_message',
            'body': {
                'scores': [scores[i % 4] for i in range(self.player.position, self.player.position + 4)],
                'ranks': [ranks[i % 4] for i in range(self.player.position, self.player.position + 4)]
            }
        })

    # 通知1(ツモ和/リーチ/暗槓/加槓)
    def tsumoho_notice_message(self) -> None:
        if self.player.judge.can_tsumoho():
            self.player.actions.append({'type': 'tsumoho_notice_message'})
        else:
            self.game.tsumoho_decisions[self.player.position] = False

    def riichi_notice_message(self) -> None:
        for i in self.player.tehai:
            if self.player.judge.can_riichi_declare(i):
                self.player.actions.append({
                    'type': 'riichi_notice_message',
                })
                break

    def riichi_declare_notice_message(self) -> None:
        body = []

        for i in self.player.tehai:
            if self.player.judge.can_riichi_declare(i):
                body.append({
                    'pai': i,
                })

        if len(body) != 0:
            self.player.actions.append({
                'type': 'riichi_declare_notice_message',
                'body': body
            })

    def ankan_notice_message(self) -> None:
        body = []

        for i in range(34):
            if self.player.judge.can_ankan([i * 4 + j for j in range(4)]):
                body.append({
                    'pais': [i * 4 + j for j in range(4)],
                    'dummies': self.game.make_dummies([i * 4 + j for j in range(4)])
                })

        if len(body) == 0:
            self.game.ankan_decisions[self.player.position] = None
        else:
            self.player.actions.append({
                'type': 'ankan_notice_message',
                'body': body
            })

    # 通知2(ロン和/明槓/ポン/チー)
    def ronho_notice_message(self) -> None:
        if self.player.judge.can_ronho():
            self.player.actions.append({'type': 'ronho_notice_message'})
        else:
            self.game.ronho_decisions[self.player.position] = False

    def pon_notice_message(self) -> None:
        body = []

        if self.game.last_teban is None:
            raise ValueError('last_teban is None')
        if self.game.last_dahai is None:
            raise ValueError('last_dahai is None')

        done = [[0] * 2 for _ in range(34)]
        aka = [16, 52, 88]
        for i, j in combinations(self.player.tehai, 2):
            if not i // 4 == j // 4 == self.game.last_dahai // 4:
                continue

            if i in aka or j in aka or self.game.last_dahai in aka:
                if done[i // 4][1] == 0:
                    pais = [self.game.last_dahai, i, j]
                    if self.player.judge.can_pon(pais, self.game.last_dahai):
                        body.append({
                            'pai': self.game.last_dahai,
                            'pais': pais,
                            'dummies': self.game.make_dummies(pais),
                            'from_who': (self.game.last_teban - self.player.position) % 4
                        })
                        done[i // 4][1] = 1
            else:
                if done[i // 4][0] == 0:
                    pais = [self.game.last_dahai, i, j]
                    if self.player.judge.can_pon(pais, self.game.last_dahai):
                        body.append({
                            'pai': self.game.last_dahai,
                            'pais': pais,
                            'dummies': self.game.make_dummies(pais),
                            'from_who': (self.game.last_teban - self.player.position) % 4
                        })
                        done[i // 4][0] = 1

        if len(body) == 0:
            self.game.pon_decisions[self.player.position] = (None, None)
        else:
            self.player.actions.append({
                'type': 'pon_notice_message',
                'body': body
            })

    def chi_notice_message(self) -> None:
        body = []

        if self.game.last_teban is None:
            raise ValueError('last_teban is None')
        if self.game.last_dahai is None:
            raise ValueError('last_dahai is None')

        tmp = set(map(self.game.make_simple, self.player.tehai))
        tehai = []
        for i in self.player.tehai:
            if self.game.make_simple(i) in tmp:
                tehai.append(i)
                tmp.remove(self.game.make_simple(i))

        for i, j in combinations(tehai, 2):
            pais = [self.game.last_dahai, i, j]
            if self.player.judge.can_chi(pais, self.game.last_dahai):
                body.append({
                    'pai': self.game.last_dahai,
                    'pais': pais,
                    'dummies': self.game.make_dummies(pais),
                    'from_who': (self.game.last_teban - self.player.position) % 4
                })

        if len(body) == 0:
            self.game.chi_decisions[self.player.position] = (None, None)
        else:
            self.player.actions.append({
                'type': 'chi_notice_message',
                'body': body
            })
