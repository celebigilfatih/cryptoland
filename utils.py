import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import logging
from datetime import datetime, timedelta

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def format_number(number, precision=2):
    """
    Sayıları okunabilir formatta biçimlendirir.
    
    Args:
        number (float): Biçimlendirilecek sayı
        precision (int): Ondalık basamak sayısı
    
    Returns:
        str: Biçimlendirilmiş sayı
    """
    try:
        if number is None:
            return "N/A"
        
        if isinstance(number, str):
            return number
        
        if abs(number) >= 1_000_000_000:
            return f"{number / 1_000_000_000:.{precision}f}B"
        elif abs(number) >= 1_000_000:
            return f"{number / 1_000_000:.{precision}f}M"
        elif abs(number) >= 1_000:
            return f"{number / 1_000:.{precision}f}K"
        else:
            return f"{number:.{precision}f}"
    except Exception as e:
        logger.error(f"Sayı biçimlendirilirken hata oluştu: {e}")
        return str(number)

def create_candlestick_chart(df, symbol, selected_indicators=None):
    """
    Mum grafiği oluşturur.
    
    Args:
        df (pd.DataFrame): Veri çerçevesi
        symbol (str): Sembol
        selected_indicators (list, optional): Seçilen indikatörler
    
    Returns:
        plotly.graph_objects.Figure: Mum grafiği
    """
    try:
        if selected_indicators is None:
            selected_indicators = []
        
        # Subplot sayısını belirle
        subplot_count = 1  # Ana grafik için
        
        if "volume" in selected_indicators:
            subplot_count += 1
        
        if "rsi" in selected_indicators:
            subplot_count += 1
        
        if "macd" in selected_indicators:
            subplot_count += 1
        
        # Subplot yüksekliklerini belirle - Ana grafik için daha fazla alan ayır
        row_heights = [0.7]  # Ana grafik için daha büyük oran (0.6'dan 0.7'ye)
        
        if "volume" in selected_indicators:
            row_heights.append(0.1)  # Hacim grafiği için
        
        if "rsi" in selected_indicators:
            row_heights.append(0.15)  # RSI grafiği için küçültüldü (0.2'den 0.15'e)
        
        if "macd" in selected_indicators:
            row_heights.append(0.15)  # MACD grafiği için küçültüldü (0.2'den 0.15'e)
        
        # Subplot düzenini oluştur
        fig = make_subplots(
            rows=subplot_count,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.01,  # Dikey boşluğu azalt (0.02'den 0.01'e)
            row_heights=row_heights,
            subplot_titles=["Fiyat"] + (["Hacim"] if "volume" in selected_indicators else []) + (["RSI"] if "rsi" in selected_indicators else []) + (["MACD"] if "macd" in selected_indicators else [])
        )
        
        # Mum grafiği ekle
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name="Fiyat"
            ),
            row=1, col=1
        )
        
        # Bollinger Bands
        if "bollinger" in selected_indicators and 'bb_high' in df.columns and 'bb_mid' in df.columns and 'bb_low' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_high'],
                    line=dict(color='rgba(250, 0, 0, 0.7)', width=1),
                    name="BB Üst"
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_mid'],
                    line=dict(color='rgba(0, 0, 250, 0.7)', width=1),
                    name="BB Orta"
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['bb_low'],
                    line=dict(color='rgba(0, 250, 0, 0.7)', width=1),
                    name="BB Alt"
                ),
                row=1, col=1
            )
        
        # EMA
        if "ema" in selected_indicators:
            if 'ema_9' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_9'],
                        line=dict(color='rgba(255, 165, 0, 0.7)', width=1.5),
                        name="EMA 9"
                    ),
                    row=1, col=1
                )
            
            if 'ema_21' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_21'],
                        line=dict(color='rgba(148, 0, 211, 0.7)', width=1.5),
                        name="EMA 21"
                    ),
                    row=1, col=1
                )
            
            if 'ema_50' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['ema_50'],
                        line=dict(color='rgba(255, 0, 255, 0.7)', width=1.5),
                        name="EMA 50"
                    ),
                    row=1, col=1
                )
        
        # VWAP
        if "vwap" in selected_indicators and 'vwap' in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['vwap'],
                    line=dict(color='rgba(255, 0, 255, 0.7)', width=1.5, dash='dot'),
                    name="VWAP"
                ),
                row=1, col=1
            )
        
        # VWEMA
        if "vwema" in selected_indicators:
            if 'vwema_5' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['vwema_5'],
                        line=dict(color='rgba(0, 255, 255, 0.7)', width=1.5),
                        name="VWEMA 5"
                    ),
                    row=1, col=1
                )
            
            if 'vwema_20' in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df['timestamp'],
                        y=df['vwema_20'],
                        line=dict(color='rgba(255, 255, 0, 0.7)', width=1.5),
                        name="VWEMA 20"
                    ),
                    row=1, col=1
                )
        
        # Fair Value Gap (FVG) gösterimi
        if "fvg" in selected_indicators and 'bullish_fvg_count' in df.columns and 'bearish_fvg_count' in df.columns:
            # Bullish FVG için yukarı ok işaretleri
            bullish_fvg_df = df[df['bullish_fvg_count'] > 0]
            if not bullish_fvg_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bullish_fvg_df['timestamp'],
                        y=bullish_fvg_df['high'] + (bullish_fvg_df['high'] * 0.002),  # Mumun biraz üstünde
                        mode='markers',
                        marker=dict(
                            symbol='triangle-up',
                            size=10,
                            color='rgba(0, 255, 0, 0.8)',
                            line=dict(width=1, color='rgba(0, 255, 0, 1)')
                        ),
                        name="Bullish FVG"
                    ),
                    row=1, col=1
                )
            
            # Bearish FVG için aşağı ok işaretleri
            bearish_fvg_df = df[df['bearish_fvg_count'] > 0]
            if not bearish_fvg_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bearish_fvg_df['timestamp'],
                        y=bearish_fvg_df['low'] - (bearish_fvg_df['low'] * 0.002),  # Mumun biraz altında
                        mode='markers',
                        marker=dict(
                            symbol='triangle-down',
                            size=10,
                            color='rgba(255, 0, 0, 0.8)',
                            line=dict(width=1, color='rgba(255, 0, 0, 1)')
                        ),
                        name="Bearish FVG"
                    ),
                    row=1, col=1
                )
        
        # Break of Structure (BOS) gösterimi
        if "bos" in selected_indicators and 'bullish_bos' in df.columns and 'bearish_bos' in df.columns:
            # Bullish BOS için yukarı ok işaretleri
            bullish_bos_df = df[df['bullish_bos'] == True]
            if not bullish_bos_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bullish_bos_df['timestamp'],
                        y=bullish_bos_df['high'] + (bullish_bos_df['high'] * 0.004),  # Mumun biraz daha üstünde
                        mode='markers',
                        marker=dict(
                            symbol='arrow-up',
                            size=12,
                            color='rgba(0, 255, 0, 1)',
                            line=dict(width=2, color='rgba(0, 255, 0, 1)')
                        ),
                        name="Bullish BOS"
                    ),
                    row=1, col=1
                )
            
            # Bearish BOS için aşağı ok işaretleri
            bearish_bos_df = df[df['bearish_bos'] == True]
            if not bearish_bos_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bearish_bos_df['timestamp'],
                        y=bearish_bos_df['low'] - (bearish_bos_df['low'] * 0.004),  # Mumun biraz daha altında
                        mode='markers',
                        marker=dict(
                            symbol='arrow-down',
                            size=12,
                            color='rgba(255, 0, 0, 1)',
                            line=dict(width=2, color='rgba(255, 0, 0, 1)')
                        ),
                        name="Bearish BOS"
                    ),
                    row=1, col=1
                )
        
        # FVG + BOS Kombosu gösterimi
        if "fvg_bos_combo" in selected_indicators and 'fvg_bos_combo_signal' in df.columns:
            # Bullish Kombo için özel işaret (çift yukarı ok)
            bullish_combo_df = df[df['fvg_bos_combo_signal'] == 2]
            if not bullish_combo_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bullish_combo_df['timestamp'],
                        y=bullish_combo_df['high'] + (bullish_combo_df['high'] * 0.006),  # Mumun daha da üstünde
                        mode='markers',
                        marker=dict(
                            symbol='star',
                            size=14,
                            color='rgba(0, 255, 0, 1)',
                            line=dict(width=2, color='rgba(0, 255, 0, 1)')
                        ),
                        name="Bullish FVG+BOS Kombo"
                    ),
                    row=1, col=1
                )
            
            # Bearish Kombo için özel işaret (çift aşağı ok)
            bearish_combo_df = df[df['fvg_bos_combo_signal'] == -2]
            if not bearish_combo_df.empty:
                fig.add_trace(
                    go.Scatter(
                        x=bearish_combo_df['timestamp'],
                        y=bearish_combo_df['low'] - (bearish_combo_df['low'] * 0.006),  # Mumun daha da altında
                        mode='markers',
                        marker=dict(
                            symbol='star',
                            size=14,
                            color='rgba(255, 0, 0, 1)',
                            line=dict(width=2, color='rgba(255, 0, 0, 1)')
                        ),
                        name="Bearish FVG+BOS Kombo"
                    ),
                    row=1, col=1
                )
        
        # Hacim grafiği
        current_row = 1
        
        if "volume" in selected_indicators:
            current_row += 1
            
            # Hacim çubuklarının rengini belirle (yeşil: yükseliş, kırmızı: düşüş)
            colors = ['green' if row['close'] >= row['open'] else 'red' for _, row in df.iterrows()]
            
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['volume'],
                    marker_color=colors,
                    name="Hacim"
                ),
                row=current_row, col=1
            )
        
        # RSI grafiği
        if "rsi" in selected_indicators and 'rsi' in df.columns:
            current_row += 1
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['rsi'],
                    line=dict(color='blue', width=1),
                    name="RSI"
                ),
                row=current_row, col=1
            )
            
            # Aşırı alım/satım çizgileri
            fig.add_trace(
                go.Scatter(
                    x=[df['timestamp'].iloc[0], df['timestamp'].iloc[-1]],
                    y=[30, 30],
                    line=dict(color='green', width=1, dash='dash'),
                    name="Aşırı Satım"
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=[df['timestamp'].iloc[0], df['timestamp'].iloc[-1]],
                    y=[70, 70],
                    line=dict(color='red', width=1, dash='dash'),
                    name="Aşırı Alım"
                ),
                row=current_row, col=1
            )
        
        # MACD grafiği
        if "macd" in selected_indicators and 'macd' in df.columns and 'macd_signal' in df.columns:
            current_row += 1
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['macd'],
                    line=dict(color='blue', width=1.5),
                    name="MACD"
                ),
                row=current_row, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['macd_signal'],
                    line=dict(color='red', width=1),
                    name="Sinyal"
                ),
                row=current_row, col=1
            )
            
            # MACD histogramı
            colors = ['green' if val >= 0 else 'red' for val in df['macd'] - df['macd_signal']]
            
            fig.add_trace(
                go.Bar(
                    x=df['timestamp'],
                    y=df['macd'] - df['macd_signal'],
                    marker_color=colors,
                    name="MACD Hist"
                ),
                row=current_row, col=1
            )
        
        # Grafik düzenini ayarla - Daha büyük ve detaylı grafik için
        fig.update_layout(
            title=f"{symbol} Grafiği",
            xaxis_title="Tarih",
            yaxis_title="Fiyat",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=700,  # Grafik yüksekliğini artır (varsayılan 450'den 700'e)
            margin=dict(l=50, r=50, t=80, b=50),  # Kenar boşluklarını optimize et
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            hovermode="x unified"  # Fare imleci aynı x değerindeki tüm noktaları göstersin
        )
        
        # X ekseni formatını ayarla
        fig.update_xaxes(
            rangeslider_visible=False,
            rangebreaks=[
                dict(bounds=["sat", "mon"])  # Hafta sonlarını gizle
            ]
        )
        
        return fig
    except Exception as e:
        logger.error(f"Mum grafiği oluşturulurken hata: {e}")
        # Boş bir grafik döndür
        return go.Figure()

