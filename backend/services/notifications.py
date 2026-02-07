"""
Synthia 4.2 - Notification Service

Sends WhatsApp (via Twilio) and Telegram messages
when agent pipelines complete or fail.
"""

import os
import json
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class NotificationService:
    """Send notifications via WhatsApp and Telegram."""

    def __init__(self):
        self.telegram_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
        self.telegram_api = f"https://api.telegram.org/bot{self.telegram_token}"
        self._recipients = self._load_recipients()
        self._twilio = None

    def _load_recipients(self) -> list[dict]:
        """Load notification recipients from env."""
        raw = os.getenv("NOTIFICATION_RECIPIENTS", "[]")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return []

    def _get_twilio(self):
        if self._twilio is None:
            from services.twilio_service import get_twilio_service
            self._twilio = get_twilio_service()
        return self._twilio

    async def send_telegram(
        self,
        chat_id: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> bool:
        """Send a Telegram message."""
        if not self.telegram_token:
            logger.warning("Telegram token not configured")
            return False

        try:
            async with httpx.AsyncClient() as client:
                if media_url:
                    resp = await client.post(
                        f"{self.telegram_api}/sendPhoto",
                        json={"chat_id": chat_id, "photo": media_url, "caption": message},
                    )
                else:
                    resp = await client.post(
                        f"{self.telegram_api}/sendMessage",
                        json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
                    )
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.error("Telegram send failed: %s", e)
            return False

    async def send_whatsapp(
        self,
        to: str,
        message: str,
        media_url: Optional[str] = None,
    ) -> bool:
        """Send a WhatsApp message via Twilio."""
        try:
            twilio = self._get_twilio()
            if not twilio.is_available:
                logger.warning("Twilio not available for WhatsApp")
                return False
            twilio.send_whatsapp(to, message, media_url)
            return True
        except Exception as e:
            logger.error("WhatsApp send failed: %s", e)
            return False

    async def notify_job_complete(self, job) -> None:
        """Notify all recipients that a pipeline job completed."""
        msg = (
            f"✅ *Synthia Pipeline Complete*\n\n"
            f"Job: `{job.job_id}`\n"
            f"Niche: {job.niche}\n"
            f"Page: {job.page_type}\n"
            f"Status: {job.status}\n"
            f"Steps completed: {len(job.results_per_step)}\n"
            f"Started: {job.started_at}\n"
            f"Finished: {job.completed_at}"
        )
        await self._broadcast(msg)

    async def notify_job_failed(self, job) -> None:
        """Notify all recipients that a pipeline job failed."""
        msg = (
            f"❌ *Synthia Pipeline Failed*\n\n"
            f"Job: `{job.job_id}`\n"
            f"Failed at: {job.current_agent}\n"
            f"Error: {job.error}\n"
            f"Started: {job.started_at}"
        )
        await self._broadcast(msg)

    async def _broadcast(self, message: str) -> None:
        """Send message to all configured recipients."""
        for recipient in self._recipients:
            rtype = recipient.get("type", "")
            rid = recipient.get("id", "")

            if rtype == "telegram" and rid:
                await self.send_telegram(rid, message)
            elif rtype == "whatsapp" and rid:
                await self.send_whatsapp(rid, message)
            else:
                logger.warning("Unknown recipient type: %s", rtype)


# Singleton
_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service


__all__ = ["NotificationService", "get_notification_service"]
