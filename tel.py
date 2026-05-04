"""
📱 Cep Telefonu Algılama Sistemi
YOLOv8 ile gerçek zamanlı nesne algılama
Telefon 5 saniye boyunca sürekli görünürse YouTube linki açılır
Sol üstte yeşil çember + kırmızı geri sayım göstergesi
"""

import cv2
import webbrowser
import time
from ultralytics import YOLO

# ─────────────────────────────────────────
# AYARLAR
# ─────────────────────────────────────────
YOUTUBE_URL         = "https://www.youtube.com/shorts/eQ9ByDhO-DQ"
COOLDOWN_SECONDS    = 15      # Video açıldıktan sonra tekrar açılmaması için bekleme
CONFIDENCE_THRESH   = 0.50    # Minimum güven skoru
CAMERA_INDEX        = 0
FRAME_WIDTH         = 1280
FRAME_HEIGHT        = 720
MODEL_NAME          = "yolov8n.pt"

COUNTDOWN_TARGET    = 3       # Kaç saniye görünürse video açılır

CELL_PHONE_CLASS_ID = 67

# ─── Çember ayarları ───
CX, CY  = 80, 90              # Çember merkezi (sol üst)
RADIUS  = 55                  # Çember yarıçapı


# ─────────────────────────────────────────
# ÇEMBER GERİ SAYIM ÇİZİCİ
# ─────────────────────────────────────────

def draw_countdown_circle(frame, elapsed: float, target: int, phone_visible: bool):
    """
    Sol üstte yuvarlak geri sayım göstergesi çizer.
      - Dış çember dolum yayı : yeşil
      - İçindeki sayı         : kırmızı (1 → 5)
      - Telefon yoksa         : gri nokta bekleme ikonu
    """
    # ── Yarı saydam arka plan diski ──────────────────
    overlay = frame.copy()
    cv2.circle(overlay, (CX, CY), RADIUS + 10, (20, 20, 20), -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)

    # ── Arka plan halkası (koyu gri) ─────────────────
    cv2.circle(frame, (CX, CY), RADIUS, (60, 60, 60), 10, cv2.LINE_AA)

    if phone_visible and elapsed > 0:
        # Dolum oranı → saat yönünde yay
        ratio   = min(elapsed / target, 1.0)
        sweep   = int(ratio * 360)

        # Yeşil dolum yayı (12 konumundan başlar = -90°)
        cv2.ellipse(
            frame,
            (CX, CY),
            (RADIUS, RADIUS),
            0,
            -90,
            -90 + sweep,
            (0, 230, 50),   # yeşil
            10,
            cv2.LINE_AA
        )

        # İçindeki sayı: 1'den 5'e
        display_num = min(int(elapsed) + 1, target)
        num_text    = str(display_num)

        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.4
        thickness  = 3
        (tw, th), _ = cv2.getTextSize(num_text, font, font_scale, thickness)
        tx = CX - tw // 2
        ty = CY + th // 2

        # Gölge (okunabilirlik)
        cv2.putText(frame, num_text, (tx + 2, ty + 2), font, font_scale,
                    (0, 0, 0), thickness + 2, cv2.LINE_AA)
        # Kırmızı sayı
        cv2.putText(frame, num_text, (tx, ty), font, font_scale,
                    (0, 0, 220), thickness, cv2.LINE_AA)

    else:
        # Telefon yok → üç gri nokta
        for dx in (-16, 0, 16):
            cv2.circle(frame, (CX + dx, CY), 5, (130, 130, 130), -1, cv2.LINE_AA)


# ─────────────────────────────────────────
# BOUNDING BOX ÇİZİCİ
# ─────────────────────────────────────────