def get_time_periods():
    """
    Zaman periyotlarını döndürür.
    
    Returns:
        dict: Zaman periyotları
    """
    now = datetime.now()
    
    return {
        "Son 1 saat": now - timedelta(hours=1),
        "Son 4 saat": now - timedelta(hours=4),
        "Son 12 saat": now - timedelta(hours=12),
        "Son 24 saat": now - timedelta(hours=24),
        "Son 3 gün": now - timedelta(days=3),
        "Son 7 gün": now - timedelta(days=7),
        "Son 14 gün": now - timedelta(days=14),
        "Son 30 gün": now - timedelta(days=30),
        "Son 90 gün": now - timedelta(days=90),
        "Son 180 gün": now - timedelta(days=180),
        "Son 365 gün": now - timedelta(days=365)
    }

def filter_dataframe_by_date(df, start_date):
    """
    DataFrame'i belirli bir tarihten sonraki verilerle filtreler.
    
    Args:
        df (pandas.DataFrame): Filtrelenecek DataFrame
        start_date (datetime): Başlangıç tarihi
    
    Returns:
        pandas.DataFrame: Filtrelenmiş DataFrame
    """
    try:
        if 'timestamp' not in df.columns:
            logger.error("DataFrame'de 'timestamp' sütunu bulunamadı")
            return df
        
        return df[df['timestamp'] >= start_date]
    except Exception as e:
        logger.error(f"DataFrame filtrelenirken hata oluştu: {e}")
        return df

