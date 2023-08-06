from nextcord.gateway import DiscordWebSocket

class SpaceShuttle(DiscordWebSocket):
    @classmethod
    async def from_client(cls, client, **kwargs):
        client.earth.ready_timer.start()
        return await super().from_client(client, **kwargs)
    
    async def send_as_json(self, data):
        self._takeoff('socket_send', data)
        await super().send_as_json(data)