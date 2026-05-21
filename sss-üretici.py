import os
import fitz 
import json
import time
import google.generativeai as genai

# ============================================================
# AYARLAR
# ============================================================
GOOGLE_API_KEY = "AIzaSyBBF3d-LuIzHwt-xpAs7q67UZlgqaEbCDQ"
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

pdf_klasoru = "./pdf_dosyalari"
cikti_dosyasi = "pau_dataset_v2.json"
takip_dosyasi = "islenen_pdfler_v2.txt"
PARCA_BOYUTU = 3000

# ============================================================
# HAFIZA SİSTEMİ
# Takip dosyasındaki format:
#   "dosya.pdf"            → PDF tamamen tamamlandı
#   "dosya.pdf::parca::3"  → 3. parça tamamlandı, devam edecek
# ============================================================
islenen_pdfler = set()       # tamamen biten PDF'ler
parca_ilerleme = {}          # yarım kalanlar: {dosya_adi: son_tamamlanan_parca_no}

if os.path.exists(takip_dosyasi):
    with open(takip_dosyasi, "r", encoding="utf-8") as f:
        for satir in f:
            satir = satir.strip()
            if not satir:
                continue
            if "::parca::" in satir:
                bolumler = satir.split("::parca::")
                dosya = bolumler[0]
                parca_no = int(bolumler[1])
                # Aynı dosya için en yüksek parça numarasını tut
                parca_ilerleme[dosya] = max(parca_ilerleme.get(dosya, 0), parca_no)
            else:
                islenen_pdfler.add(satir)

tum_veriler = []
if os.path.exists(cikti_dosyasi):
    try:
        with open(cikti_dosyasi, "r", encoding="utf-8") as f:
            tum_veriler = json.load(f)
        print(f" Mevcut veri seti yüklendi: {len(tum_veriler)} soru zaten var.")
    except:
        tum_veriler = []

# ============================================================
# PROMPT
# ============================================================
sistem_komutu = """
Sen Pamukkale Üniversitesi öğrenci işleri asistanını eğitmek için veri seti hazırlayan bir uzmansın.
Sana bir yönerge metni verilecek. Aşağıdaki kurallara kesinlikle uy:

--- SORU ÜRETİMİ ---
Metnin uzunluğuna göre 10-25 arasında soru üret. Tekrar eden sorular üretme.
Soruları şu 3 formatta karıştırarak üret:
  - ÖĞRENCİ DİLİ: Günlük, doğal öğrenci ağzıyla (Örn: "Stajı geç başlatsam sorun olur mu?")
  - RESMİ DİL: Resmi akademik dille (Örn: "Staj başlangıç tarihinin ertelenmesinin yaptırımları nelerdir?")
  - NEGATİF ÖRNEK: Metinde cevabı OLMAYAN ama konuyla ilgili görünen bir soru.
    Bu sorunun response'u KESİNLİKLE şu olmalı: "Bu konuda yönergede bir bilgi bulunmamaktadır."
    Bu sorunun context'i boş string olmalı: ""

--- CEVAP YAZMA KURALLARI (ÇOK ÖNEMLİ) ---
1. Yönetmelik maddelerini KESİNLİKLE birebir kopyalama. Asla.
2. Cevabı bir üniversite görevlisinin öğrenciye SÖZLÜ olarak söyleyeceği gibi yaz.
3. Sade, anlaşılır Türkçe kullan. Resmi ama robotik değil.
4. Maksimum 2-3 cümle. Gereksiz uzatma.
5. Madde numaralarını cevaba yazma. ("Madde 7/a'ya göre..." gibi ifadeler KULLANMA)
6. Cevap context'teki bilgiyle %100 tutarlı olmalı, uydurma yapma.

--- FORMAT ---
Çıktıyı SADECE geçerli JSON dizisi olarak ver. Her obje şu anahtarları içermeli:
  - "instruction": Öğrencinin sorusu
  - "context": Cevabın dayandığı orijinal madde metni (sadece ilgili kısım, tüm paragraf değil)
  - "response": Asistanın sade ve sentezlenmiş cevabı

Örnek DOĞRU cevap stili:
  instruction: "İsteğe bağlı staj kaç gün yapılabilir?"
  context: "İsteğe bağlı staj süresi yirmi iş gününden az, otuz iş gününden fazla olamaz."
  response: "İsteğe bağlı stajınızı en az 20, en fazla 30 iş günü olarak yapabilirsiniz."

Örnek YANLIŞ cevap stili (BUNU YAPMA):
  response: "İsteğe bağlı staj süresi yirmi iş gününden az, otuz iş gününden fazla olamaz.
             Müfredatında zorunlu staj bulunan öğrenci isteğe bağlı stajını..."

İşte analiz edeceğin yönerge metni:
--------------------------------------------------
{metin}
--------------------------------------------------
"""

