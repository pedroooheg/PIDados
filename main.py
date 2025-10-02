import csv
import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Iterable
import MedPerUBS
from datetime import datetime
import subprocess
import sys

banco = 'banco_de_dados\inserir_dados.py'
DT = datetime.now()
NOME_ARQUIVO = DT.strftime("%d-%m-%y")
ARQ_UNIDADES = Path("data/ubs_upa.json")
ARQ_MEDICAMENTOS = Path("data/medicamentos.csv")
ARQ_SAIDA = Path(f"data/{NOME_ARQUIVO}.json")

DISTANCIA_MAX = 100                 # metros 
CONSULTA_EM_LOTE = True            # True = chamadas em grupo; False = 1 por medicamento'
MAX_MEDICAMENTOS_POR_CHAMADA = 5   # limite da API (máx. 5 por payload)
VERBOSE_MED = False                # True para imprimir cada medicamento consultado
LOG_QTD_WARN = True                # True para avisar quando não conseguir parsear quantidade

UNIDADES_LIMIT = None                # processa somente as primeiras N unidades (None para todas)
UNIDADES_OFFSET = 0                # pula as primeiras N unidades antes de começar
TARGET_CNES: List[int] = []        # opcional: processe apenas esses CNES (ex.: [2030969, 2752166])


def carregar_unidades() -> List[Dict[str, Any]]:
    with ARQ_UNIDADES.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["d"]

def carregar_medicamentos() -> List[Dict[str, str]]:
    meds: List[Dict[str, str]] = []
    with ARQ_MEDICAMENTOS.open("r", encoding="utf-8") as f:
        leitor = csv.reader(f)
        for i, row in enumerate(leitor):
            if not row or len(row) < 2:
                continue
            id_, nome = row[0].strip(), row[1].strip()
            if i == 0 and not id_.isdigit():
                continue
            meds.append({"id": id_, "nome": nome})
    return meds

def endereco_from_unidade(u: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "end": f"{u['Logradouro']}, {u['Numero']} - {u['Bairro']}",
        "lat": u["Geo"]["Latitude"],
        "lng": u["Geo"]["Longitude"],
    }

def normalizar_quantidade(v: Any, med_nome: Optional[str] = None) -> Optional[int]:

    if v is None:
        return None
    s = str(v).strip()
    if s == "" or s.lower() == "null":
        return None
    digits = re.sub(r"\D", "", s)  
    if digits == "":
        if LOG_QTD_WARN:
            print(f"[WARN] Quantidade não numérica para '{med_nome or ''}': '{s}'")
        return None
    try:
        return int(digits)
    except Exception:
        if LOG_QTD_WARN:
            print(f"[WARN] Falha ao converter quantidade para '{med_nome or ''}': '{s}' -> '{digits}'")
        return None

def chunks(seq: List[Dict[str, str]], n: int) -> Iterable[List[Dict[str, str]]]:
    for i in range(0, len(seq), n):
        yield seq[i:i+n]

