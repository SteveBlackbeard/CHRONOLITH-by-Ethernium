#!/usr/bin/env python3
"""
notify_webhook.py — CHRONOLITH v5.1
===========================================
Sends automated notifications to Discord and/or Telegram when the chronolith
cycle detects critical events (ATTENTION_REQUIRED, security violations, etc.).

Configure webhook URLs in chronolith.json under the "notifications" key.
Zero external dependencies (uses only urllib from Python stdlib).

Google-style docstrings.
"""
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone


def _load_webhook_config(repo_root: Path) -> dict:
    """Loads webhook configuration from chronolith.json.

    Args:
        repo_root: The root path of the project.

    Returns:
        A dict with 'discord_url' and/or 'telegram_bot_token'/'telegram_chat_id'.
    """
    config_path = repo_root / "chronolith.json"
    if not config_path.exists():
        return {}
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        return config.get("notifications", {})
    except Exception:
        return {}


def send_discord(webhook_url: str, message: str, status: str = "ALERT") -> bool:
    """Sends a notification to a Discord channel via webhook.

    Args:
        webhook_url: The Discord webhook URL from channel settings.
        message: The notification text body.
        status: A status label (e.g., 'OK', 'ALERT', 'CRITICAL').

    Returns:
        True if the message was sent successfully, False otherwise.

    Example:
        >>> send_discord("https://discord.com/api/webhooks/...", "Parity error detected", "ALERT")
        True
    """
    emoji = {"OK": "✅", "ALERT": "⚠️", "CRITICAL": "🚨"}.get(status, "🔔")
    payload = {
        "username": "CHRONOLITH",
        "embeds": [{
            "title": f"{emoji} CHRONOLITH — {status}",
            "description": message,
            "color": 0xFF4400 if status == "CRITICAL" else 0xFFCC00 if status == "ALERT" else 0x00FFCC,
            "footer": {"text": f"Ethernium Hub · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}"},
        }]
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.URLError as e:
        print(f"  [!] Discord webhook failed: {e}")
        return False


def send_telegram(bot_token: str, chat_id: str, message: str, status: str = "ALERT") -> bool:
    """Sends a notification to a Telegram chat via bot.

    Args:
        bot_token: The Telegram bot token from @BotFather.
        chat_id: The target chat ID (personal, group, or channel).
        message: The notification text body (supports Markdown).
        status: A status label for emoji selection.

    Returns:
        True if the message was sent successfully, False otherwise.
    """
    emoji = {"OK": "✅", "ALERT": "⚠️", "CRITICAL": "🚨"}.get(status, "🔔")
    text = f"{emoji} *CHRONOLITH — {status}*\n\n{message}\n\n_Ethernium Hub_"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=10)
        return True
    except urllib.error.URLError as e:
        print(f"  [!] Telegram webhook failed: {e}")
        return False


def notify(repo_root: Path, message: str, status: str = "ALERT") -> dict:
    """Dispatches a notification to all configured channels.

    Reads webhook configuration automatically from chronolith.json.
    Gracefully skips channels that are not configured.

    Args:
        repo_root: The root path of the project.
        message: The notification text body.
        status: Severity level — 'OK', 'ALERT', or 'CRITICAL'.

    Returns:
        A dict with keys 'discord' and 'telegram', each True/False.

    Example:
        >>> notify(Path("."), "Secret key exposed in CHANGELOG.md", "CRITICAL")
        {'discord': True, 'telegram': False}
    """
    cfg = _load_webhook_config(repo_root)
    results = {"discord": False, "telegram": False}

    discord_url = cfg.get("discord_webhook_url", "")
    if discord_url:
        results["discord"] = send_discord(discord_url, message, status)
        print(f"  [{'✔' if results['discord'] else '!'}] Discord notification {'sent' if results['discord'] else 'failed'}.")
    else:
        print("  [~] Discord not configured (set notifications.discord_webhook_url in chronolith.json).")

    tg_token = cfg.get("telegram_bot_token", "")
    tg_chat = cfg.get("telegram_chat_id", "")
    if tg_token and tg_chat:
        results["telegram"] = send_telegram(tg_token, tg_chat, message, status)
        print(f"  [{'✔' if results['telegram'] else '!'}] Telegram notification {'sent' if results['telegram'] else 'failed'}.")
    else:
        print("  [~] Telegram not configured (set notifications.telegram_bot_token + telegram_chat_id).")

    return results


if __name__ == "__main__":
    # Quick test — reads config from current project root
    root = Path(__file__).parent.parent.parent
    print("[*] Testing notification channels...")
    notify(root, "This is a test notification from CHRONOLITH v5.1.", "ALERT")
