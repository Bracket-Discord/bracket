from typing import Any, Dict
from configs import settings


class DiscordOAuth2:
    AUTH_BASE_URL = "https://discord.com/api/oauth2/authorize"
    TOKEN_URL = "https://discord.com/api/oauth2/token"
    API_BASE_URL = "https://discord.com/api"
    REVOKE_URL = "https://discord.com/api/oauth2/token/revoke"
    SCOPES = ["identify", "email", "guilds"]

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, state: str) -> str:
        from urllib.parse import urlencode

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.SCOPES),
            "state": state,
            "prompt": "consent",
        }
        return f"{self.AUTH_BASE_URL}?{urlencode(params)}"

    async def fetch_token(self, code: str) -> Dict[str, Any]:
        import aiohttp

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        async with aiohttp.ClientSession() as session:
            async with session.post(self.TOKEN_URL, data=data, headers=headers) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def fetch_user(self, access_token: str) -> Dict[str, Any]:
        import aiohttp

        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.API_BASE_URL}/users/@me", headers=headers
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def fetch_guilds(self, access_token: str) -> Dict[str, Any]:
        import aiohttp

        headers = {"Authorization": f"Bearer {access_token}"}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.API_BASE_URL}/users/@me/guilds", headers=headers
            ) as resp:
                resp.raise_for_status()
                return await resp.json()


oauth2 = DiscordOAuth2(
    client_id=settings.discord.client_id,
    client_secret=settings.discord.client_secret,
    redirect_uri="http://localhost:8000/oauth/callback",
)
