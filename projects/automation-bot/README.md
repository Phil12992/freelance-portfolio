# 🤖 Asynchroner Monitoring- & Alert-Bot

Produktionsfertiger Python-Service zur 24/7-Überwachung von Webseiten und APIs.

## Funktionen
- **Asynchron & Schnell:** Parallele Überprüfung mehrerer Endpunkte via `httpx` & `asyncio`.
- **Zustandsüberwachung:** Erkennt Ausfälle und Wiederherstellungen ohne Spam-Dopplungen.
- **Telegram Webhook:** Versendet strukturierte Benachrichtigungen direkt aufs Smartphone.
- **Autor:** Philipp Brüll ([phil.bruell@gmail.com](mailto:phil.bruell@gmail.com))

## Schnellstart
```bash
pip install -r requirements.txt
python monitor_bot.py
```
