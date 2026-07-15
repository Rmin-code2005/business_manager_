import httpx

from django.conf import settings

class NerkhClient:
    def __init__(self):
        self.base_url = settings.NERKH_BASE_URL
        self.api_key = settings.NERKH_ACCESS_TOKEN

    @property
    def headers(self):
        headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.NERKH_ACCESS_TOKEN}",
        }

        return headers

    async def get(self, endpoint: str, params: dict | None = None):
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{self.base_url}{endpoint}",
                headers=self.headers,
                params=params,
            )

            response.raise_for_status()

            return response.json()