"""
PAU Öğrenci İşleri Asistanı — 7B GGUF + HİBRİT RAG
====================================================
İki kademeli retrieval:
1. ÖNCE SSS-RAG → çok benzer soru var mı?
   - Skor > 0.88 → DİREKT SSS cevabı (hızlı, model kullanmaz)
2. SSS yetersizse → Yönerge RAG
   - Reranker + akıllı filtre + model üretir

Avantajlar:
- Hız: Yüksek skor durumunda 0.5 saniyede cevap
- Doğruluk: SSS cevabı zaten doğrulanmış kabul ediliyor
- Esneklik: Yönergedeki detaylar gerektiğinde model çalışır
"""
# ============================================================
# OFFLINE MODE
# ============================================================
import os
os.environ["HF_HUB_OFFLINE"] = "1"          # HF Hub'a bağlanma
os.environ["TRANSFORMERS_OFFLINE"] = "1"    # Transformers'ı offline yap
os.environ["HF_DATASETS_OFFLINE"] = "1"     # Datasets'i offline yap

import re
import time
from pathlib import Path
from llama_cpp import Llama
from llama_index.core import StorageContext, load_index_from_storage, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.postprocessor import SentenceTransformerRerank

# ============================================================
# AYARLAR 
# ============================================================
_BASE = Path(__file__).parent
GGUF_YOLU     = str(_BASE / "qwen7b-pau-Q4_K_M.gguf")
RAG_DB_YOLU   = str(_BASE / "pau_rag_db_v2")
SSS_RAG_DB_YOLU = str(_BASE / "pau_sss_rag_db")

# ============================================================
# EŞİK DEĞERLERİ
# ============================================================
SSS_DIRECT_THRESHOLD = 0.88   # Bu üstünde SSS cevabı direkt gösterilir
RAG_LOW_CONFIDENCE = 0.3      # Yönerge RAG'da reranker bunun altındaysa "bilmiyorum"

# ============================================================
# SYSTEM PROMPT
# ============================================================
SYSTEM_PROMPT = """Sen Pamukkale Üniversitesi öğrenci işleri asistanısın. Görevin, sana verilen bağlama dayanarak öğrencilerin sorularını sade ve doğru bir şekilde yanıtlamak.

KURALLAR:
1. Sadece bağlamda olan bilgileri kullan, asla uydurma
2. Kısa ve net cevap ver (2-3 cümle)
3. Madde numaralarını söyleme (örn. "Madde 7'ye göre" yazma)
4. Bağlamda cevap yoksa "Bu konuda yönergede bir bilgi bulunmamaktadır. Doğru cevap için bölüm sekreterliğine veya öğrenci işlerine başvurmanızı öneririm." de"""


# ============================================================
# 1. RAG BİLEŞENLERİNİ YÜKLE (HEM YÖNERGE HEM SSS)
# ============================================================
def rag_yukle(use_reranker=True):
    print("[1/3] RAG bileşenleri yükleniyor (CPU)...")

    # Embedding (her iki RAG için ortak)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="intfloat/multilingual-e5-large",
        query_instruction="query: ",
        text_instruction="passage: ",
        device="cpu"
    )
    Settings.llm = None

    # YÖNERGE RAG (mevcut)
    print("Yönerge RAG yükleniyor...")
    yonerge_storage = StorageContext.from_defaults(persist_dir=RAG_DB_YOLU)
    yonerge_index = load_index_from_storage(yonerge_storage)

    # SSS RAG (yeni)
    print("SSS RAG yükleniyor...")
    sss_storage = StorageContext.from_defaults(persist_dir=SSS_RAG_DB_YOLU)
    sss_index = load_index_from_storage(sss_storage)

    # Reranker (sadece yönerge için)
    reranker = None
    if use_reranker:
        try:
            reranker = SentenceTransformerRerank(
                model="BAAI/bge-reranker-v2-m3",
                top_n=3,
                device="cpu"
            )
            print("Reranker yüklendi.")
        except Exception as e:
            print(f"Reranker yüklenemedi: {e}")
            reranker = None

    # Retrievers
    yonerge_top_k = 10 if reranker else 3
    yonerge_retriever = yonerge_index.as_retriever(similarity_top_k=yonerge_top_k)
    sss_retriever = sss_index.as_retriever(similarity_top_k=3)

    print("RAG hazır.\n")
    return yonerge_retriever, sss_retriever, reranker


