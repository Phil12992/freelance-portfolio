"""Asynchroner Monitoring & Alerting Bot.

Entwickelt von Philipp Brüll (phil.bruell@gmail.com).
Ueberwacht Ziel-URLs / APIs und sendet formatierte Warnungen an Telegram.
"""
from __future__ import annotations
import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("MonitorBot")

class SiteMonitor:
    def __init__(self, targets: list[str], telegram_token: str = "", chat_id: str = ""):
        self.targets = targets
        self.telegram_token = telegram_token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("TELEGRAM_CHAT_ID", "")
        self._last_status: dict[str, int] = {}

    async def check_endpoint(self, client: httpx.AsyncClient, url: str) -> tuple[str, int, float]:
        t0 = asyncio.get_event_loop().time()
        try:
            resp = await client.get(url, timeout=10.0, follow_redirects=True)
            elapsed_ms = (asyncio.get_event_loop().time() - t0) * 1000
            return url, resp.status_code, elapsed_ms
        except Exception as exc:
            elapsed_ms = (asyncio.get_event_loop().time() - t0) * 1000
            log.warning(f"Fehler bei {url}: {exc}")
            return url, 0, elapsed_ms

    async def send_alert(self, client: httpx.AsyncClient, message: str) -> None:
        if not self.telegram_token or not self.chat_id:
            log.info(f"[LOKALER ALERT]: {message}")
            return
        tg_url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
        payload = {"chat_id": self.chat_id, "text": message, "parse_mode": "Markdown"}
        try:
            await client.post(tg_url, json=payload, timeout=5.0)
        except Exception as exc:
            log.error(f"Telegram Versand fehlgeschlagen: {exc}")

    async def run_once(self) -> None:
        async with httpx.AsyncClient() as client:
            tasks = [self.check_endpoint(client, u) for u in self.targets]
            results = await asyncio.gather(*tasks)

            for url, status, latency in results:
                prev_status = self._last_status.get(url, 200)
                self._last_status[url] = status
                log.info(f"{url} -> HTTP {status} ({latency:.1f}ms)")

                # Alert bei Ausfall (HTTP != 200)
                if status != 200 and prev_status == 200:
                    alert_msg = f"🚨 *AUSFALL-ALARM:* `{url}` antwortet mit Code `{status}`! (Latenz: {latency:.0f}ms)"
                    await self.send_alert(client, alert_msg)
                elif status == 200 and prev_status != 200:
                    rec_msg = f"✅ *ENTWARNUNG:* `{url}` ist wieder online! (Latenz: {latency:.0f}ms)"
                    await self.send_alert(client, rec_msg)

async def main():
    targets = [
        "https://phil12992.github.io/freelance-portfolio/",
        "https://api.github.com",
    ]
    bot = SiteMonitor(targets)
    log.info("Starte SiteMonitor fuer %d Ziele...", len(targets))
    await bot.run_once()

if __name__ == "__main__":
    asyncio.run(main())
