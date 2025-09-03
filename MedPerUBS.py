from dotenv import load_dotenv
import requests
import json
import os


# caminho_token = r"C:\Users\Pedro\Documents\token.txt"
# with open(caminho_token, "r", encoding="utf-8") as f:
#     token_appcheck = f.read().strip()

def getDispMedicamentoPorUnidade(endereco, medicamento):
    load_dotenv()
    token_appcheck = os.getenv("TOKEN")

    url = "https://southamerica-east1-mobile-testes.cloudfunctions.net/disponilidadesParaMedicamentos"

    headers = {
        "accept": "*/*",
        "content-type": "application/json",
        "x-firebase-appcheck": token_appcheck
    }

    payload = {
        "data": {
            "endereco": f"{endereco['end']}, São Paulo - SP",
            "coordenadas": {
                "lat": endereco['lat'],
                "lng": endereco['lng']
            },
            "medicamentos": [
                {
                    "id": medicamento["id"],
                    "name": medicamento["nome"]
                }
            ]
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        try:
            data = response.json()  # Converte a resposta em dicionário Python
            with open("data/resposta_api.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)  # Salva formatado
            print("Resposta salva em 'resposta_api.json'")
        except Exception as e:
            print("Erro ao converter para JSON:", e)
    else:
        print("Erro:", response.status_code, response.text)