# ============================================================
# 2. QWEN 7B GGUF MODELİNİ YÜKLE
# ============================================================
def model_yukle():
    print("[2/3] Qwen 2.5 7B GGUF yükleniyor (GPU)...")
    start = time.time()
    llm = Llama(
        model_path=GGUF_YOLU,
        n_ctx=4096,
        n_gpu_layers=-1,
        n_threads=8,
        n_batch=512,
        verbose=False,
    )
    print(f"Model yüklendi ({time.time()-start:.1f}s)\n")
    return llm


# ============================================================
# 3. SSS RAG SORGULAMA
# ============================================================
def sss_ara(soru, sss_retriever):
    """
    SSS'te benzer soru var mı kontrol et.
    Returns: (en_iyi_skor, en_iyi_eslesme) veya (0, None)
    """
    soru_formatted = f"query: {soru}"
    nodes = sss_retriever.retrieve(soru_formatted)

    if not nodes:
        return 0, None

    # En yüksek skorlu eşleşmeyi al
    en_iyi = max(nodes, key=lambda n: n.score if n.score else 0)
    skor = en_iyi.score if en_iyi.score else 0

    return skor, en_iyi


# ============================================================
# 4. YÖNERGE RAG SORGULAMA
# ============================================================
def yonerge_ara(soru, yonerge_retriever, reranker):
    soru_formatted = f"query: {soru}"
    soru_lower = soru.lower()

    # Akıllı filtre: lisansüstü filtresi
    lisansustu_kelimeler = ["lisansüstü", "lisansustu", "yüksek lisans", "yuksek lisans",
                            "doktora", "tezli", "tezsiz", "yl ", "phd"]
    lisansustu_sorusu = any(k in soru_lower for k in lisansustu_kelimeler)

    nodes = yonerge_retriever.retrieve(soru_formatted)

    if not lisansustu_sorusu:
        filtered_nodes = []
        for node in nodes:
            dosya = node.metadata.get("dosya_adi", "").lower()
            if "lisansüstü" not in dosya and "lisansustu" not in dosya:
                filtered_nodes.append(node)
        if filtered_nodes:
            nodes = filtered_nodes

    # Reranker
    if reranker is not None:
        nodes = reranker.postprocess_nodes(nodes, query_str=soru)

    context_parts = []
    kaynaklar = []
    for i, node in enumerate(nodes, 1):
        context_parts.append(f"[Bilgi {i}] {node.text}")
        kaynaklar.append({
            "dosya": node.metadata.get("dosya_adi", "bilinmiyor"),
            "skor": round(node.score, 3) if node.score else 0
        })

    context = "\n\n".join(context_parts)
    return context, kaynaklar


