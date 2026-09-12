from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Optional
import aiohttp
import discord

# 日本標準時 (JST = UTC+9)
JST = timezone(timedelta(hours=9))

# 東京の緯度・経度
TOKYO_LATITUDE = 35.6895
TOKYO_LONGITUDE = 139.6917

# WMO天気コードのマッピング: (名称, 絵文字, カラーコード)
WMO_WEATHER_MAP: Dict[int, tuple[str, str, int]] = {
    0: ("快晴", "☀️", 0xF59E0B),
    1: ("晴れ", "🌤️", 0xFBBF24),
    2: ("一部曇り", "⛅", 0x9CA3AF),
    3: ("曇り", "☁️", 0x6B7280),
    45: ("霧", "🌫️", 0x9CA3AF),
    48: ("着氷性の霧", "🌫️", 0x9CA3AF),
    51: ("薄い霧雨", "🌧️", 0x60A5FA),
    53: ("霧雨", "🌧️", 0x60A5FA),
    55: ("濃い霧雨", "🌧️", 0x60A5FA),
    56: ("着氷性の霧雨（弱）", "🧊", 0x38BDF8),
    57: ("着氷性の霧雨（強）", "🧊", 0x38BDF8),
    61: ("小雨", "🌧️", 0x3B82F6),
    63: ("雨", "🌧️", 0x2563EB),
    65: ("強い雨", "🌧️", 0x1D4ED8),
    66: ("着氷性の雨（弱）", "🧊", 0x38BDF8),
    67: ("着氷性の雨（強）", "🧊", 0x38BDF8),
    71: ("小雪", "❄️", 0xE0F2FE),
    73: ("雪", "❄️", 0xBAE6FD),
    75: ("大雪", "❄️", 0x7DD3FC),
    77: ("霧雪", "❄️", 0xE0F2FE),
    80: ("にわか雨（弱）", "🌦️", 0x3B82F6),
    81: ("にわか雨", "🌦️", 0x2563EB),
    82: ("激しいにわか雨", "⛈️", 0x1D4ED8),
    85: ("にわか雪（弱）", "🌨️", 0xBAE6FD),
    86: ("にわか雪（強）", "🌨️", 0x7DD3FC),
    95: ("雷雨", "⛈️", 0x7C3AED),
    96: ("雷雨と雹（弱）", "⛈️", 0x5B21B6),
    99: ("雷雨と雹（強）", "⛈️", 0x4C1D95),
}


def get_weather_info_from_code(code: int) -> tuple[str, str, int]:
    """WMOコードから (天気名, 絵文字, 色) を取得する"""
    return WMO_WEATHER_MAP.get(code, ("不明", "❓", 0x6B7280))


async def fetch_tokyo_weather() -> Optional[Dict[str, Any]]:
    """Open-Meteo API から東京の今日の天気予報を取得する"""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={TOKYO_LATITUDE}&longitude={TOKYO_LONGITUDE}"
        f"&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
        f"&timezone=Asia%2FTokyo&forecast_days=1"
    )

    headers = {"User-Agent": "DiscordBot-WeatherClient/1.0"}

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    return None
                data = await response.json()
                return data
    except Exception as e:
        print(f"天気情報取得エラー: {e}")
        return None


def create_weather_embed(weather_data: Dict[str, Any], title_prefix: str = "東京の今日の天気予報") -> discord.Embed:
    """天気データから Discord 用の Embed を作成する"""
    daily = weather_data.get("daily", {})

    target_date = daily.get("time", [""])[0]
    weather_code = daily.get("weather_code", [-1])[0]
    temp_max = daily.get("temperature_2m_max", [None])[0]
    temp_min = daily.get("temperature_2m_min", [None])[0]
    precip_prob = daily.get("precipitation_probability_max", [None])[0]

    weather_name, emoji, color = get_weather_info_from_code(weather_code)

    now_jst = datetime.now(JST)
    date_display = target_date if target_date else now_jst.strftime("%Y-%m-%d")

    embed = discord.Embed(
        title=f"{emoji} {title_prefix} ({date_display})",
        description="おはようございます！今日の東京の天気予報をお届けします。",
        color=color,
        timestamp=now_jst
    )

    embed.add_field(name="天気", value=f"{emoji} **{weather_name}**", inline=True)

    temp_text = []
    if temp_max is not None:
        temp_text.append(f"最高: **{temp_max}℃**")
    if temp_min is not None:
        temp_text.append(f"最低: **{temp_min}℃**")
    embed.add_field(name="気温", value=" / ".join(temp_text) if temp_text else "情報なし", inline=True)

    precip_text = f"**{precip_prob}%**" if precip_prob is not None else "情報なし"
    embed.add_field(name="降水確率", value=precip_text, inline=True)

    # 降水確率に応じた傘のアドバイス
    if precip_prob is not None:
        if precip_prob >= 60:
            advice = "☔ 今日は雨が降る可能性が高いです。傘を忘れずにお持ちください！"
        elif precip_prob >= 30:
            advice = "🌂 雨が降る可能性があります。折りたたみ傘があると安心です。"
        else:
            advice = "☀️ 傘の心配はほとんどなさそうです。良い一日をお過ごしください！"
        embed.add_field(name="お出かけアドバイス", value=advice, inline=False)

    embed.set_footer(text="データ提供: Open-Meteo")
    return embed
