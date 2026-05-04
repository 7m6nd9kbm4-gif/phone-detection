# phone-detection
YOLOv8 ile gerçek zamanlı cep telefonu algılama sistemi. Telefon belirli süre görünürse otomatik aksiyon (YouTube açma) tetikler.

İnstagram Link: https://www.instagram.com/reel/DX7KwO9N0kr/?igsh=a2NxMXl2ZDF1NHJr
# Cep Telefonu Algılama Sistemi

Bu proje, YOLOv8 kullanarak gerçek zamanlı olarak kameradan cep telefonu algılar. Telefon belirli bir süre boyunca görünürse otomatik olarak bir aksiyon tetikler (örneğin bir YouTube videosu açar).

## Özellikler

- Gerçek zamanlı nesne algılama
- Sadece "cell phone" sınıfını tespit eder
- Geri sayım sistemi ile süre takibi
- Cooldown mekanizması ile tekrar tetiklenmeyi engeller
- Otomatik tarayıcı açma özelliği

## Nasıl Çalışır

Program kamera görüntüsünü sürekli olarak işler ve YOLOv8 modeli ile nesne tespiti yapar. Eğer bir telefon algılanırsa geri sayım başlar. Telefon belirlenen süre boyunca görünmeye devam ederse, sistem otomatik olarak tanımlı linki açar. İşlem sonrası belirli bir süre tekrar tetikleme yapılmaz.

## Kurulum

Gerekli kütüphaneleri yüklemek için:

pip install ultralytics opencv-python

## Çalıştırma

python main.py

## Ayarlar

Kod içerisinde aşağıdaki parametreler değiştirilebilir:

- COUNTDOWN_TARGET: Telefonun kaç saniye görünmesi gerektiği
- COOLDOWN_SECONDS: Tekrar tetikleme için bekleme süresi
- CONFIDENCE_THRESH: Algılama güven eşiği
- YOUTUBE_URL: Açılacak bağlantı

## Notlar

- YOLO modeli ilk çalıştırmada indirilebilir
- Kamera index değeri sistemine göre değiştirilebilir
- Gerçek zamanlı performans kullanılan donanıma bağlıdır

## Lisans

Bu proje MIT lisansı ile lisanslanmıştır.
