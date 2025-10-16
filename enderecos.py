import requests
import json

# caminho_token  = r""
# with open(caminho_token, "r", encoding="utf-8") as f:
#     token_appcheck =f.read().strip()

url = "https://cep-brasil-491795579965.southamerica-east1.run.app/ubs-reference/local"

headers = {
"Host": "cep-brasil-491795579965.southamerica-east1.run.app",
"Accept": "*/*",
"Content-Type": "application/json; charset=utf-8",
"Connection": "keep-alive",
"Priority": "u=4",
"TE": "trailers"
}

payload = {"logradouro":"Rua Pedro correia garcao"}


response = requests.post(url, headers=headers, json=payload)
if response.status_code in [200, 201]:
    try:
        data = response.json()  
        with open("data/resposta_api_endereco.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)  # Salva formatado
        print("Resposta salva em 'teste_api.json'")
    except Exception as e:
        print("Erro ao converter para JSON:", e)
else:
    print("Erro:", response.status_code, response.text)