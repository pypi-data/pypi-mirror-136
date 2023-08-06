import time
from aiohttp import ClientSession

from nextcord.http import HTTPClient, Route
from nextcord.errors import HTTPException, LoginFailure

from .dawn import Earth

class Meteor:
    def __init__(self, *args, **kwargs):
        self._pitch: Pitch = kwargs.pop('pitch')
        self._session = ClientSession(*args, **kwargs)
        self.prepare_request_method()
        
    def __getattr__(self, name):
        return getattr(self._session, name)
    
    def prepare_request_method(self):
        _old_request = self._session._request
        async def _request(s, *args, **kwargs):
            start = time.monotonic()
            try:
                ret = await _old_request(s, *args, **kwargs)
            except Exception as e:
                await self._pitch.earth.http_request_error(*args, kwargs, exc=e)
                raise
            else:
                end = time.monotonic()
                dur = end - start
                await self._pitch.earth.http_request(*args, kwargs, ret=ret, dur=dur)
                return ret
        self._session._request = _request
        
class Pitch(HTTPClient):
    session_cls: Meteor
    earth: Earth
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from . import __version__ # circular import
        self.user_agent += f' nextcord-ext-space/{__version__}'
        
    @classmethod
    def from_http_client(cls, http_client: HTTPClient, session_cls: Meteor, earth: Earth):
        old = http_client
        self = cls(
            old.connector,
            proxy=old.proxy,
            proxy_auth=old.proxy_auth,
            loop=old.loop,
            unsync_clock=not old.use_clock,
        )
        self.session_cls = session_cls
        self.earth = earth
        return self
    
    def recreate(self):
        if self._HTTPClient__session.closed:
            self._HTTPClient__session = self.session_cls(connector=self.connector, pitch=self)
            
    async def static_login(self, token, *, bot):
        print(dir(self))
        # Necessary to get aiohttp to stop complaining about session creation
        self._HTTPClient__session = self.session_cls(connector=self.connector, pitch=self)
        print(self._HTTPClient__session)
        old_token, old_bot = self.token, self.bot_token
        self._token(token, bot=bot)
        
        try:
            print(self._HTTPClient__session)
            data = await self.request(Route('GET', '/users/@me'))
        except HTTPException as exc:
            self._token(old_token, bot=old_bot)
            if exc.response.status == 401:
                raise LoginFailure('Invalid token has been provided.') from exc
            raise
        
        return data