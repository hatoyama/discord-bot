import json
import os
from pathlib import Path
from typing import Optional

CONFIG_FILE = Path(__file__).parent / "config.json"


def get_weather_channel_id() -> Optional[int]:
    """設定ファイルまたは環境変数から天気通知先チャンネルIDを取得する"""
    # 1. config.json を確認
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                channel_id = data.get("weather_channel_id")
                if channel_id:
                    return int(channel_id)
        except Exception:
            pass

    # 2. 環境変数 DISCORD_CHANNEL_ID を確認
    env_channel_id = os.getenv("DISCORD_CHANNEL_ID")
    if env_channel_id and env_channel_id.strip():
        try:
            return int(env_channel_id.strip())
        except ValueError:
            return None

    return None


def set_weather_channel_id(channel_id: int) -> bool:
    """通知先チャンネルIDを config.json に保存する"""
    data = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    data["weather_channel_id"] = channel_id

    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False