def draw_boxes(frame, boxes):
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 220, 0), 2, cv2.LINE_AA)

        label = f"Cell Phone {conf:.0%}"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        cv2.rectangle(frame, (x1, y1 - lh - 10), (x1 + lw + 6, y1), (0, 180, 0), -1)
        cv2.putText(frame, label, (x1 + 3, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2, cv2.LINE_AA)


# ─────────────────────────────────────────
# ALT BİLGİ ÇUBUĞU
# ─────────────────────────────────────────

def draw_status_bar(frame, phone_visible, elapsed, target, cooldown_left):
    h, w = frame.shape[:2]
    cv2.rectangle(frame, (0, h - 34), (w, h), (18, 18, 18), -1)

    if cooldown_left > 0:
        msg   = f"Bekleniyor – tekrar {cooldown_left}s sonra aktif  |  Cikis: Q"
        color = (60, 160, 255)
    elif phone_visible:
        remaining_s = max(0, target - int(elapsed))
        msg   = f"Telefon goruldu! {remaining_s}s sonra video aciliyor...  |  Cikis: Q"
        color = (0, 220, 80)
    else:
        msg   = "Telefon bekleniyor...  |  Cikis: Q"
        color = (150, 150, 150)

    cv2.putText(frame, msg, (12, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.52, color, 1, cv2.LINE_AA)


# ─────────────────────────────────────────
# ANA DÖNGÜ
# ─────────────────────────────────────────

def main():
    print("=" * 57)
    print("  📱  Cep Telefonu Algilama  |  YOLOv8 + Geri Sayim")
    print("=" * 57)
    print(f"  Model         : {MODEL_NAME}")
    print(f"  Geri sayim    : {COUNTDOWN_TARGET} saniye")
    print(f"  Cooldown      : {COOLDOWN_SECONDS} saniye")
    print(f"  Guven esigi   : {CONFIDENCE_THRESH:.0%}")
    print(f"  YouTube URL   : {YOUTUBE_URL}")
    print("=" * 57)

    print("\n[*] Model yukleniyor...")
    model = YOLO(MODEL_NAME)
    print("[✓] Model hazir.\n")

    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[HATA] Kamera ({CAMERA_INDEX}) acılamadı!")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, 30)

    phone_seen_since = None   # Telefonun ilk görüldüğü zaman
    last_triggered   = 0.0   # Son YouTube açılma zamanı
    total_opened     = 0

    print("[*] Kamera aktif. Cıkmak icin 'Q' basin.\n")

    # ... (ana döngü başlangıcı)
    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        # AYNA YANSIMASINI DÜZELTEN SATIR:
        # 1: Yatay çevirme (Mirror effect fix), 0: Dikey, -1: Her iki eksen
        frame = cv2.flip(frame, 1) 

        results = model(frame, verbose=False, conf=CONFIDENCE_THRESH)
# ... (kodun geri kalanı aynı kalacak)
        phone_boxes = [
            box
            for r in results
            for box in r.boxes
            if int(box.cls[0]) == CELL_PHONE_CLASS_ID
        ]

        now           = time.time()
        phone_visible = len(phone_boxes) > 0
        cooldown_left = max(0, int(COOLDOWN_SECONDS - (now - last_triggered)))

        # ── Geri sayım mantığı ──────────────────────────
        if phone_visible:
            if phone_seen_since is None:
                phone_seen_since = now      # İlk görülme → saymaya başla
            elapsed = now - phone_seen_since
        else:
            phone_seen_since = None         # Telefon kayboldu → sıfırla
            elapsed = 0.0

        # 5 saniye doldu + cooldown bitti → YouTube aç!
        if phone_visible and elapsed >= COUNTDOWN_TARGET and cooldown_left == 0:
            total_opened    += 1
            last_triggered   = now
            phone_seen_since = None
            elapsed          = 0.0
            print(f"[✓] Video acildi! (#{total_opened})  YouTube: {YOUTUBE_URL}")
            webbrowser.open(YOUTUBE_URL)

        # ── Çizim ──────────────────────────────────────
        draw_boxes(frame, phone_boxes)
        draw_countdown_circle(frame, elapsed, COUNTDOWN_TARGET, phone_visible)
        draw_status_bar(frame, phone_visible, elapsed, COUNTDOWN_TARGET, cooldown_left)

        cv2.imshow("Cep Telefonu Algilama  –  YOLOv8", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), ord("Q"), 27):
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"\n[*] Program sonlandi. Toplam video acilma: {total_opened}")


if __name__ == "__main__":
    main()