# ============================================================
# YARDIMCI FONKSİYONLAR
# ============================================================
def kalite_filtresi(veriler):
    """Context'i cevaba kopyalayan örnekleri temizler."""
    temiz = []
    atlanan = 0
    for ornek in veriler:
        ctx = ornek.get("context", "").strip()
        resp = ornek.get("response", "").strip()
        if ctx and resp and ctx[:80].lower() == resp[:80].lower():
            atlanan += 1
            continue
        temiz.append(ornek)
    return temiz, atlanan


def kaydet(veriler, dosya_adi_pdf, parca_no=None, tamamlandi=False):
    """Veriyi JSON'a, ilerlemeyi takip dosyasına kaydeder."""
    with open(cikti_dosyasi, "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=4)

    with open(takip_dosyasi, "a", encoding="utf-8") as f:
        if tamamlandi:
            f.write(dosya_adi_pdf + "\n")
        else:
            f.write(f"{dosya_adi_pdf}::parca::{parca_no}\n")


# ============================================================
# ANA DÖNGÜ
# ============================================================
print("PAU Dataset Üretici V2 Başladı\n")

for dosya_adi in sorted(os.listdir(pdf_klasoru)):
    if not dosya_adi.endswith(".pdf"):
        continue

    # Tamamen tamamlanmış PDF'leri atla
    if dosya_adi in islenen_pdfler:
        print(f"Atlanıyor (tamamlandı): {dosya_adi}")
        continue

    dosya_yolu = os.path.join(pdf_klasoru, dosya_adi)
    print(f"\n📄 İşleniyor: {dosya_adi}")

    try:
        metin = ""
        doc = fitz.open(dosya_yolu)
        for sayfa in doc:
            metin += sayfa.get_text() + "\n"
        doc.close()

        if len(metin.strip()) < 50:
            print(f"Çok kısa, atlanıyor.")
            continue

        # Parçalara böl
        kelimeler = metin.split()
        parcalar = [
            " ".join(kelimeler[i:i + PARCA_BOYUTU])
            for i in range(0, len(kelimeler), PARCA_BOYUTU)
        ]
        toplam_parca = len(parcalar)
        print(f"{toplam_parca} parçaya bölündü.")

        # Kaldığımız parçadan devam et
        baslangic_parca = parca_ilerleme.get(dosya_adi, 0)
        if baslangic_parca > 0:
            print(f"{baslangic_parca}. parçaya kadar zaten işlendi, devam ediliyor...")

        dosya_yeni_veriler = []

        for parca_no, parca_metin in enumerate(parcalar, 1):
            # Daha önce tamamlanan parçaları geç
            if parca_no <= baslangic_parca:
                print(f"Parça {parca_no}/{toplam_parca} atlanıyor (zaten işlendi).")
                continue

            print(f"Parça {parca_no}/{toplam_parca} işleniyor...")

            hazir_prompt = sistem_komutu.replace("{metin}", parca_metin)
            response = model.generate_content(hazir_prompt)
            parca_veriler = json.loads(response.text)

            temiz, atlanan = kalite_filtresi(parca_veriler)
            if atlanan > 0:
                print(f"      🗑️  {atlanan} kopyala-yapıştır örnek atıldı.")

            dosya_yeni_veriler.extend(temiz)
            tum_veriler.extend(temiz)

            # Her parça bittikten sonra anında kaydet
            kaydet(tum_veriler, dosya_adi, parca_no=parca_no, tamamlandi=False)
            print(f"Parça {parca_no} kaydedildi. ({len(temiz)} soru) "
                  f"(Toplam: {len(tum_veriler)})")

            if parca_no < toplam_parca:
                time.sleep(5)

        # PDF tamamen bitti — takip dosyasına "tamamlandı" olarak işaretle
        kaydet(tum_veriler, dosya_adi, tamamlandi=True)
        islenen_pdfler.add(dosya_adi)

        print(f"{dosya_adi} tamamlandı. "
              f"({len(dosya_yeni_veriler)} soru) (Toplam: {len(tum_veriler)})")

        time.sleep(5)

    except json.JSONDecodeError as e:
        print(f"JSON parse hatası ({dosya_adi}): {e}")

    except Exception as e:
        print(f"Hata ({dosya_adi}): {e}")
        if "429" in str(e):
            print("API kotası doldu! Program durduruluyor.")
            print("Yeniden başlatınca kaldığı yerden devam edecek.")
            break

print(f"\n Toplam {len(tum_veriler)} soru üretildi.")
print(f"Çıktı: {cikti_dosyasi}")