import streamlit as st
import time
import logging
from datetime import datetime
from config import (
    APP_TITLE, APP_ICON, THEME_COLOR, SECONDARY_COLOR, 
    BACKGROUND_COLOR, TEXT_COLOR, CARD_BACKGROUND, ACCENT_COLOR
)
from components import (
    render_sidebar,
    render_dashboard,
    render_loading_placeholder,
    render_market_overview,
    render_screener
)

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sayfa yapılandırması
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern dashboard teması
st.markdown(f"""
<style>
    /* Ana tema renkleri */
    :root {{
        --primary-color: #4CAF50;
        --secondary-color: #66BB6A;
        --background-color: #000924;
        --text-color: white;
        --card-background: #001a3d;
        --accent-color: #4CAF50;
    }}
    
    /* Body ve HTML arka planı */
    html, body {{
        background-color: var(--background-color) !important;
    }}
    
    /* Genel stil ayarları */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 95%;
        background-color: var(--background-color);
    }}
    
    /* Ana sayfa arka planı */
    .stApp {{
        background-color: var(--background-color);
    }}
    
    /* Ana içerik alanı */
    .main {{
        background-color: var(--background-color);
    }}
    
    /* Streamlit bileşenlerinin stilini özelleştirme */
    .stProgress > div > div > div > div {{
        background-color: var(--primary-color);
    }}
    
    /* Butonlar */
    .stButton > button {{
        background-color: var(--primary-color);
        color: white;
        border-radius: 4px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }}
    .stButton > button:hover {{
        background-color: var(--secondary-color);
        color: white;
    }}
    
    /* Sekmeler */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background-color: var(--card-background);
        border-radius: 12px 12px 0 0;
        padding: 5px 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
        box-shadow: 0 -4px 10px rgba(0, 0, 0, 0.1);
    }}
    .stTabs [data-baseweb="tab"] {{
        height: 54px;
        white-space: pre-wrap;
        background-color: rgba(0, 0, 0, 0.2);
        border-radius: 10px 10px 0 0;
        gap: 8px;
        padding: 10px 24px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-bottom: none;
        margin-right: 2px;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background-color: rgba(76, 175, 80, 0.1);
        transform: translateY(-3px);
    }}
    .stTabs [aria-selected="true"] {{
        background-color: var(--primary-color);
        box-shadow: 0 -4px 10px rgba(76, 175, 80, 0.2);
        transform: translateY(-5px);
    }}
    
    /* Metrik kartları */
    [data-testid="stMetric"] {{
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }}
    [data-testid="stMetricLabel"] {{
        font-size: 1rem;
        font-weight: 600;
    }}
    [data-testid="stMetricValue"] {{
        font-size: 1.5rem;
        font-weight: 700;
    }}
    [data-testid="stMetricDelta"] {{
        font-size: 0.9rem;
    }}
    
    /* Veri tabloları */
    .stDataFrame {{
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid var(--card-background);
    }}
    .stDataFrame [data-testid="stTable"] {{
        background-color: var(--card-background);
    }}
    .stDataFrame thead tr th {{
        background-color: var(--secondary-color);
        color: white;
    }}
    
    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: var(--card-background);
        border-right: 2px solid rgba(255, 255, 255, 0.1);
    }}
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    [data-testid="stSidebarContent"] {{
        background-color: #000924;
    }}
    
    /* Başlıklar */
    h1, h2, h3, h4, h5, h6 {{
        color: white;
    }}
    h1 {{
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        color: white;
    }}
    h2 {{
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: white;
    }}
    h3 {{
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: white;
    }}
    
    /* Grafik konteyner */
    .stPlotlyChart {{
        background-color: var(--card-background);
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    /* Selectbox */
    .stSelectbox {{
        border-radius: 8px;
    }}
    .stSelectbox > div > div {{
        background-color: var(--card-background);
        border-radius: 8px;
    }}
</style>
""", unsafe_allow_html=True)

def main():
    """
    Ana uygulama fonksiyonu.
    """
    try:
        # Yan menüyü oluştur
        (
            selected_symbol,
            selected_interval,
            data_limit,
            selected_indicators,
            auto_refresh,
            refresh_interval,
            api_connected,
            binance_api
        ) = render_sidebar()
        
        # API bağlantısı yoksa uyarı göster
        if not api_connected:
            st.warning("Binance API bağlantısı kurulamadı. Lütfen API anahtarlarınızı kontrol edin.")
            st.info("API anahtarlarınızı .env dosyasına ekleyin.")
            return
        
        # Sekmeleri oluştur
        tabs = st.tabs(["📊 Analiz Paneli", "🌍 Piyasa Genel Bakış", "🔍 Kripto Para Tarayıcı"])
        
        # Analiz Paneli sekmesi
        with tabs[0]:
            render_dashboard(
                symbol=selected_symbol,
                interval=selected_interval,
                data_limit=data_limit,
                selected_indicators=selected_indicators,
                binance_api=binance_api
            )
        
        # Piyasa Genel Bakış sekmesi
        with tabs[1]:
            render_market_overview(binance_api=binance_api)
        
        # Kripto Para Tarayıcı sekmesi
        with tabs[2]:
            render_screener(
                binance_api=binance_api,
                interval=selected_interval
            )
        
        # Otomatik yenileme
        if auto_refresh:
            refresh_seconds = {
                "10 saniye": 10,
                "30 saniye": 30,
                "1 dakika": 60,
                "5 dakika": 300
            }
            
            seconds = refresh_seconds.get(refresh_interval, 30)
            
            st.caption(f"Sayfa {seconds} saniyede bir otomatik olarak yenilenecek.")
            time.sleep(seconds)
            st.experimental_rerun()
    
    except Exception as e:
        logger.error(f"Uygulama çalıştırılırken hata oluştu: {e}")
        st.error(f"Bir hata oluştu: {e}")

if __name__ == "__main__":
    main()