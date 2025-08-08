import pandas as pd
import numpy as np
from binance.client import Client
from binance.exceptions import BinanceAPIException
import logging
import time
from config import BINANCE_API_KEY, BINANCE_API_SECRET

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self):
        """Binance API istemcisini başlatır."""
        try:
            self.client = Client(BINANCE_API_KEY, BINANCE_API_SECRET)
            logger.info("Binance API bağlantısı başarılı.")
        except Exception as e:
            logger.error(f"Binance API bağlantısı başarısız: {e}")
            self.client = None

    def get_all_symbols(self):
        """Tüm kripto para çiftlerini getirir."""
        try:
            exchange_info = self.client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols'] if s['quoteAsset'] == 'USDT']
            return sorted(symbols)
        except BinanceAPIException as e:
            logger.error(f"Semboller alınırken hata oluştu: {e}")
            return []
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return []

    def get_klines(self, symbol, interval, limit=500):
        """Belirli bir sembol ve zaman aralığı için kline verilerini getirir."""
        try:
            klines = self.client.get_klines(symbol=symbol, interval=interval, limit=limit)
            
            # Verileri DataFrame'e dönüştür
            df = pd.DataFrame(klines, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Veri tiplerini dönüştür
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            numeric_columns = ['open', 'high', 'low', 'close', 'volume', 
                              'quote_asset_volume', 'taker_buy_base_asset_volume', 
                              'taker_buy_quote_asset_volume']
            
            df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric)
            
            return df
        except BinanceAPIException as e:
            logger.error(f"{symbol} için kline verileri alınırken hata oluştu: {e}")
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return pd.DataFrame()

    def get_ticker_prices(self, symbols=None):
        """Belirli sembollerin güncel fiyatlarını getirir."""
        try:
            if symbols:
                prices = self.client.get_all_tickers()
                filtered_prices = [price for price in prices if price['symbol'] in symbols]
                return filtered_prices
            else:
                return self.client.get_all_tickers()
        except BinanceAPIException as e:
            logger.error(f"Fiyat bilgileri alınırken hata oluştu: {e}")
            return []
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return []

    def get_account_info(self):
        """Hesap bilgilerini getirir."""
        try:
            return self.client.get_account()
        except BinanceAPIException as e:
            logger.error(f"Hesap bilgileri alınırken hata oluştu: {e}")
            return {}
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return {}

    def get_symbol_info(self, symbol):
        """Belirli bir sembol hakkında detaylı bilgi getirir."""
        try:
            return self.client.get_symbol_info(symbol)
        except BinanceAPIException as e:
            logger.error(f"{symbol} bilgileri alınırken hata oluştu: {e}")
            return {}
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return {}

    def get_historical_trades(self, symbol, limit=500):
        """Belirli bir sembol için geçmiş işlemleri getirir."""
        try:
            return self.client.get_historical_trades(symbol=symbol, limit=limit)
        except BinanceAPIException as e:
            logger.error(f"{symbol} için geçmiş işlemler alınırken hata oluştu: {e}")
            return []
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return []

    def get_top_symbols_by_volume(self, quote_asset='USDT', limit=10):
        """İşlem hacmine göre en yüksek sembolleri getirir."""
        try:
            # 24 saatlik istatistikleri al
            tickers = self.client.get_ticker()
            
            # USDT çiftlerini filtrele
            usdt_tickers = [t for t in tickers if t['symbol'].endswith(quote_asset)]
            
            # Hacme göre sırala
            sorted_tickers = sorted(usdt_tickers, key=lambda x: float(x['quoteVolume']), reverse=True)
            
            # İlk 'limit' kadar sembolü döndür
            return sorted_tickers[:limit]
        except BinanceAPIException as e:
            logger.error(f"Hacim bilgileri alınırken hata oluştu: {e}")
            return []
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return []

    def get_market_depth(self, symbol, limit=100):
        """Belirli bir sembol için emir defterini getirir."""
        try:
            return self.client.get_order_book(symbol=symbol, limit=limit)
        except BinanceAPIException as e:
            logger.error(f"{symbol} için emir defteri alınırken hata oluştu: {e}")
            return {}
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return {}