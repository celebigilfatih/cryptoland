import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Binance API anahtarları
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")

# Varsayılan semboller
DEFAULT_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "DOGEUSDT",
    "XRPUSDT", "DOTUSDT", "LTCUSDT", "LINKUSDT", "SOLUSDT"
]

# Zaman aralıkları
INTERVALS = {
    "1 dakika": "1m",
    "3 dakika": "3m",
    "5 dakika": "5m",
    "15 dakika": "15m",
    "30 dakika": "30m",
    "1 saat": "1h",
    "2 saat": "2h",
    "4 saat": "4h",
    "6 saat": "6h",
    "8 saat": "8h",
    "12 saat": "12h",
    "1 gün": "1d",
    "3 gün": "3d",
    "1 hafta": "1w",
    "1 ay": "1M"
}

# İndikatör parametreleri
INDICATOR_PARAMS = {
    "RSI": {
        "period": 14,
        "overbought": 70,
        "oversold": 30
    },
    "MACD": {
        "fast_period": 12,
        "slow_period": 26,
        "signal_period": 9
    },
    "Bollinger": {
        "window": 20,
        "window_dev": 2
    },
    "EMA": {
        "short_period": 9,
        "medium_period": 21,
        "long_period": 50
    }
}

# Uygulama ayarları
APP_TITLE = "Cryptoland - Kripto Trading Sinyal Uygulaması"
APP_ICON = "📈"
THEME_COLOR = "#4CAF50"  # Modern yeşil tema rengi
SECONDARY_COLOR = "#2E7D32"  # Koyu yeşil
BACKGROUND_COLOR = "#1E1E1E"  # Koyu arka plan
TEXT_COLOR = "#FFFFFF"  # Beyaz metin
CARD_BACKGROUND = "#2D2D2D"  # Kart arka plan rengi
ACCENT_COLOR = "#81C784"  # Vurgu rengi