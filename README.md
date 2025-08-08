# Cryptoland - Kripto Trading Sinyal Uygulaması

Binance API kullanarak kripto para birimlerini listeleyen ve çeşitli teknik indikatörler ile al/sat sinyalleri üreten bir uygulama.

## Özellikler

- Binance API entegrasyonu
- Kripto para birimlerinin listelenmesi
- Teknik indikatörler (RSI, MACD, Bollinger Bands, vb.)
- Al/Sat sinyalleri
- Streamlit ile kullanıcı dostu arayüz
- Shadcn UI ile modern tasarım

## Kurulum

1. Repoyu klonlayın:
```
git clone https://github.com/yourusername/cryptoland.git
cd cryptoland
```

2. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```

3. `.env` dosyasını oluşturun ve Binance API anahtarlarınızı ekleyin:
```
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

4. Uygulamayı çalıştırın:
```
streamlit run app.py
```

## Proje Yapısı

- `app.py`: Ana Streamlit uygulaması
- `binance_api.py`: Binance API ile iletişim için fonksiyonlar
- `indicators.py`: Teknik indikatör hesaplamaları
- `utils.py`: Yardımcı fonksiyonlar
- `config.py`: Uygulama yapılandırması
- `components/`: UI bileşenleri