def calculate_change(current, previous):
    """
    Yüzde değişimi hesaplar.
    
    Args:
        current (float): Mevcut değer
        previous (float): Önceki değer
    
    Returns:
        float: Yüzde değişim
    """
    try:
        if previous == 0:
            return 0
        return ((current - previous) / previous) * 100
    except Exception as e:
        logger.error(f"Değişim hesaplanırken hata oluştu: {e}")
        return 0

def get_signal_emoji(signal):
    """
    Sinyal için emoji döndürür.
    
    Args:
        signal (str or int): Sinyal metni veya değeri
    
    Returns:
        str: Emoji
    """
    try:
        # Eğer signal bir string ise
        if isinstance(signal, str):
            if signal == "GÜÇLÜ AL":
                return "🔥 📈"
            elif signal == "AL":
                return "📈"
            elif signal == "GÜÇLÜ SAT":
                return "🔥 📉"
            elif signal == "SAT":
                return "📉"
            else:
                return "➖"
        # Eğer signal bir sayı ise
        elif isinstance(signal, (int, float, np.int64, np.float64)):
            if signal >= 2:
                return "🟢🟢"  # Güçlü alış için çift yeşil
            elif signal > 0:
                return "🟢"    # Alış için yeşil
            elif signal <= -2:
                return "🔴🔴"  # Güçlü satış için çift kırmızı
            elif signal < 0:
                return "🔴"    # Satış için kırmızı
            else:
                return "⚪"    # Nötr için beyaz
        else:
            return "⚪"
    except Exception:
        return "⚪"