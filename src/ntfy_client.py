import httpx
from typing import Optional
from config import settings

async def send_notification(topic: str, title: str, message: str, priority: int = 3) -> bool:
    url = f"{settings.ntfy_base_url}/{topic}"
    headers = {"Title": title, "Priority": str(priority)}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(url, headers=headers, content=message)
            return resp.status_code < 400
    except:
        return False
