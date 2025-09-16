from dotenv import load_dotenv
import requests
import os
import json
import time
from typing import List, Dict, Any, Optional

load_dotenv()
TOKEN_APPCHECK = os.getenv("TOKEN")

URL = "https://southamerica-east1-mobile-testes.cloudfunctions.net/disponilidadesParaMedicamentos"

def _headers() -> Dict[str, str]:
    token = TOKEN_APPCHECK or os.getenv("TOKEN")
    return {
        "accept": "*/*",
        "content-type": "application/json",
        "x-firebase-appcheck": token if token else ""
    }

def _post(endereco: Dict[str, Any], medicamentos: List[Dict[str, str]], timeout: int = 60) -> Optional[Dict[str, Any]]:

    if not TOKEN_APPCHECK and not os.getenv("TOKEN"):
        print("[API] AVISO: TOKEN não encontrado no ambiente (.env).")
    if not medicamentos:
        print("[API] Nada a consultar: lista de medicamentos vazia.")
        return None

    payload = {
        "data": {
            "endereco": f"{endereco['end']}, São Paulo - SP",
            "coordenadas": {"lat": endereco["lat"], "lng": endereco["lng"]},
            "medicamentos": [{"id": m["id"], "name": m["nome"]} for m in medicamentos]
        }
    }

    meds_count = len(payload["data"]["medicamentos"])
    start = time.monotonic()
    try:
        resp = requests.post(URL, headers=_headers(), json=payload, timeout=timeout)
        elapsed_ms = int((time.monotonic() - start) * 1000)

        print(f"[API] POST {URL} | meds={meds_count} | status={resp.status_code} | {elapsed_ms} ms")

        if resp.status_code != 200:
            body_preview = (resp.text or "")[:200].replace("\n", " ")
            print(f"[API] ERRO HTTP {resp.status_code}: {body_preview}")
            return None

        try:
            return resp.json()
        except json.JSONDecodeError as je:
            print(f"[API] ERRO JSON Decode: {je}")
            body_preview = (resp.text or "")[:200].replace("\n", " ")
            print(f"[API] Corpo (preview): {body_preview}")
            return None

    except requests.Timeout:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        print(f"[API] TIMEOUT após {elapsed_ms} ms (meds={meds_count})")
        return None
    except requests.RequestException as re:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        print(f"[API] FALHA de rede ({elapsed_ms} ms): {re}")
        return None
    except Exception as e:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        print(f"[API] EXCEÇÃO inesperada ({elapsed_ms} ms): {e}")
        return None

def consultar_um(endereco: Dict[str, Any], medicamento: Dict[str, str]) -> Optional[Dict[str, Any]]:
    """Consulta a API para apenas um medicamento."""
    return _post(endereco, [medicamento])

def consultar_lote(endereco: Dict[str, Any], medicamentos: List[Dict[str, str]]) -> Optional[Dict[str, Any]]:
    """Consulta a API para um lote (limite recomendado: 5 medicamentos)."""
    return _post(endereco, medicamentos)
