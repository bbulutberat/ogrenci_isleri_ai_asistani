"""
PAU Öğrenci İşleri Asistanı — FastAPI Backend
"""
import os
import sys
import uuid
import json
import time
from pathlib import Path
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# hibrit_asistan.py proje kök dizininde olduğu için path'e ekliyoruz
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(title="PAU Öğrenci İşleri Asistanı API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONVERSATIONS_FILE = Path(__file__).parent / "conversations.json"

# Singleton model state — model bir kez yüklenir, bellekte kalır
_state: dict = {
    "llm": None,
    "yonerge_retriever": None,
    "sss_retriever": None,
    "reranker": None,
    "loaded": False,
    "loading": False,
    "error": None,
}


def load_conversations() -> dict:
    if CONVERSATIONS_FILE.exists():
        try:
            with open(CONVERSATIONS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            # Bozuk dosyayı yedekle ve boş başla
            CONVERSATIONS_FILE.rename(CONVERSATIONS_FILE.with_suffix(".bak"))
            return {}
    return {}


def _to_serializable(obj):
    """NumPy / özel tipleri saf Python tiplerine dönüştür."""
    import numpy as np
    if isinstance(obj, dict):
        return {k: _to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_serializable(i) for i in obj]
    if isinstance(obj, (np.floating, np.float32, np.float64)):
        return float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    return obj


def save_conversations(conversations: dict) -> None:
    with open(CONVERSATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(_to_serializable(conversations), f, ensure_ascii=False, indent=2)


def get_assistant():
    if _state["loaded"]:
        return (
            _state["llm"],
            _state["yonerge_retriever"],
            _state["sss_retriever"],
            _state["reranker"],
        )

    if _state["error"]:
        raise RuntimeError(_state["error"])

    _state["loading"] = True
    try:
        from hibrit_asistan import rag_yukle, model_yukle

        _state["yonerge_retriever"], _state["sss_retriever"], _state["reranker"] = rag_yukle()
        _state["llm"] = model_yukle()
        _state["loaded"] = True
    except Exception as exc:
        _state["error"] = str(exc)
        raise
    finally:
        _state["loading"] = False

    return (
        _state["llm"],
        _state["yonerge_retriever"],
        _state["sss_retriever"],
        _state["reranker"],
    )


# ── Request models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    conversation_id: str
    message: str


class NewConversationRequest(BaseModel):
    title: str | None = None


# ── Endpoints ───────────────────────────────────────────────────────────────

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": _state["loaded"],
        "model_loading": _state["loading"],
        "model_error": _state["error"],
    }


@app.get("/api/conversations")
def list_conversations():
    convs = load_conversations()
    return sorted(convs.values(), key=lambda c: c["updated_at"], reverse=True)


@app.post("/api/conversations")
def create_conversation(req: NewConversationRequest | None = None):
    convs = load_conversations()
    conv_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    title = (req.title if req and req.title else None) or "Yeni Sohbet"
    conv = {
        "id": conv_id,
        "title": title,
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    convs[conv_id] = conv
    save_conversations(convs)
    return conv


@app.get("/api/conversations/{conv_id}")
def get_conversation(conv_id: str):
    convs = load_conversations()
    if conv_id not in convs:
        raise HTTPException(404, "Sohbet bulunamadı")
    return convs[conv_id]


@app.delete("/api/conversations/{conv_id}")
def delete_conversation(conv_id: str):
    convs = load_conversations()
    if conv_id not in convs:
        raise HTTPException(404, "Sohbet bulunamadı")
    del convs[conv_id]
    save_conversations(convs)
    return {"success": True}


@app.post("/api/chat")
def chat(req: ChatRequest):
    convs = load_conversations()
    if req.conversation_id not in convs:
        raise HTTPException(404, "Sohbet bulunamadı")

    try:
        llm, yonerge_retriever, sss_retriever, reranker = get_assistant()
    except Exception as exc:
        raise HTTPException(500, f"Model yüklenemedi: {exc}")

    from hibrit_asistan import cevap_uret_hibrit

    try:
        start = time.time()
        cevap, kaynaklar = cevap_uret_hibrit(
            req.message, llm, yonerge_retriever, sss_retriever, reranker
        )
        elapsed = round(time.time() - start, 2)
        # NumPy tiplerini saf Python tiplerine çevir
        kaynaklar = _to_serializable(kaynaklar)
    except Exception as exc:
        raise HTTPException(500, f"Cevap üretme hatası: {exc}")

    now = datetime.now().isoformat()
    conv = convs[req.conversation_id]

    conv["messages"].append({
        "id": str(uuid.uuid4()),
        "role": "user",
        "content": req.message,
        "timestamp": now,
    })
    conv["messages"].append({
        "id": str(uuid.uuid4()),
        "role": "assistant",
        "content": cevap,
        "sources": kaynaklar,
        "elapsed": elapsed,
        "timestamp": now,
    })

    # İlk mesajı başlık olarak kullan
    if len(conv["messages"]) == 2:
        conv["title"] = req.message[:60] + ("…" if len(req.message) > 60 else "")

    conv["updated_at"] = now
    save_conversations(convs)

    return {"answer": cevap, "sources": kaynaklar, "elapsed": elapsed}
