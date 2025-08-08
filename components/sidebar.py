import streamlit as st
import pandas as pd
from config import DEFAULT_SYMBOLS, INTERVALS
from binance_api import BinanceAPI
import logging

# Loglama ayarları
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def render_sidebar():
    """
    Yan menüyü oluşturur ve seçilen parametreleri döndürür.
    
    Returns:
        tuple: Seçilen sembol, zaman aralığı, indikatörler ve diğer parametreler
    """
    try:
        # Modern sidebar stilini uygula
        st.markdown("""
        <style>
        .sidebar .sidebar-content {
            background-color: var(--card-background);
            border-right: 1px solid rgba(255, 255, 255, 0.05);
            box-shadow: 5px 0 15px rgba(0, 0, 0, 0.2);
        }
        
        /* Sidebar başlık stilini özelleştir */
        .sidebar .sidebar-content h1 {
            color: white;
            font-size: 26px !important;
            font-weight: 700 !important;
            margin-bottom: 25px !important;
            padding-bottom: 15px !important;
            border-bottom: 2px solid rgba(76, 175, 80, 0.3);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
        }
        
        /* Sidebar alt başlık stilini özelleştir */
        .sidebar .sidebar-content h3 {
            color: white;
            font-size: 18px !important;
            font-weight: 600 !important;
            margin-top: 30px !important;
            margin-bottom: 15px !important;
            display: flex;
            align-items: center;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Sidebar için Streamlit başlık stilleri */
        [data-testid="stSidebar"] h1 {
            color: white !important;
            font-size: 26px !important;
            font-weight: 700 !important;
            margin-bottom: 25px !important;
            padding-bottom: 15px !important;
            border-bottom: 2px solid rgba(76, 175, 80, 0.3);
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
        }
        
        [data-testid="stSidebar"] h3 {
            color: white !important;
            font-size: 18px !important;
            font-weight: 600 !important;
            margin-top: 30px !important;
            margin-bottom: 15px !important;
            display: flex;
            align-items: center;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            letter-spacing: 0.5px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Sidebar checkbox ve selectbox text renkleri */
        [data-testid="stSidebar"] .stCheckbox label span {
            color: white !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox label {
            color: white !important;
        }
        
        /* Sidebar seçim kutuları */
        .sidebar .sidebar-content .stSelectbox > div > div {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 10px !important;
            padding: 2px 5px !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
            transition: all 0.3s ease !important;
        }
        
        .sidebar .sidebar-content .stSelectbox > div > div:hover {
            border-color: var(--primary-color) !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.2) !important;
        }
        
        /* Sidebar checkbox stilini özelleştir */
        .sidebar .sidebar-content .stCheckbox > label {
            display: flex !important;
            align-items: center !important;
            padding: 10px 12px !important;
            background-color: rgba(0, 0, 0, 0.2) !important;
            border-radius: 10px !important;
            margin-bottom: 8px !important;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1) !important;
        }
        
        .sidebar .sidebar-content .stCheckbox > label:hover {
            background-color: rgba(76, 175, 80, 0.1) !important;
            transform: translateX(3px);
            border-color: rgba(76, 175, 80, 0.3) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2) !important;
        }
        
        /* Sidebar slider stilini özelleştir */
        .sidebar .sidebar-content .stSlider > div > div > div {
            background-color: var(--primary-color) !important;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3) !important;
        }
        
        .sidebar .sidebar-content .stSlider {
            padding: 10px 5px !important;
        }
        
        /* Sidebar bilgi kutusu stilini özelleştir */
        .sidebar .sidebar-content .stAlert {
            background-color: rgba(0, 0, 0, 0.2) !important;
            border-left: 4px solid var(--primary-color) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
            margin: 15px 0 !important;
        }
        
        /* Sidebar başarı mesajı stilini özelleştir */
        .sidebar .sidebar-content .stSuccess {
            background-color: rgba(76, 175, 80, 0.1) !important;
            border-left: 4px solid var(--primary-color) !important;
            border-radius: 10px !important;
            padding: 15px !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
            margin: 15px 0 !important;
        }
        
        /* Sidebar hata mesajı stilini özelleştir */
        .sidebar .sidebar-content .stError {
            background-color: rgba(244, 67, 54, 0.1) !important;
            border-left: 4px solid #F44336 !important;
            border-radius: 10px !important;
            padding: 15px !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1) !important;
            margin: 15px 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.sidebar.title("🛠️ Ayarlar")
        
        # API bağlantısı
        api_connected = False
        binance_api = BinanceAPI()
        
        if binance_api.client:
            api_connected = True
            st.sidebar.success("✅ Binance API bağlantısı kuruldu")
        else:
            st.sidebar.error("❌ Binance API bağlantısı kurulamadı")
            st.sidebar.info("API anahtarlarınızı .env dosyasına ekleyin")
        
        # Sembol seçimi
        st.sidebar.subheader("💱 Kripto Para Seçimi")
        
        # Sembol listesini al
        if api_connected:
            try:
                all_symbols = binance_api.get_all_symbols()
                top_symbols = [s['symbol'] for s in binance_api.get_top_symbols_by_volume(limit=10)]
                
                # Sembol listesini oluştur
                symbol_options = ["En Popüler 10"] + ["Tüm Semboller"] + top_symbols
                
                selected_symbol_option = st.sidebar.selectbox(
                    "Sembol Listesi",
                    options=symbol_options,
                    index=0
                )
                
                if selected_symbol_option == "En Popüler 10":
                    symbol_list = top_symbols
                elif selected_symbol_option == "Tüm Semboller":
                    symbol_list = all_symbols
                else:
                    symbol_list = [selected_symbol_option]
                
                selected_symbol = st.sidebar.selectbox(
                    "Kripto Para",
                    options=symbol_list,
                    index=0
                )
            except Exception as e:
                logger.error(f"Sembol listesi alınırken hata oluştu: {e}")
                selected_symbol = st.sidebar.selectbox(
                    "Kripto Para",
                    options=DEFAULT_SYMBOLS,
                    index=0
                )
        else:
            selected_symbol = st.sidebar.selectbox(
                "Kripto Para",
                options=DEFAULT_SYMBOLS,
                index=0
            )
        
        # Zaman aralığı seçimi
        st.sidebar.subheader("⏱️ Zaman Aralığı")
        
        selected_interval_name = st.sidebar.selectbox(
            "Mum Aralığı",
            options=list(INTERVALS.keys()),
            index=5  # 1 saat varsayılan
        )
        
        selected_interval = INTERVALS[selected_interval_name]
        
        # Veri limiti
        data_limit = st.sidebar.slider(
            "Veri Sayısı",
            min_value=50,
            max_value=1000,
            value=200,
            step=50
        )
        
        # İndikatör seçimleri
        st.sidebar.subheader("📊 Teknik İndikatörler")
        
        selected_indicators = []
        
        if st.sidebar.checkbox("RSI", value=True):
            selected_indicators.append("rsi")
        
        if st.sidebar.checkbox("MACD", value=True):
            selected_indicators.append("macd")
        
        if st.sidebar.checkbox("Bollinger Bands", value=True):
            selected_indicators.append("bollinger")
        
        if st.sidebar.checkbox("EMA (9, 21, 50)", value=True):
            selected_indicators.append("ema")
        
        if st.sidebar.checkbox("Stochastic", value=True):
            selected_indicators.append("stochastic")
        
        if st.sidebar.checkbox("Volume", value=True):
            selected_indicators.append("volume")
            
        if st.sidebar.checkbox("VWAP", value=True):
            selected_indicators.append("vwap")
            
        if st.sidebar.checkbox("VWEMA (5, 20)", value=True):
            selected_indicators.append("vwema")
            
        # Smart Money Concepts bölümü
        st.sidebar.subheader("💰 Smart Money Concepts")
        
        if st.sidebar.checkbox("Fair Value Gap (FVG)", value=True, help="Fiyat boşluklarını tespit eden ve kurumsal alım/satım bölgelerini gösteren indikatör"):
            selected_indicators.append("fvg")
            
        if st.sidebar.checkbox("Break of Structure (BOS)", value=True, help="Fiyatın önceki yüksek/düşük noktaları kırmasını tespit eden ve trend yönünü belirleyen indikatör"):
            selected_indicators.append("bos")
            
        if st.sidebar.checkbox("FVG + BOS Kombosu", value=True, help="Fair Value Gap ve Break of Structure sinyallerinin birlikte oluştuğu güçlü alım/satım fırsatlarını gösteren kombine indikatör"):
            selected_indicators.append("fvg_bos_combo")
        
        # Otomatik yenileme
        st.sidebar.subheader("🔄 Yenileme")
        
        auto_refresh = st.sidebar.checkbox("Otomatik Yenile", value=False)
        
        refresh_interval = None
        if auto_refresh:
            refresh_interval = st.sidebar.selectbox(
                "Yenileme Aralığı",
                options=["10 saniye", "30 saniye", "1 dakika", "5 dakika"],
                index=1
            )
        
        # Hakkında bölümü
        st.sidebar.markdown("""
        <div style="
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            margin: 25px 0 15px 0;
            padding-top: 15px;
        "></div>
        """, unsafe_allow_html=True)
        st.sidebar.subheader("ℹ️ Hakkında")
        st.sidebar.info(
            """
            Bu uygulama, Binance API kullanarak kripto para birimlerini izlemek ve 
            teknik analiz indikatörleri ile al/sat sinyalleri üretmek için tasarlanmıştır.
            
            **Not:** Bu uygulama finansal tavsiye vermez. Yatırım kararlarınızı kendi 
            araştırmalarınıza dayanarak vermelisiniz.
            """
        )
        
        return (
            selected_symbol,
            selected_interval,
            data_limit,
            selected_indicators,
            auto_refresh,
            refresh_interval,
            api_connected,
            binance_api
        )
    except Exception as e:
        logger.error(f"Yan menü oluşturulurken hata oluştu: {e}")
        # Varsayılan değerleri döndür
        return (
            DEFAULT_SYMBOLS[0],
            "1h",
            200,
            ["rsi", "macd", "bollinger", "ema", "volume", "vwap", "vwema"],
            False,
            None,
            False,
            None
        )