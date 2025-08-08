import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from utils import format_number, calculate_change
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def render_market_overview(binance_api):
    """
    Piyasa genel bakış sayfasını oluşturur.
    
    Args:
        binance_api (BinanceAPI): Binance API nesnesi
    """
    try:
        st.title("🌍 Kripto Piyasası Genel Bakış")
        
        # Veri yükleme göstergesi
        with st.spinner("Piyasa verileri yükleniyor..."):
            # En yüksek hacimli kripto paraları al
            top_symbols = binance_api.get_top_symbols_by_volume(limit=20)
            
            if not top_symbols:
                st.error("Piyasa verileri alınamadı. Lütfen daha sonra tekrar deneyin.")
                return
            
            # Veriyi DataFrame'e dönüştür
            market_data = []
            
            for ticker in top_symbols:
                symbol = ticker['symbol']
                price = float(ticker['lastPrice']) if 'lastPrice' in ticker else 0
                change_24h = float(ticker['priceChangePercent']) if 'priceChangePercent' in ticker else 0
                volume_24h = float(ticker['quoteVolume']) if 'quoteVolume' in ticker else 0
                
                market_data.append({
                    "Sembol": symbol,
                    "Fiyat": price,
                    "24s Değişim (%)": change_24h,
                    "24s Hacim": volume_24h
                })
            
            market_df = pd.DataFrame(market_data)
        
        # Piyasa özeti
        st.subheader("En Yüksek Hacimli Kripto Paralar")
        
        # Renklendirme fonksiyonu
        def color_change(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'white'
            return f'color: {color}'
        
        # Veri tablosunu göster
        st.dataframe(
            market_df,
            column_config={
                "Sembol": st.column_config.TextColumn("Sembol"),
                "Fiyat": st.column_config.NumberColumn(
                    "Fiyat",
                    format="$%.4f"
                ),
                "24s Değişim (%)": st.column_config.NumberColumn(
                    "24s Değişim (%)",
                    format="%.2f%%"
                ),
                "24s Hacim": st.column_config.NumberColumn(
                    "24s Hacim",
                    format="$%.2f"
                )
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Piyasa grafiği
        st.subheader("Piyasa Performansı")
        
        # Değişim grafiği
        fig = go.Figure()
        
        # Sıralama
        sorted_df = market_df.sort_values(by="24s Değişim (%)", ascending=True)
        
        # Renkleri belirle
        colors = ['green' if x > 0 else 'red' for x in sorted_df["24s Değişim (%)"]]
        
        # Grafik oluştur
        fig.add_trace(
            go.Bar(
                x=sorted_df["Sembol"],
                y=sorted_df["24s Değişim (%)"],
                marker_color=colors,
                text=sorted_df["24s Değişim (%)"].apply(lambda x: f"{x:.2f}%"),
                textposition='auto'
            )
        )
        
        fig.update_layout(
            title="24 Saatlik Fiyat Değişimi (%)",
            xaxis_title="Kripto Para",
            yaxis_title="Değişim (%)",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Hacim grafiği
        fig2 = go.Figure()
        
        # Hacime göre sırala
        volume_df = market_df.sort_values(by="24s Hacim", ascending=False)
        
        fig2.add_trace(
            go.Bar(
                x=volume_df["Sembol"],
                y=volume_df["24s Hacim"],
                marker_color='blue',
                text=volume_df["24s Hacim"].apply(lambda x: f"${format_number(x)}"),
                textposition='auto'
            )
        )
        
        fig2.update_layout(
            title="24 Saatlik İşlem Hacmi",
            xaxis_title="Kripto Para",
            yaxis_title="Hacim (USDT)",
            template="plotly_dark"
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # Kazananlar ve kaybedenler
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚀 En Çok Kazananlar")
            
            # En çok kazananları al
            gainers = market_df.sort_values(by="24s Değişim (%)", ascending=False).head(5)
            
            # Tabloyu göster
            st.dataframe(
                gainers,
                column_config={
                    "Sembol": st.column_config.TextColumn("Sembol"),
                    "Fiyat": st.column_config.NumberColumn(
                        "Fiyat",
                        format="$%.4f"
                    ),
                    "24s Değişim (%)": st.column_config.NumberColumn(
                        "24s Değişim (%)",
                        format="%.2f%%"
                    ),
                    "24s Hacim": st.column_config.NumberColumn(
                        "24s Hacim",
                        format="$%.2f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        
        with col2:
            st.subheader("📉 En Çok Kaybedenler")
            
            # En çok kaybedenleri al
            losers = market_df.sort_values(by="24s Değişim (%)").head(5)
            
            # Tabloyu göster
            st.dataframe(
                losers,
                column_config={
                    "Sembol": st.column_config.TextColumn("Sembol"),
                    "Fiyat": st.column_config.NumberColumn(
                        "Fiyat",
                        format="$%.4f"
                    ),
                    "24s Değişim (%)": st.column_config.NumberColumn(
                        "24s Değişim (%)",
                        format="%.2f%%"
                    ),
                    "24s Hacim": st.column_config.NumberColumn(
                        "24s Hacim",
                        format="$%.2f"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        
        # Son güncelleme zamanı
        st.caption(f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    except Exception as e:
        logger.error(f"Piyasa genel bakış oluşturulurken hata oluştu: {e}")
        st.error(f"Bir hata oluştu: {e}")