import json
import os
from typing import List, Dict, Any, Optional

import requests

try:
    import chromadb
    from chromadb.utils import embedding_functions
except Exception:
    chromadb = None
    embedding_functions = None


# Reduce Chroma telemetry noise in local dev
os.environ.setdefault('ANONYMIZED_TELEMETRY', 'False')

OLLAMA_HOST = os.environ.get('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_CHAT_MODEL = os.environ.get('OLLAMA_CHAT_MODEL', 'llama3')
OLLAMA_EMBED_MODEL = os.environ.get('OLLAMA_EMBED_MODEL', 'nomic-embed-text')
CHROMA_DIR = os.environ.get('CHROMA_DIR', '.chroma')
CHROMA_COLLECTION = os.environ.get('CHROMA_COLLECTION', 'unify_content')


def ollama_generate(prompt: str, model: Optional[str] = None, temperature: float = 0.2) -> str:
    url = f"{OLLAMA_HOST}/api/generate"
    payload = {
        "model": model or OLLAMA_CHAT_MODEL,
        "prompt": prompt,
        "options": {"temperature": temperature},
        "stream": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()
    except requests.exceptions.ConnectionError as ce:
        raise RuntimeError("Cannot connect to Ollama at %s. Is it running? Try `ollama serve`." % OLLAMA_HOST) from ce
    # Prefer non-stream single JSON
    try:
        data = r.json()
        if isinstance(data, dict) and data.get('response'):
            return data['response']
    except Exception:
        pass
    # If server still streamed, concatenate lines' response fields
    try:
        parts = []
        for line in r.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and 'response' in obj:
                    parts.append(obj['response'])
            except Exception:
                continue
        if parts:
            return ''.join(parts)
    except Exception:
        pass
    return r.text


def ollama_embed(text: str, model: Optional[str] = None) -> List[float]:
    url = f"{OLLAMA_HOST}/api/embeddings"
    payload = {"model": model or OLLAMA_EMBED_MODEL, "prompt": text}
    try:
        r = requests.post(url, json=payload, timeout=60)
        if r.status_code == 404:
            raise RuntimeError("Ollama embeddings endpoint returned 404. Ensure Ollama is running and the embedding model is available: `ollama pull %s`." % (model or OLLAMA_EMBED_MODEL))
        r.raise_for_status()
    except requests.exceptions.ConnectionError as ce:
        raise RuntimeError("Cannot connect to Ollama at %s. Is it running? Try `ollama serve`." % OLLAMA_HOST) from ce
    data = r.json()
    vec = data.get('embedding') or data.get('embeddings') or []
    if not vec:
        raise RuntimeError('Ollama did not return an embedding vector.')
    return vec


def _get_chroma_client():
    if chromadb is None:
        raise RuntimeError('ChromaDB not installed. Please add chromadb to requirements and install.')
    return chromadb.PersistentClient(path=CHROMA_DIR)


def get_collection():
    client = _get_chroma_client()
    try:
        coll = client.get_collection(CHROMA_COLLECTION)
    except Exception:
        coll = client.create_collection(CHROMA_COLLECTION)
    return coll


def add_documents(docs: List[Dict[str, Any]]):
    # docs: [{id, text, metadata}]
    if not docs:
        return
    coll = get_collection()
    ids = [str(d['id']) for d in docs]
    texts = [d['text'] for d in docs]
    metadatas = [d.get('metadata', {}) for d in docs]
    embeddings = [ollama_embed(t) for t in texts]
    coll.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)


def query_similar(query_text: str, n: int = 5) -> List[Dict[str, Any]]:
    coll = get_collection()
    qvec = ollama_embed(query_text)
    res = coll.query(query_embeddings=[qvec], n_results=n)
    results = []
    for i in range(len(res.get('ids', [[]])[0])):
        results.append({
            'id': res['ids'][0][i],
            'text': res['documents'][0][i],
            'metadata': res['metadatas'][0][i],
            'distance': res.get('distances', [[None]])[0][i] if res.get('distances') else None,
        })
    return results