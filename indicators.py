import pandas as pd
import numpy as np
import ta
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
import logging
from typing import Tuple, List, Dict, Optional

def calculate_vwema(df, period):
    """
    Volume Weighted Exponential Moving Average hesaplar.
    
    Args:
        df (pandas.DataFrame): OHLCV verileri içeren DataFrame
        period (int): VWEMA periyodu
    
    Returns:
        pandas.Series: Hesaplanan VWEMA değerleri
    """
    try:
        # Hacim ağırlıklı fiyat hesapla
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vw_price = typical_price * df['volume']
        
        # EMA hesapla
        multiplier = 2 / (period + 1)
        vwema = pd.Series(index=df.index)
        
        # İlk değeri SMA olarak ayarla
        vwema.iloc[:period] = vw_price.iloc[:period].sum() / df['volume'].iloc[:period].sum()
        
        # Kalan değerleri EMA formülü ile hesapla
        for i in range(period, len(df)):
            vwema.iloc[i] = (vw_price.iloc[i] * multiplier) + (vwema.iloc[i-1] * (1 - multiplier))
        
        return vwema
    except Exception as e:
        logger.error(f"VWEMA hesaplanırken hata oluştu: {e}")
        return pd.Series(np.nan, index=df.index)

def find_fair_value_gaps(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Fair Value Gap (FVG) bölgelerini tespit eder.
    
    FVG, piyasada hızlı bir fiyat hareketi sonucu oluşan ve daha sonra
    fiyatın geri dönüp doldurma eğiliminde olduğu boşluklardır.
    
    Args:
        df (pandas.DataFrame): OHLCV verileri içeren DataFrame
    
    Returns:
        Tuple[pandas.DataFrame, pandas.DataFrame]: Bullish ve Bearish FVG'leri içeren DataFrames
    """
    try:
        # Boş DataFrames oluştur
        bullish_fvg = pd.DataFrame(columns=['timestamp', 'fvg_low', 'fvg_high', 'filled'])
        bearish_fvg = pd.DataFrame(columns=['timestamp', 'fvg_low', 'fvg_high', 'filled'])
        
        # En az 3 mum gerekli
        if len(df) < 3:
            return bullish_fvg, bearish_fvg
        
        # FVG'leri bul
        for i in range(1, len(df) - 1):
            # Bullish FVG: Önceki mumun yüksek değeri, sonraki mumun düşük değerinden küçükse
            if df['high'].iloc[i-1] < df['low'].iloc[i+1]:
                new_row = pd.DataFrame({
                    'timestamp': [df['timestamp'].iloc[i]],
                    'fvg_low': [df['high'].iloc[i-1]],
                    'fvg_high': [df['low'].iloc[i+1]],
                    'filled': [False]
                })
                bullish_fvg = pd.concat([bullish_fvg, new_row], ignore_index=True)
            
            # Bearish FVG: Önceki mumun düşük değeri, sonraki mumun yüksek değerinden büyükse
            if df['low'].iloc[i-1] > df['high'].iloc[i+1]:
                new_row = pd.DataFrame({
                    'timestamp': [df['timestamp'].iloc[i]],
                    'fvg_low': [df['high'].iloc[i+1]],
                    'fvg_high': [df['low'].iloc[i-1]],
                    'filled': [False]
                })
                bearish_fvg = pd.concat([bearish_fvg, new_row], ignore_index=True)
        
        return bullish_fvg, bearish_fvg
    except Exception as e:
        logger.error(f"FVG hesaplanırken hata oluştu: {e}")
        return pd.DataFrame(), pd.DataFrame()

def find_break_of_structure(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    """
    Break of Structure (BOS) noktalarını tespit eder.
    
    BOS, fiyatın önceki yüksek/düşük noktalarını kırması durumudur ve
    trend değişiminin veya devamının sinyali olabilir.
    
    Args:
        df (pandas.DataFrame): OHLCV verileri içeren DataFrame
        window (int): Yüksek/düşük noktaları belirlemek için kullanılacak pencere boyutu
    
    Returns:
        pandas.DataFrame: BOS noktalarını içeren DataFrame
    """
    try:
        # Boş DataFrame oluştur
        bos_points = pd.DataFrame(columns=['timestamp', 'price', 'type'])
        
        # En az window+1 mum gerekli
        if len(df) <= window:
            return bos_points
        
        # Rolling window ile yüksek ve düşük noktaları bul
        df['rolling_high'] = df['high'].rolling(window=window).max().shift(1)
        df['rolling_low'] = df['low'].rolling(window=window).min().shift(1)
        
        # BOS noktalarını bul
        for i in range(window, len(df)):
            # Bullish BOS: Fiyat önceki yüksek noktayı kırıyorsa
            if df['high'].iloc[i] > df['rolling_high'].iloc[i]:
                new_row = pd.DataFrame({
                    'timestamp': [df['timestamp'].iloc[i]],
                    'price': [df['high'].iloc[i]],
                    'type': ['bullish']
                })
                bos_points = pd.concat([bos_points, new_row], ignore_index=True)
            
            # Bearish BOS: Fiyat önceki düşük noktayı kırıyorsa
            if df['low'].iloc[i] < df['rolling_low'].iloc[i]:
                new_row = pd.DataFrame({
                    'timestamp': [df['timestamp'].iloc[i]],
                    'price': [df['low'].iloc[i]],
                    'type': ['bearish']
                })
                bos_points = pd.concat([bos_points, new_row], ignore_index=True)
        
        return bos_points
    except Exception as e:
        logger.error(f"BOS hesaplanırken hata oluştu: {e}")
        return pd.DataFrame()

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TechnicalIndicators:
    def __init__(self, df):
        """
        Teknik indikatörleri hesaplamak için sınıf.
        
        Args:
            df (pandas.DataFrame): OHLCV verileri içeren DataFrame
        """
        self.df = df.copy()
        
        # DataFrame'in gerekli sütunları içerdiğinden emin ol
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in self.df.columns:
                logger.error(f"DataFrame'de gerekli sütun eksik: {col}")
                raise ValueError(f"DataFrame'de gerekli sütun eksik: {col}")
    
    def add_fvg(self):
        """Fair Value Gap (FVG) bölgelerini tespit eder ve DataFrame'e ekler."""
        try:
            # FVG'leri bul
            bullish_fvg, bearish_fvg = find_fair_value_gaps(self.df)
            
            # FVG bilgilerini DataFrame'e ekle
            self.df['bullish_fvg_count'] = 0
            self.df['bearish_fvg_count'] = 0
            
            # Son 5 mum içindeki FVG sayısını hesapla
            for i in range(len(self.df)):
                # Son 5 mum içindeki timestamp'leri al
                recent_timestamps = self.df['timestamp'].iloc[max(0, i-5):i+1]
                
                # Bu zaman aralığındaki bullish FVG'leri say
                bullish_count = len(bullish_fvg[bullish_fvg['timestamp'].isin(recent_timestamps)])
                self.df.loc[self.df.index[i], 'bullish_fvg_count'] = bullish_count
                
                # Bu zaman aralığındaki bearish FVG'leri say
                bearish_count = len(bearish_fvg[bearish_fvg['timestamp'].isin(recent_timestamps)])
                self.df.loc[self.df.index[i], 'bearish_fvg_count'] = bearish_count
            
            return self.df
        except Exception as e:
            logger.error(f"FVG eklenirken hata oluştu: {e}")
            return self.df
    
    def add_bos(self, window=10):
        """Break of Structure (BOS) noktalarını tespit eder ve DataFrame'e ekler."""
        try:
            # BOS noktalarını bul
            bos_points = find_break_of_structure(self.df, window)
            
            # BOS bilgilerini DataFrame'e ekle
            self.df['bullish_bos'] = False
            self.df['bearish_bos'] = False
            
            # BOS noktalarını işaretle
            for _, row in bos_points.iterrows():
                idx = self.df[self.df['timestamp'] == row['timestamp']].index
                if len(idx) > 0:
                    if row['type'] == 'bullish':
                        self.df.loc[idx[0], 'bullish_bos'] = True
                    elif row['type'] == 'bearish':
                        self.df.loc[idx[0], 'bearish_bos'] = True
            
            return self.df
        except Exception as e:
            logger.error(f"BOS eklenirken hata oluştu: {e}")
            return self.df
    
    def add_all_indicators(self, selected_indicators=None):
        """
        Tüm indikatörleri ekler.
        
        Args:
            selected_indicators (list, optional): Eklenecek indikatörlerin listesi. None ise tüm indikatörler eklenir.
        
        Returns:
            pandas.DataFrame: İndikatörleri eklenmiş DataFrame
        """
        try:
            if selected_indicators is None:
                selected_indicators = ["rsi", "macd", "bollinger", "ema", "stochastic", "volume", "vwap", "vwema", "fvg", "bos", "fvg_bos_combo"]
            
            # RSI
            if "rsi" in selected_indicators:
                self.add_rsi()
            
            # MACD
            if "macd" in selected_indicators:
                self.add_macd()
            
            # Bollinger Bands
            if "bollinger" in selected_indicators:
                self.add_bollinger_bands()
            
            # EMA
            if "ema" in selected_indicators:
                self.add_ema()
            
            # Stochastic
            if "stochastic" in selected_indicators:
                self.add_stochastic()
            
            # VWAP
            if "vwap" in selected_indicators:
                self.add_vwap()
                
            # VWEMA
            if "vwema" in selected_indicators:
                self.add_vwema()
            
            # Smart Money Concepts göstergeleri
            # Fair Value Gap (FVG)
            if "fvg" in selected_indicators:
                self.add_fvg()
                
            # Break of Structure (BOS)
            if "bos" in selected_indicators:
                self.add_bos()
            
            # FVG + BOS Kombosu için ayrıca bir şey yapmaya gerek yok,
            # çünkü bu sinyal add_signal_columns() içinde hesaplanıyor
            # ve her iki gösterge de eklendiğinde otomatik olarak oluşuyor
            
            # Sinyal sütunlarını ekle
            self.add_signal_columns()
            
            return self.df
        except Exception as e:
            logger.error(f"Tüm indikatörler eklenirken hata oluştu: {e}")
            return self.df
    
    def add_macd(self, fast_period=12, slow_period=26, signal_period=9):
        """MACD indikatörünü ekler."""
        try:
            macd = MACD(
                close=self.df['close'],
                window_fast=fast_period,
                window_slow=slow_period,
                window_sign=signal_period
            )
            
            self.df['macd'] = macd.macd()
            self.df['macd_signal'] = macd.macd_signal()
            self.df['macd_diff'] = macd.macd_diff()
            
            return self.df
        except Exception as e:
            logger.error(f"MACD eklenirken hata oluştu: {e}")
            return self.df
    
    def add_rsi(self, period=14):
        """RSI indikatörünü ekler."""
        try:
            rsi = RSIIndicator(close=self.df['close'], window=period)
            self.df['rsi'] = rsi.rsi()
            
            return self.df
        except Exception as e:
            logger.error(f"RSI eklenirken hata oluştu: {e}")
            return self.df
    
    def add_bollinger_bands(self, window=20, window_dev=2):
        """Bollinger Bands indikatörünü ekler."""
        try:
            bollinger = BollingerBands(
                close=self.df['close'],
                window=window,
                window_dev=window_dev
            )
            
            self.df['bb_high'] = bollinger.bollinger_hband()
            self.df['bb_mid'] = bollinger.bollinger_mavg()
            self.df['bb_low'] = bollinger.bollinger_lband()
            self.df['bb_width'] = bollinger.bollinger_wband()
            self.df['bb_pct'] = (self.df['close'] - self.df['bb_low']) / (self.df['bb_high'] - self.df['bb_low'])
            
            return self.df
        except Exception as e:
            logger.error(f"Bollinger Bands eklenirken hata oluştu: {e}")
            return self.df
    
    def add_ema(self, short_period=9, medium_period=21, long_period=50):
        """EMA indikatörlerini ekler."""
        try:
            self.df[f'ema_{short_period}'] = EMAIndicator(close=self.df['close'], window=short_period).ema_indicator()
            self.df[f'ema_{medium_period}'] = EMAIndicator(close=self.df['close'], window=medium_period).ema_indicator()
            self.df[f'ema_{long_period}'] = EMAIndicator(close=self.df['close'], window=long_period).ema_indicator()
            
            return self.df
        except Exception as e:
            logger.error(f"EMA eklenirken hata oluştu: {e}")
            return self.df
    
    def add_sma(self, short_period=10, medium_period=30, long_period=100):
        """SMA indikatörlerini ekler."""
        try:
            self.df[f'sma_{short_period}'] = SMAIndicator(close=self.df['close'], window=short_period).sma_indicator()
            self.df[f'sma_{medium_period}'] = SMAIndicator(close=self.df['close'], window=medium_period).sma_indicator()
            self.df[f'sma_{long_period}'] = SMAIndicator(close=self.df['close'], window=long_period).sma_indicator()
            
            return self.df
        except Exception as e:
            logger.error(f"SMA eklenirken hata oluştu: {e}")
            return self.df
    
    def add_stochastic(self, window=14, smooth_window=3):
        """Stochastic Oscillator indikatörünü ekler."""
        try:
            stoch = StochasticOscillator(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=window,
                smooth_window=smooth_window
            )
            
            self.df['stoch_k'] = stoch.stoch()
            self.df['stoch_d'] = stoch.stoch_signal()
            
            return self.df
        except Exception as e:
            logger.error(f"Stochastic Oscillator eklenirken hata oluştu: {e}")
            return self.df
    
    def add_atr(self, window=14):
        """Average True Range indikatörünü ekler."""
        try:
            atr = AverageTrueRange(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                window=window
            )
            
            self.df['atr'] = atr.average_true_range()
            
            return self.df
        except Exception as e:
            logger.error(f"ATR eklenirken hata oluştu: {e}")
            return self.df
    
    def add_obv(self):
        """On-Balance Volume indikatörünü ekler."""
        try:
            obv = OnBalanceVolumeIndicator(
                close=self.df['close'],
                volume=self.df['volume']
            )
            
            self.df['obv'] = obv.on_balance_volume()
            
            return self.df
        except Exception as e:
            logger.error(f"OBV eklenirken hata oluştu: {e}")
            return self.df
    
    def add_vwap(self):
        """Volume Weighted Average Price indikatörünü ekler."""
        try:
            vwap = VolumeWeightedAveragePrice(
                high=self.df['high'],
                low=self.df['low'],
                close=self.df['close'],
                volume=self.df['volume'],
                window=14
            )
            
            self.df['vwap'] = vwap.volume_weighted_average_price()
            
            return self.df
        except Exception as e:
            logger.error(f"VWAP eklenirken hata oluştu: {e}")
            return self.df
            
    def add_vwema(self, short_period=5, long_period=20):
        """Volume Weighted Exponential Moving Average indikatörlerini ekler."""
        try:
            # VWEMA hesapla
            self.df[f'vwema_{short_period}'] = calculate_vwema(self.df, short_period)
            self.df[f'vwema_{long_period}'] = calculate_vwema(self.df, long_period)
            
            return self.df
        except Exception as e:
            logger.error(f"VWEMA eklenirken hata oluştu: {e}")
            return self.df
    
    def add_signal_columns(self):
        """Sinyal sütunlarını ekler."""
        try:
            # RSI sinyalleri
            self.df['rsi_signal'] = 0
            self.df.loc[self.df['rsi'] < 30, 'rsi_signal'] = 1  # Aşırı satım - Alış sinyali
            self.df.loc[self.df['rsi'] > 70, 'rsi_signal'] = -1  # Aşırı alım - Satış sinyali
            
            # MACD sinyalleri
            self.df['macd_signal_value'] = self.df['macd_signal']
            self.df['macd_diff'] = self.df['macd'] - self.df['macd_signal_value']
            self.df['macd_signal'] = 0
            self.df.loc[self.df['macd'] > self.df['macd_signal_value'], 'macd_signal'] = 1  # MACD, sinyal çizgisinin üzerinde - Alış sinyali
            self.df.loc[self.df['macd'] < self.df['macd_signal_value'], 'macd_signal'] = -1  # MACD, sinyal çizgisinin altında - Satış sinyali
            
            # Bollinger Bands sinyalleri
            self.df['bb_signal'] = 0
            self.df.loc[self.df['close'] < self.df['bb_low'], 'bb_signal'] = 1  # Fiyat alt bandın altında - Alış sinyali
            self.df.loc[self.df['close'] > self.df['bb_high'], 'bb_signal'] = -1  # Fiyat üst bandın üstünde - Satış sinyali
            
            # EMA çapraz sinyalleri (9 ve 21)
            self.df['ema_cross_signal'] = 0
            self.df.loc[(self.df['ema_9'] > self.df['ema_21']) & (self.df['ema_9'].shift(1) <= self.df['ema_21'].shift(1)), 'ema_cross_signal'] = 1  # Altın çapraz - Alış sinyali
            self.df.loc[(self.df['ema_9'] < self.df['ema_21']) & (self.df['ema_9'].shift(1) >= self.df['ema_21'].shift(1)), 'ema_cross_signal'] = -1  # Ölüm çaprazı - Satış sinyali
            
            # Stochastic sinyalleri
            self.df['stoch_signal'] = 0
            self.df.loc[(self.df['stoch_k'] < 20) & (self.df['stoch_d'] < 20) & (self.df['stoch_k'] > self.df['stoch_d']), 'stoch_signal'] = 1  # Aşırı satım ve yukarı çapraz - Alış sinyali
            self.df.loc[(self.df['stoch_k'] > 80) & (self.df['stoch_d'] > 80) & (self.df['stoch_k'] < self.df['stoch_d']), 'stoch_signal'] = -1  # Aşırı alım ve aşağı çapraz - Satış sinyali
            
            # VWEMA çapraz sinyalleri (5 ve 20)
            if 'vwema_5' in self.df.columns and 'vwema_20' in self.df.columns:
                self.df['vwema_cross_signal'] = 0
                self.df.loc[(self.df['vwema_5'] > self.df['vwema_20']) & (self.df['vwema_5'].shift(1) <= self.df['vwema_20'].shift(1)), 'vwema_cross_signal'] = 1  # Altın çapraz - Alış sinyali
                self.df.loc[(self.df['vwema_5'] < self.df['vwema_20']) & (self.df['vwema_5'].shift(1) >= self.df['vwema_20'].shift(1)), 'vwema_cross_signal'] = -1  # Ölüm çaprazı - Satış sinyali
            else:
                self.df['vwema_cross_signal'] = 0
            
            # FVG sinyalleri
            self.df['fvg_signal'] = 0
            # Bullish FVG sayısı bearish'ten fazlaysa alış sinyali
            self.df.loc[self.df['bullish_fvg_count'] > self.df['bearish_fvg_count'], 'fvg_signal'] = 1
            # Bearish FVG sayısı bullish'ten fazlaysa satış sinyali
            self.df.loc[self.df['bearish_fvg_count'] > self.df['bullish_fvg_count'], 'fvg_signal'] = -1
            
            # BOS sinyalleri
            self.df['bos_signal'] = 0
            # Bullish BOS varsa alış sinyali
            self.df.loc[self.df['bullish_bos'] == True, 'bos_signal'] = 1
            # Bearish BOS varsa satış sinyali
            self.df.loc[self.df['bearish_bos'] == True, 'bos_signal'] = -1
            
            # FVG + BOS Kombo sinyali
            self.df['fvg_bos_combo_signal'] = 0
            # Bullish FVG ve Bullish BOS birlikte varsa güçlü alış sinyali
            self.df.loc[(self.df['bullish_fvg_count'] > 0) & (self.df['bullish_bos'] == True), 'fvg_bos_combo_signal'] = 2
            # Bearish FVG ve Bearish BOS birlikte varsa güçlü satış sinyali
            self.df.loc[(self.df['bearish_fvg_count'] > 0) & (self.df['bearish_bos'] == True), 'fvg_bos_combo_signal'] = -2
            
            # Genel sinyal (tüm sinyallerin toplamı)
            self.df['overall_signal'] = (
                self.df['rsi_signal'] + 
                self.df['macd_signal'] + 
                self.df['bb_signal'] + 
                self.df['ema_cross_signal'] + 
                self.df['stoch_signal'] +
                self.df['vwema_cross_signal'] +
                self.df['fvg_signal'] +
                self.df['bos_signal'] +
                self.df['fvg_bos_combo_signal']
            )
            
            # Güçlü sinyal sütunları
            self.df['strong_buy_signal'] = (self.df['overall_signal'] >= 3).astype(int)
            self.df['strong_sell_signal'] = (self.df['overall_signal'] <= -3).astype(int)
            
            return self.df
        except Exception as e:
            logger.error(f"Sinyal sütunları eklenirken hata oluştu: {e}")
            return self.df

def get_signals(df):
    """
    Teknik göstergelerden sinyal değerlerini alır.
    
    Args:
        df (pd.DataFrame): Teknik göstergeleri içeren DataFrame
    
    Returns:
        dict: Sinyal değerlerini içeren sözlük
    """
    try:
        if df is None or df.empty:
            return {}
        
        # Son satırı al
        last_row = df.iloc[-1]
        
        signals = {
            'rsi': {
                'value': last_row['rsi'] if 'rsi' in last_row else None,
                'signal': last_row['rsi_signal'] if 'rsi_signal' in last_row else 0
            },
            'macd': {
                'value': last_row['macd'] if 'macd' in last_row else None,
                'signal': last_row['macd_signal'] if 'macd_signal' in last_row else 0
            },
            'bollinger': {
                'value': f"Üst: {last_row['bb_high']:.2f}, Alt: {last_row['bb_low']:.2f}" if 'bb_high' in last_row and 'bb_low' in last_row else None,
                'signal': last_row['bb_signal'] if 'bb_signal' in last_row else 0
            },
            'ema_cross': {
                'value': f"EMA9: {last_row['ema_9']:.2f}, EMA21: {last_row['ema_21']:.2f}" if 'ema_9' in last_row and 'ema_21' in last_row else None,
                'signal': last_row['ema_cross_signal'] if 'ema_cross_signal' in last_row else 0
            },
            'stochastic': {
                'value': f"K: {last_row['stoch_k']:.2f}, D: {last_row['stoch_d']:.2f}" if 'stoch_k' in last_row and 'stoch_d' in last_row else None,
                'signal': last_row['stoch_signal'] if 'stoch_signal' in last_row else 0
            },
            'vwap': {
                'value': last_row['vwap'] if 'vwap' in last_row else None,
                'signal': 1 if 'vwap' in last_row and last_row['close'] > last_row['vwap'] else (-1 if 'vwap' in last_row and last_row['close'] < last_row['vwap'] else 0)
            },
            'vwema_cross': {
                'value': f"VWEMA5: {last_row['vwema_5']:.2f}, VWEMA20: {last_row['vwema_20']:.2f}" if 'vwema_5' in last_row and 'vwema_20' in last_row else None,
                'signal': last_row['vwema_cross_signal'] if 'vwema_cross_signal' in last_row else 0
            },
            'overall': {
                'value': last_row['overall_signal'] if 'overall_signal' in last_row else None,
                'signal': last_row['overall_signal'] if 'overall_signal' in last_row else 0
            }
        }
        
        # FVG sinyallerini ekle (eğer varsa)
        if 'bullish_fvg_count' in last_row and 'bearish_fvg_count' in last_row:
            signals['fvg'] = {
                'value': f"Bullish: {last_row['bullish_fvg_count']}, Bearish: {last_row['bearish_fvg_count']}",
                'signal': last_row['fvg_signal'] if 'fvg_signal' in last_row else 0
            }
        
        # BOS sinyallerini ekle (eğer varsa)
        if 'bullish_bos' in last_row and 'bearish_bos' in last_row:
            bullish_text = "Evet" if last_row['bullish_bos'] else "Hayır"
            bearish_text = "Evet" if last_row['bearish_bos'] else "Hayır"
            signals['bos'] = {
                'value': f"Bullish: {bullish_text}, Bearish: {bearish_text}",
                'signal': last_row['bos_signal'] if 'bos_signal' in last_row else 0
            }
        
        # FVG + BOS Kombo sinyalini ekle (eğer varsa)
        if 'fvg_bos_combo_signal' in last_row:
            combo_value = ""
            if last_row['fvg_bos_combo_signal'] == 2:
                combo_value = "Bullish FVG + Bullish BOS"
            elif last_row['fvg_bos_combo_signal'] == -2:
                combo_value = "Bearish FVG + Bearish BOS"
            else:
                combo_value = "Kombo sinyal yok"
                
            signals['fvg_bos_combo'] = {
                'value': combo_value,
                'signal': last_row['fvg_bos_combo_signal']
            }
        
        return signals
    except Exception as e:
        logger.error(f"Sinyaller alınırken hata oluştu: {e}")
        return {}