# ============================================================
# 5. HİBRİT CEVAP ÜRETİCİ
# ============================================================
def cevap_uret_hibrit(soru, llm, yonerge_retriever, sss_retriever, reranker, debug=False):
    """
    Strateji C:
    - SSS skoru >= 0.88 → direkt SSS cevabı (model çalışmaz)
    - SSS skoru < 0.88  → Yönerge RAG
    """
    # ÖNCE SSS'TE ARA
    sss_skor, sss_eslesme = sss_ara(soru, sss_retriever)

    if debug:
        print(f"\n--- DEBUG: SSS Skoru: {sss_skor:.3f} ---")
        if sss_eslesme:
            print(f"   En yakın SSS: {sss_eslesme.text[:80]}...")

    # ============================================================
    # YOL A: Yüksek skor → DİREKT SSS CEVABI
    # ============================================================
    if sss_skor >= SSS_DIRECT_THRESHOLD:
        cevap = sss_eslesme.metadata["cevap"]
        kaynak = {
            "yol": "SSS_DIRECT",
            "skor": round(sss_skor, 3),
            "kategori": sss_eslesme.metadata["kategori"],
            "eslesilen_soru": sss_eslesme.text,
        }
        return cevap, [kaynak]

    # ============================================================
    # YOL B: Düşük skor → YÖNERGE RAG
    # ============================================================
    yonerge_context, yonerge_kaynaklar = yonerge_ara(soru, yonerge_retriever, reranker)

    if debug:
        print(f"\n--- DEBUG: YÖNERGE RAG ---")
        for k in yonerge_kaynaklar:
            print(f"{k['dosya']} (skor: {k['skor']})")

    # Düşük güven kontrolü (mevcut sistemden)
    if reranker is not None and yonerge_kaynaklar:
        en_yuksek_skor = max(k['skor'] for k in yonerge_kaynaklar)
        if en_yuksek_skor < RAG_LOW_CONFIDENCE:
            cevap = ("Bu konuda yönergede net bir bilgi bulamadım. "
                     "Doğru cevap için bölüm sekreterliğine veya öğrenci işlerine başvurmanızı öneririm.")
            kaynak = {"yol": "BILMIYORUM", "skor": en_yuksek_skor}
            return cevap, [kaynak]

    # Model'le cevap üret
    user_msg = f"BAĞLAM:\n{yonerge_context}\n\nSORU: {soru}"
    prompt = (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user_msg}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )

    response = llm(
        prompt,
        max_tokens=150,
        temperature=0.2,
        top_p=0.85,
        repeat_penalty=1.15,
        stop=["<|im_end|>", "<|im_start|>"],
    )
    cevap = response["choices"][0]["text"].strip()

    cumleler = re.split(r'(?<=[.!?])\s+', cevap)
    if len(cumleler) > 3:
        cevap = ' '.join(cumleler[:3])

    # Yönerge kaynaklarına yol etiketi ekle
    for k in yonerge_kaynaklar:
        k["yol"] = "YONERGE_RAG"

    return cevap, yonerge_kaynaklar


# ============================================================
# 6. ANA DÖNGÜ
# ============================================================
def main():
    print("=" * 60)
    print("🎓 PAU ÖĞRENCİ İŞLERİ ASİSTANI (7B + HİBRİT RAG)")
    print("=" * 60)

    yonerge_retriever, sss_retriever, reranker = rag_yukle()
    llm = model_yukle()

    print("[3/3] ✅ Sistem hazır!\n")
    print("Çıkmak için 'q' yazın. Debug için soru sonuna ' /debug' ekleyin.\n")
    print("=" * 60)

    while True:
        soru = input("\n👨‍🎓 Soru:\n ").strip()

        if not soru:
            continue
        if soru.lower() in ["q", "çıkış", "cikis", "exit"]:
            print("👋 Görüşürüz!")
            break

        debug = False
        if soru.endswith(" /debug"):
            debug = True
            soru = soru[:-7].strip()

        try:
            print("⏳ Düşünüyor...")
            start = time.time()
            cevap, kaynaklar = cevap_uret_hibrit(
                soru, llm, yonerge_retriever, sss_retriever, reranker, debug=debug
            )
            sure = time.time() - start

            print(f"\n🤖 Asistan: {cevap}")
            print(f"⏱️  ({sure:.1f}s)")

            # Yol bilgisini göster
            if kaynaklar:
                yol = kaynaklar[0].get("yol", "?")
                yol_emoji = {
                    "SSS_DIRECT": "Direkt SSS",
                    "SSS_CONTEXT": "SSS + Model",
                    "YONERGE_RAG": "Yönerge",
                    "BILMIYORUM": "Bilinmiyor",
                }
                print(f"{yol_emoji.get(yol, yol)} (skor: {kaynaklar[0].get('skor', '?')})")

                if debug:
                    print(f"\n--- DEBUG: TÜM KAYNAKLAR ---")
                    for k in kaynaklar:
                        print(f"   {k}")

        except Exception as e:
            print(f"❌ Hata: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()