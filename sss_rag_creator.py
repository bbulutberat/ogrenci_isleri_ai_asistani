"""
SSS-RAG Veritabanı Oluşturucu
==============================
pau_sss.json dosyasından ayrı bir vektör veritabanı oluşturur.
Bu DB hibrit retriever'da kullanılacak.

Mevcut yönerge RAG'ından FARKLI:
- Her chunk = bir SSS sorusu 
- Embed edilen metin = SORU
- Metadata: kategori + cevap birlikte saklanır
- Sadece SSS verisi, yönergeler dahil değil
"""
import json
import os
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# ============================================================
# AYARLAR
# ============================================================
SSS_JSON = "pau_sss.json"
SSS_RAG_DB_YOLU = r"C:\Users\brtbl\OneDrive\Masaüstü\pau asistan\pau_sss_rag_db"

# ============================================================
# E5 EMBEDDING
# ============================================================
print("⏳ E5-large embedding modeli yükleniyor...")
Settings.embed_model = HuggingFaceEmbedding(
    model_name="intfloat/multilingual-e5-large",
    query_instruction="query: ",
    text_instruction="passage: "
)
Settings.llm = None
print("Embedding hazır.\n")

# ============================================================
# SSS YÜKLE
# ============================================================
print("SSS verisi yükleniyor...")
with open(SSS_JSON, "r", encoding="utf-8") as f:
    sss_data = json.load(f)
print(f"{len(sss_data)} SSS örneği yüklendi.\n")

# ============================================================
# DOCUMENT NESNELERİ OLUŞTUR
# ============================================================
# ÖNEMLİ: text alanına SADECE soruyu koyuyoruz
# Çünkü kullanıcının sorusu bu sorulara benzeyecek
# Cevap metadata'da saklanır
print("Document nesneleri hazırlanıyor.")
belgeler = []
for i, sss in enumerate(sss_data):
    soru = sss["soru"]
    cevap = sss["cevap"]
    kategori = sss["kategori"]

    # Eşleşme için sadece soruyu embed et
    # Cevap metadata'da
    belge = Document(
        text=soru,
        metadata={
            "kategori": kategori,
            "cevap": cevap,
            "sss_id": i,
            "kaynak": "PAU_SSS"
        }
    )
    belgeler.append(belge)

print(f"{len(belgeler)} document oluşturuldu.\n")

# ============================================================
# VEKTÖR DB OLUŞTUR
# ============================================================
print(" Vektör veritabanı oluşturuluyor...")

index = VectorStoreIndex.from_documents(belgeler, show_progress=True)

# Kaydet
print(f"\n Veritabanı kaydediliyor: {SSS_RAG_DB_YOLU}")
os.makedirs(SSS_RAG_DB_YOLU, exist_ok=True)
index.storage_context.persist(persist_dir=SSS_RAG_DB_YOLU)

print(f"\n{'='*60}")
print(f"SSS-RAG DB: {SSS_RAG_DB_YOLU}")
print(f"Toplam: {len(belgeler)} SSS embed edildi")
print(f"{'='*60}")