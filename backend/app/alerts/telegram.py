import httpx
import logging
from typing import Optional

class TelegramDeliverer:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = bool(bot_token and chat_id)

    async def send_message(self, text: str) -> bool:
        if not self.enabled:
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json={
                    "chat_id": self.chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                })
                return resp.status_code == 200
        except Exception as e:
            logging.error(f"Telegram delivery failed: {e}")
            return False
