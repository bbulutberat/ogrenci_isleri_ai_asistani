import os
import fitz
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter

print("⏳ Gelişmiş PAU RAG Veritabanı Oluşturucu V2 Başlatılıyor...")

# ============================================================
# 1. TEMEL AYARLAR
# ============================================================
# E5-Large: Türkçe'de E5-base'den belirgin şekilde daha iyi (~%10-15 fark)
# query: ve passage: prefix'leri E5 ailesi için ZORUNLU
Settings.embed_model = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-large",
    query_instruction="query: ",
    text_instruction="passage: "
)
Settings.llm = None

# Madde bütünlüğünü koruyan chunk ayarları
Settings.node_parser = SentenceSplitter(
    chunk_size=400,
    chunk_overlap=80,
    paragraph_separator="\n\n",
    secondary_chunking_regex=r"MADDE \d+",
)

# ============================================================
# 2. METADATA ÇIKARMA — Fakülte + Konu kategorisi
# ============================================================
def extract_metadata(filename):
    isim = os.path.basename(filename).lower()

    # Fakülte / kapsam tespiti
    if "mühendislik" in isim or "muhendislik" in isim:
        kapsam = "muhendislik"
    elif "tıp" in isim or "tip" in isim:
        kapsam = "tip"
    elif "turizm" in isim:
        kapsam = "turizm"
    elif "mimarlık" in isim or "mimarlik" in isim:
        kapsam = "mimarlik"
    elif "hukuk" in isim:
        kapsam = "hukuk"
    elif "iletişim" in isim or "iletisim" in isim:
        kapsam = "iletisim"
    elif "diş hekimliği" in isim or "dis hekimligi" in isim:
        kapsam = "dis_hekimligi"
    elif "fizyoterapi" in isim:
        kapsam = "fizyoterapi"
    elif "iktisadi" in isim or "idari" in isim:
        kapsam = "iibf"
    elif "teknoloji" in isim:
        kapsam = "teknoloji"
    elif "sağlık bilimleri" in isim or "saglik bilimleri" in isim:
        kapsam = "saglik_bilimleri"
    elif "müzik" in isim or "sahne" in isim:
        kapsam = "muzik_sahne"
    elif "denizli sağlık" in isim or "denizli saglik" in isim:
        kapsam = "denizli_saglik"
    else:
        kapsam = "genel"

    # Konu kategorisi (yatay etiket — birden fazla fakültenin yönergesi olabilir)
    if "staj" in isim:
        konu = "staj"
    elif "danışman" in isim or "danisman" in isim:
        konu = "danismanlik"
    elif "yatay" in isim or "dikey" in isim:
        konu = "gecis"
    elif "burs" in isim:
        konu = "burs"
    elif "disiplin" in isim:
        konu = "disiplin"
    elif "hazırlık" in isim or "hazirlik" in isim:
        konu = "hazirlik"
    elif "yandal" in isim or "çift anadal" in isim or "cift anadal" in isim:
        konu = "ek_program"
    elif "sınav" in isim or "sinav" in isim or "değerlendirme" in isim or "notland" in isim:
        konu = "sinav"
    elif "mezun" in isim:
        konu = "mezuniyet"
    elif "uluslararası" in isim or "değişim" in isim or "yurtdışı" in isim or "yurtdisi" in isim:
        konu = "uluslararasi"
    elif "engelli" in isim:
        konu = "engelli_destek"
    elif "topluluk" in isim:
        konu = "topluluk"
    elif "ilişik" in isim or "iliski" in isim:
        konu = "iliski_kesme"
    elif "kütüphane" in isim or "kutuphane" in isim:
        konu = "kutuphane"
    elif "muafiyet" in isim or "intibak" in isim:
        konu = "muafiyet"
    elif "lisansüstü" in isim or "lisansustu" in isim:
        konu = "lisansustu"
    elif "uzaktan" in isim:
        konu = "uzaktan_egitim"
    else:
        konu = "diger"

    return {
        "kapsam": kapsam,
        "konu": konu,
        "dosya_adi": isim
    }

# ============================================================
# 3. PDF'LERİ TEMİZ ŞEKİLDE OKU
# ============================================================
def temiz_pdf_oku(dosya_yolu):
    """PyMuPDF ile blok bazlı okuma — yapı korunur."""
    doc = fitz.open(dosya_yolu)
    metin = ""
    for sayfa in doc:
        bloklar = sayfa.get_text("blocks")
        for blok in bloklar:
            if len(blok) >= 7 and blok[6] == 0:  # text block
                icerik = blok[4].strip()
                if icerik:
                    metin += icerik + "\n"
        metin += "\n"
    doc.close()
    return metin

# ============================================================
# 4. PDF'LERİ OKU VE DOCUMENT'LARA DÖNÜŞTÜR
# ============================================================
pdf_klasoru = r"C:\Users\brtbl\OneDrive\Masaüstü\nihai sonuc\pdf_dosyalari"
hedef_klasor = r"C:\Users\brtbl\OneDrive\Masaüstü\nihai sonuc\pau_rag_db_v2"

print(f"\n📂 PDF klasörü: {pdf_klasoru}")

belgeler = []
pdf_dosyalari = [f for f in os.listdir(pdf_klasoru) if f.endswith(".pdf")]
print(f"📄 {len(pdf_dosyalari)} PDF bulundu.\n")

for i, dosya_adi in enumerate(pdf_dosyalari, 1):
    dosya_yolu = os.path.join(pdf_klasoru, dosya_adi)
    print(f"[{i}/{len(pdf_dosyalari)}] {dosya_adi}")

    try:
        metin = temiz_pdf_oku(dosya_yolu)
        if len(metin.strip()) < 50:
            print(f"   ⚠️  Çok kısa, atlanıyor.")
            continue

        metadata = extract_metadata(dosya_adi)
        print(f"   🏷️  kapsam={metadata['kapsam']}, konu={metadata['konu']}")

        belge = Document(text=metin, metadata=metadata)
        belgeler.append(belge)

    except Exception as e:
        print(f"   ❌ Hata: {e}")

print(f"\n✅ Toplam {len(belgeler)} belge işlendi.")

# ============================================================
# 5. VERİTABANINI OLUŞTUR VE KAYDET
# ============================================================
print("\n🧠 Vektör veritabanı oluşturuluyor (E5-Large embedding)...")
print("   ⏳ Bu işlem ilk seferde 5-10 dakika sürebilir (model indirilir).")

index = VectorStoreIndex.from_documents(belgeler, show_progress=True)
index.storage_context.persist(persist_dir=hedef_klasor)

print(f"\n🎉 BAŞARILI! Veritabanı kaydedildi: {hedef_klasor}")
print(f"📊 Özet: {len(belgeler)} belge, embedding model: multilingual-e5-large")