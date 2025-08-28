import requests
import json


caminho_token = r"C:\Users\Pedro\Documents\token.txt"
with open(caminho_token, "r", encoding="utf-8") as f:
    token_appcheck = f.read().strip()

url = "https://southamerica-east1-mobile-testes.cloudfunctions.net/disponilidadesParaMedicamentos"

headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://e-saudesp.prefeitura.sp.gov.br",
    "referer": "https://e-saudesp.prefeitura.sp.gov.br/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-firebase-appcheck": token_appcheck
}

payload = {
    "data": {
        "endereco": "Avenida Engenheiro Eusébio Stevaux, 2496 - Jurubatuba, São Paulo - SP",
        "coordenadas": {
            "lat": -23.6803402,
            "lng": -46.692731
        },
        "medicamentos": [
            {
                "id": "1106400100100097",
                "name": "DIPIRONA SÓDICA 500 MG COMPRIMIDO"
            }
        ]
    }
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code == 200:
    try:
        data = response.json()  # Converte a resposta em dicionário Python
        with open("resposta_api.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)  # Salva formatado
        print("Resposta salva em 'resposta_api.json'")
    except Exception as e:
        print("Erro ao converter para JSON:", e)
else:
    print("Erro:", response.status_code, response.text)