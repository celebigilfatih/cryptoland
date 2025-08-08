import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
from indicators import TechnicalIndicators, get_signals
from utils import get_signal_emoji
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def render_screener(binance_api, interval="1h"):
    """
    Kripto para tarayıcı sayfasını oluşturur.
    
    Args:
        binance_api (BinanceAPI): Binance API nesnesi
        interval (str): Zaman aralığı
    """
    try:
        st.title("🔍 Kripto Para Tarayıcı")
        
        # Filtre seçenekleri
        st.subheader("Filtreler")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_volume = st.number_input(
                "Min. 24s Hacim (USDT)",
                min_value=0,
                value=1000000,
                step=1000000
            )
        
        with col2:
            signal_filter = st.selectbox(
                "Sinyal Filtresi",
                options=["Tümü", "Alış Sinyalleri", "Satış Sinyalleri", "Güçlü Alış", "Güçlü Satış", "Nötr"]
            )
        
        with col3:
            sort_by = st.selectbox(
                "Sıralama",
                options=["Hacim (Azalan)", "Hacim (Artan)", "Değişim (Azalan)", "Değişim (Artan)"]
            )
        
        # Tarama başlat
        if st.button("Taramayı Başlat", type="primary"):
            # Yükleme göstergesi
            with st.spinner("Kripto paralar taranıyor... Bu işlem birkaç dakika sürebilir."):
                # En yüksek hacimli kripto paraları al
                top_symbols = binance_api.get_top_symbols_by_volume(limit=50)
                
                if not top_symbols:
                    st.error("Piyasa verileri alınamadı. Lütfen daha sonra tekrar deneyin.")
                    return
                
                # Hacim filtresini uygula
                filtered_symbols = [
                    ticker for ticker in top_symbols 
                    if float(ticker.get('quoteVolume', 0)) >= min_volume
                ]
                
                # Sonuçları saklamak için liste
                results = []
                
                # İlerleme çubuğu
                progress_bar = st.progress(0)
                
                # Her sembol için teknik analiz yap
                for i, ticker in enumerate(filtered_symbols):
                    symbol = ticker['symbol']
                    
                    # İlerleme çubuğunu güncelle
                    progress = (i + 1) / len(filtered_symbols)
                    progress_bar.progress(progress)
                    
                    # Durum mesajını güncelle
                    st.caption(f"İşleniyor: {symbol} ({i+1}/{len(filtered_symbols)})")
                    
                    try:
                        # Kline verilerini al
                        df = binance_api.get_klines(symbol=symbol, interval=interval, limit=100)
                        
                        if df.empty:
                            continue
                        
                        # Teknik indikatörleri hesapla
                        indicators = TechnicalIndicators(df)
                        df_with_indicators = indicators.add_all_indicators()
                        
                        # Sinyalleri al
                        signals = get_signals(df_with_indicators)
                        
                        # Fiyat bilgilerini al
                        last_price = df_with_indicators['close'].iloc[-1]
                        previous_price = df_with_indicators['close'].iloc[-2]
                        price_change = ((last_price - previous_price) / previous_price) * 100
                        
                        # Sonuçları listeye ekle
                        results.append({
                            "Sembol": symbol,
                            "Son Fiyat": last_price,
                            "24s Değişim (%)": float(ticker.get('priceChangePercent', 0)),
                            "24s Hacim": float(ticker.get('quoteVolume', 0)),
                            "RSI": signals['rsi']['value'],
                            "MACD": signals['macd']['value'],
                            "BB (%)": signals['bollinger']['value'],
                            "RSI Sinyal": signals['rsi']['signal'],
                            "MACD Sinyal": signals['macd']['signal'],
                            "BB Sinyal": signals['bollinger']['signal'],
                            "Genel Sinyal": signals['overall']['signal'],
                            "Sinyal Puanı": signals['overall']['value']
                        })
                    except Exception as e:
                        logger.error(f"{symbol} için analiz yapılırken hata oluştu: {e}")
                        continue
                
                # İlerleme çubuğunu kaldır
                progress_bar.empty()
                
                # Sonuçları DataFrame'e dönüştür
                if results:
                    results_df = pd.DataFrame(results)
                    
                    # Sinyal filtresini uygula
                    if signal_filter == "Alış Sinyalleri":
                        results_df = results_df[results_df['Sinyal Puanı'] > 0]
                    elif signal_filter == "Satış Sinyalleri":
                        results_df = results_df[results_df['Sinyal Puanı'] < 0]
                    elif signal_filter == "Güçlü Alış":
                        results_df = results_df[results_df['Genel Sinyal'] == "GÜÇLÜ AL"]
                    elif signal_filter == "Güçlü Satış":
                        results_df = results_df[results_df['Genel Sinyal'] == "GÜÇLÜ SAT"]
                    elif signal_filter == "Nötr":
                        results_df = results_df[results_df['Sinyal Puanı'] == 0]
                    
                    # Sıralama uygula
                    if sort_by == "Hacim (Azalan)":
                        results_df = results_df.sort_values(by="24s Hacim", ascending=False)
                    elif sort_by == "Hacim (Artan)":
                        results_df = results_df.sort_values(by="24s Hacim", ascending=True)
                    elif sort_by == "Değişim (Azalan)":
                        results_df = results_df.sort_values(by="24s Değişim (%)", ascending=False)
                    elif sort_by == "Değişim (Artan)":
                        results_df = results_df.sort_values(by="24s Değişim (%)", ascending=True)
                    
                    # Emoji ekle
                    results_df['Genel Sinyal'] = results_df['Genel Sinyal'].apply(
                        lambda x: f"{x} {get_signal_emoji(x)}"
                    )
                    
                    # Sonuçları göster
                    st.subheader(f"Tarama Sonuçları ({len(results_df)} kripto para)")
                    
                    # Gösterilecek sütunları seç
                    display_columns = [
                        "Sembol", "Son Fiyat", "24s Değişim (%)", "24s Hacim",
                        "RSI", "MACD", "BB (%)", "Genel Sinyal"
                    ]
                    
                    st.dataframe(
                        results_df[display_columns],
                        column_config={
                            "Sembol": st.column_config.TextColumn("Sembol"),
                            "Son Fiyat": st.column_config.NumberColumn(
                                "Son Fiyat",
                                format="$%.4f"
                            ),
                            "24s Değişim (%)": st.column_config.NumberColumn(
                                "24s Değişim (%)",
                                format="%.2f%%"
                            ),
                            "24s Hacim": st.column_config.NumberColumn(
                                "24s Hacim",
                                format="$%.2f"
                            ),
                            "RSI": st.column_config.NumberColumn(
                                "RSI",
                                format="%.2f"
                            ),
                            "MACD": st.column_config.NumberColumn(
                                "MACD",
                                format="%.6f"
                            ),
                            "BB (%)": st.column_config.NumberColumn(
                                "BB (%)",
                                format="%.2f"
                            ),
                            "Genel Sinyal": st.column_config.TextColumn("Genel Sinyal")
                        },
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # CSV indirme butonu
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="CSV olarak indir",
                        data=csv,
                        file_name=f"kripto_tarama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("Filtrelere uygun kripto para bulunamadı.")
            
            # Son güncelleme zamanı
            st.caption(f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            # Tarama başlatılmadığında gösterilecek bilgi
            st.info("Kripto para taraması yapmak için 'Taramayı Başlat' butonuna tıklayın.")
            st.caption("Not: Tarama işlemi, seçilen filtrelere bağlı olarak birkaç dakika sürebilir.")
    
    except Exception as e:
        logger.error(f"Tarayıcı oluşturulurken hata oluştu: {e}")
        st.error(f"Bir hata oluştu: {e}")