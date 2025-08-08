import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import time
from indicators import TechnicalIndicators, get_signals
from utils import create_candlestick_chart, format_number, get_signal_emoji
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def render_dashboard(symbol, interval, data_limit, selected_indicators, binance_api):
    """
    Ana dashboard'u oluşturur.
    
    Args:
        symbol (str): Kripto para sembolü
        interval (str): Zaman aralığı
        data_limit (int): Veri sayısı limiti
        selected_indicators (list): Seçilen indikatörler
        binance_api (BinanceAPI): Binance API nesnesi
    """
    try:
        st.title(f"📊 {symbol} Analiz Paneli")
        
        # Veri yükleme göstergesi
        with st.spinner(f"{symbol} verileri yükleniyor..."):
            # Kline verilerini al
            df = binance_api.get_klines(symbol=symbol, interval=interval, limit=data_limit)
            
            if df.empty:
                st.error(f"{symbol} için veri alınamadı. Lütfen başka bir sembol seçin.")
                return
            
            # Teknik indikatörleri hesapla
            indicators = TechnicalIndicators(df)
            df_with_indicators = indicators.add_all_indicators()
            
            # Son fiyat bilgisini al
            last_price = df_with_indicators['close'].iloc[-1]
            previous_price = df_with_indicators['close'].iloc[-2]
            price_change = ((last_price - previous_price) / previous_price) * 100
            
            # Fiyat değişim rengi
            price_color = "green" if price_change >= 0 else "red"
            
            # Sinyalleri al
            signals = get_signals(df_with_indicators)
        
        # Analiz paneli stilini uygula
        st.markdown("""
        <style>
        /* Analiz paneli başlık stilini özelleştir */
        .main .block-container h1 {
            color: white;
            font-size: 32px !important;
            font-weight: 700 !important;
            margin-bottom: 25px !important;
            padding-bottom: 15px !important;
            border-bottom: 2px solid rgba(76, 175, 80, 0.3);
            display: flex;
            align-items: center;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
            letter-spacing: 0.5px;
        }
        
        /* Analiz paneli alt başlık stilini özelleştir */
        .main .block-container h2 {
            color: #4CAF50;
            font-size: 24px !important;
            font-weight: 700 !important;
            margin-top: 30px !important;
            margin-bottom: 20px !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
        }
        
        /* Analiz paneli alt başlık stilini özelleştir */
        .main .block-container h3 {
            color: white;
            font-size: 20px !important;
            font-weight: 600 !important;
            margin-top: 25px !important;
            margin-bottom: 15px !important;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.3px;
        }
        
        /* Modern üst bilgi kartları */
        .metric-row {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background-color: var(--card-background);
            border-radius: 14px;
            padding: 22px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
            flex: 1;
            min-width: 200px;
            position: relative;
            overflow: hidden;
            transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            border: 1px solid rgba(255, 255, 255, 0.08);
            backdrop-filter: blur(5px);
        }
        .metric-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.35);
            border-color: rgba(76, 175, 80, 0.4);
        }
        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
            border-radius: 4px 4px 0 0;
        }
        .metric-title {
            font-size: 15px;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }
        .metric-value {
            font-size: 32px;
            font-weight: 800;
            color: white;
            margin-bottom: 14px;
            text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
            letter-spacing: 0.5px;
        }
        .metric-change {
            font-size: 15px;
            display: flex;
            align-items: center;
            font-weight: 600;
            padding: 6px 12px;
            border-radius: 6px;
            width: fit-content;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            transition: all 0.3s ease;
        }
        .metric-change:hover {
            transform: translateX(3px);
        }
        .metric-change.positive {
            color: #4CAF50;
            background-color: rgba(76, 175, 80, 0.15);
            border-left: 3px solid #4CAF50;
        }
        .metric-change.negative {
            color: #F44336;
            background-color: rgba(244, 67, 54, 0.15);
            border-left: 3px solid #F44336;
        }
        .metric-change.neutral {
            color: #9E9E9E;
            background-color: rgba(158, 158, 158, 0.15);
            border-left: 3px solid #9E9E9E;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Metrik kartları için container
        st.markdown('<div class="metric-row">', unsafe_allow_html=True)
        
        # Son Fiyat kartı
        price_change_class = "positive" if price_change >= 0 else "negative"
        price_change_icon = "↑" if price_change >= 0 else "↓"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">SON FİYAT</div>
            <div class="metric-value">${format_number(last_price, 4)}</div>
            <div class="metric-change {price_change_class}">
                {price_change_icon} {format_number(price_change, 2)}%
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Genel Sinyal kartı
        overall_signal = signals['overall']['signal']
        
        # Sinyal değerini string'e çevir ve emoji al
        overall_signal_str = str(overall_signal)
        overall_emoji = get_signal_emoji(overall_signal)
        
        # Değeri al ve sınıf belirle
        try:
            overall_value = signals['overall']['value'] if signals['overall']['value'] is not None else 0
            overall_class = "positive" if overall_value > 0 else "negative" if overall_value < 0 else "neutral"
        except Exception:
            overall_value = 0
            overall_class = "neutral"
        
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">GENEL SİNYAL</div>
            <div class="metric-value">{overall_signal_str} {overall_emoji}</div>
            <div class="metric-change {overall_class}">
                Değer: {overall_value}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Grafik
        fig = create_candlestick_chart(df_with_indicators, symbol, selected_indicators)
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")
        
        # Sinyal tablosu
        st.subheader("📋 Teknik Analiz Sinyalleri")
        
        # Sinyal tablosunu oluştur
        indicators_list = ["RSI", "MACD", "Bollinger Bands", "EMA Çaprazlama", "Stochastic", "VWAP", "VWEMA Çaprazlama"]
        values = [
            str(signals['rsi']['value']) if signals['rsi']['value'] is not None else "N/A",
            str(signals['macd']['value']) if signals['macd']['value'] is not None else "N/A",
            str(signals['bollinger']['value']) if signals['bollinger']['value'] is not None else "N/A",
            str(signals['ema_cross']['value']) if signals['ema_cross']['value'] is not None else "N/A",
            str(signals['stochastic']['value']) if signals['stochastic']['value'] is not None else "N/A",
            str(signals['vwap']['value']) if signals['vwap']['value'] is not None else "N/A",
            str(signals['vwema_cross']['value']) if signals['vwema_cross']['value'] is not None else "N/A"
        ]
        signal_texts = [
            f"{signals['rsi']['signal']} {get_signal_emoji(signals['rsi']['signal'])}",
            f"{signals['macd']['signal']} {get_signal_emoji(signals['macd']['signal'])}",
            f"{signals['bollinger']['signal']} {get_signal_emoji(signals['bollinger']['signal'])}",
            f"{signals['ema_cross']['signal']} {get_signal_emoji(signals['ema_cross']['signal'])}",
            f"{signals['stochastic']['signal']} {get_signal_emoji(signals['stochastic']['signal'])}",
            f"{signals['vwap']['signal']} {get_signal_emoji(signals['vwap']['signal'])}",
            f"{signals['vwema_cross']['signal']} {get_signal_emoji(signals['vwema_cross']['signal'])}"
        ]
        
        # Genel sinyali ekle
        indicators_list.append("Genel Sinyal")
        values.append(str(signals['overall']['value']) if signals['overall']['value'] is not None else "N/A")
        signal_texts.append(f"{overall_signal_str} {overall_emoji}")
        
        signal_data = {
            "İndikatör": indicators_list,
            "Değer": values,
            "Sinyal": signal_texts
        }
        
        signal_df = pd.DataFrame(signal_data)
        
        # Sinyal tablosunu göster
        st.dataframe(
            signal_df,
            column_config={
                "İndikatör": st.column_config.TextColumn("İndikatör"),
                "Değer": st.column_config.TextColumn("Değer"),
                "Sinyal": st.column_config.TextColumn("Sinyal")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Detaylı veri tablosu
        st.subheader("📋 Detaylı Veri Tablosu")
        
        # Gösterilecek sütunları belirle
        display_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        
        if 'rsi' in df_with_indicators.columns:
            display_columns.append('rsi')
            
        if 'macd' in df_with_indicators.columns:
            display_columns.extend(['macd', 'macd_signal'])
        
        if 'bb_high' in df_with_indicators.columns:
            display_columns.extend(['bb_high', 'bb_mid', 'bb_low'])
        
        if 'ema_9' in df_with_indicators.columns:
            display_columns.extend(['ema_9', 'ema_21', 'ema_50'])
            
        if 'vwap' in df_with_indicators.columns:
            display_columns.append('vwap')
            
        if 'vwema_5' in df_with_indicators.columns and 'vwema_20' in df_with_indicators.columns:
            display_columns.extend(['vwema_5', 'vwema_20'])
        
        # Son 20 satırı göster
        st.dataframe(
            df_with_indicators[display_columns].tail(20),
            use_container_width=True
        )
        
        # Son güncelleme zamanı
        st.markdown(f"""
        <div style="
            text-align: right;
            color: #aaa;
            font-size: 13px;
            margin-top: 30px;
            margin-bottom: 15px;
            padding: 10px 16px;
            background-color: rgba(0,0,0,0.3);
            border-radius: 8px;
            display: inline-block;
            float: right;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.05);
            font-weight: 500;
            letter-spacing: 0.5px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        " onmouseover="this.style.transform='translateY(-3px)';this.style.boxShadow='0 6px 12px rgba(0, 0, 0, 0.3)';" 
           onmouseout="this.style.transform='translateY(0)';this.style.boxShadow='0 4px 8px rgba(0, 0, 0, 0.2)';">
            <span style="color: var(--primary-color); margin-right: 5px;">⏱️</span> Son güncelleme: <span style="color: white; font-weight: 600;">{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
        <div style="clear: both;"></div>
        """, unsafe_allow_html=True)
    
    except Exception as e:
        logger.error(f"Dashboard oluşturulurken hata oluştu: {e}")
        st.error(f"Bir hata oluştu: {e}")

def render_loading_placeholder():
    """
    Yükleme yer tutucusu oluşturur.
    """
    st.title("📊 Kripto Analiz Paneli")
    st.info("Lütfen yan menüden bir kripto para seçin.")
    
    # Örnek grafik
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1, 2], y=[0, 1, 0], mode="lines"))
    fig.update_layout(
        title="Kripto verilerini görüntülemek için bir sembol seçin",
        template="plotly_dark"
    )
    
    st.plotly_chart(fig, use_container_width=True)