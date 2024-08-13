import json

from channels.generic.websocket import AsyncWebsocketConsumer

from .game import Game


class MahjongConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        await self.close()

    async def send(self, data):
        data = json.dumps(data)
        print('send:', data)

        await super().send(text_data=data)

    async def receive(self, text_data):
        data = json.loads(text_data)
        data_type = data['type']
        print('receive:', data)

        if data_type == 'start_game':
            self.game = Game()
            self.game.action.start_game(data['mode'])
            self.player = self.game.find_player(0)
            await self.next()

        if data_type == 'tsumoho':
            self.game.action.tsumoho(self.player)
            await self.next()

        if data_type == 'dahai':
            self.game.action.dahai(data['body']['pai'], self.player)
            await self.next()

        if data_type == 'riichi_declare':
            self.game.action.riichi_declare(self.player)
            await self.next()

        if data_type == 'ankan':
            self.game.action.ankan(data['body']['pais'], self.player)
            await self.next()

        if data_type == 'ronho':
            self.game.action.ronho(self.player)
            await self.next()

        if data_type == 'pon':
            self.game.action.pon(data['body']['pais'], data['body']['pai'], self.player)
            await self.next()

        if data_type == 'chi':
            self.game.action.chi(data['body']['pais'], data['body']['pai'], self.player)
            await self.next()

        if data_type == 'next_kyoku':
            self.game.action.next_kyoku()
            await self.next()

        if data_type == 'cancel':
            self.player.action.cancel()
            await self.next()

        if data_type == 'next':
            await self.next()

    async def next(self):
        while self.game.routine.next():
            if len(self.player.actions) != 0:
                await self.send(self.player.actions)
                break