def consolidar_resposta_primeiro_item(
    resposta: Dict[str, Any],
    dist_max: int,
    bucket_unidade: Dict[str, Dict[str, Any]],
    unidade_meta: Dict[str, Any],   # dados da un
):

    result = resposta.get("result", {})
    disps = result.get("disponibilidade", [])
    if not disps:
        return

    item = disps[0] 
    distance = item.get("distance")
    if distance is None or distance > dist_max:
        return

    # chave de agrupamento por CNES da unidade consultada
    cnes = unidade_meta["Cnes"]
    if cnes not in bucket_unidade:
        bucket_unidade[cnes] = {
            "cnes": cnes,
            "codSQCN": unidade_meta.get("CodSQCN"),
            "nome": unidade_meta.get("Nome"),
            "logradouro": unidade_meta.get("Logradouro"),
            "numero": unidade_meta.get("Numero"),
            "bairro": unidade_meta.get("Bairro"),
            "cep": unidade_meta.get("Cep"),
            "horario": unidade_meta.get("Horario"),
            "telefones": [t for t in [unidade_meta.get("Telefone1"), unidade_meta.get("Telefone2")] if t],
            "coordenadas": {
                "lat": unidade_meta["Geo"]["Latitude"],
                "lng": unidade_meta["Geo"]["Longitude"],
            },
            "medicamentos": {}  # mapa interno por nome
        }

    meds_map = bucket_unidade[cnes]["medicamentos"]

    for q in item.get("quantidades", []):
        nome_med = q.get("medicamento")
        if not nome_med:
            continue
        qtd = normalizar_quantidade(q.get("quantidade"), med_nome=nome_med)
        nivel = q.get("nivelDisponibilidade")
        cor = q.get("cor")
        msgs = q.get("mensagens", [])

        if nome_med not in meds_map:
            meds_map[nome_med] = {
                "nome": nome_med,
                "quantidade": qtd,
                "nivelDisponibilidade": nivel,
                "cor": cor,
                "mensagens": msgs
            }
        else:
            # manter a MAIOR quantidade e mesclar mensagens
            ex = meds_map[nome_med]
            if qtd is not None and (ex["quantidade"] is None or qtd > ex["quantidade"]):
                ex["quantidade"] = qtd
                ex["nivelDisponibilidade"] = nivel
                ex["cor"] = cor
            urls = {m.get("url") for m in ex["mensagens"] if "url" in m}
            for m in msgs:
                if m.get("url") not in urls:
                    ex["mensagens"].append(m)

def main():
    unidades = carregar_unidades()
    medicamentos = carregar_medicamentos()

    original_total = len(unidades)

    if TARGET_CNES:
        unidades = [u for u in unidades if u.get("Cnes") in set(TARGET_CNES)]

    filtrado_total = len(unidades)

    start = UNIDADES_OFFSET or 0
    if start < 0:
        start = 0
    end = filtrado_total if UNIDADES_LIMIT is None else min(filtrado_total, start + UNIDADES_LIMIT)
    unidades = unidades[start:end]

    print(f"[INFO] Unidades no arquivo: {original_total}. "
          f"Após filtro CNES: {filtrado_total}. "
          f"Processando janela {start+1}..{start+len(unidades)} ({len(unidades)} unidade(s)).")

    agrupado_por_cnes: Dict[str, Dict[str, Any]] = {}

    for idx, u in enumerate(unidades, start=1):
        print(f"\\n[UNIDADE {idx}/{len(unidades)}] {u['Nome']} (CNES {u['Cnes']})")
        ender = endereco_from_unidade(u)

        if CONSULTA_EM_LOTE:
            for cidx, lote in enumerate(chunks(medicamentos, MAX_MEDICAMENTOS_POR_CHAMADA), start=1):
                print(f"  - Enviando lote {cidx} (tamanho {len(lote)})")
                resp = MedPerUBS.consultar_lote(ender, lote)
                if resp:
                    consolidar_resposta_primeiro_item(resp, DISTANCIA_MAX, agrupado_por_cnes, u)
        else:
            for midx, med in enumerate(medicamentos, start=1):
                if VERBOSE_MED:
                    print(f"  - [{midx}/{len(medicamentos)}] {med['nome']} (ID {med['id']})")
                resp = MedPerUBS.consultar_um(ender, med)
                if resp:
                    consolidar_resposta_primeiro_item(resp, DISTANCIA_MAX, agrupado_por_cnes, u)

    saida = []
    for cnes, bloco in agrupado_por_cnes.items():
        meds_map = bloco.pop("medicamentos", {})
        bloco["medicamentos"] = sorted(list(meds_map.values()), key=lambda m: m["nome"])
        saida.append(bloco)

    # ordena por nome para estabilidade
    saida.sort(key=lambda x: x["nome"] or "")

    ARQ_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    with ARQ_SAIDA.open("w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"\\n[OK] Gerado: {ARQ_SAIDA}")

if __name__ == "__main__":
    main()
    try:
        subprocess.run([sys.executable, banco], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar banco: {e}")
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {banco}")
    
