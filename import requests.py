import requests
import json

url = "https://southamerica-east1-mobile-testes.cloudfunctions.net/disponilidadesParaMedicamentos"

headers = {
    "accept": "*/*",
    "content-type": "application/json",
    "origin": "https://e-saudesp.prefeitura.sp.gov.br",
    "referer": "https://e-saudesp.prefeitura.sp.gov.br/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "x-firebase-appcheck": "eyJraWQiOiIwMHlhdmciLCJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxOjQ5MTc5NTU3OTk2NTp3ZWI6MzI5ZjZjZjQ1NjAxMGE4ZDcyOTY1NCIsImF1ZCI6WyJwcm9qZWN0c1wvNDkxNzk1NTc5OTY1IiwicHJvamVjdHNcL21vYmlsZS10ZXN0ZXMiXSwicHJvdmlkZXIiOiJyZWNhcHRjaGFfZW50ZXJwcmlzZSIsImlzcyI6Imh0dHBzOlwvXC9maXJlYmFzZWFwcGNoZWNrLmdvb2dsZWFwaXMuY29tXC80OTE3OTU1Nzk5NjUiLCJleHAiOjE3NTU3NDEzMDUsImlhdCI6MTc1NTczNzcwNSwianRpIjoiVkxRbkFKZ0VFM0VuS0JLQ2ZIVmpFTS13WDE5ZmVUcE9ZTThnLTNWSnVyQSJ9.B1lSbm3Yvz8RUZIaLnXFJG4MIvR4WhNn4C4p4hfoTyvDF2_sXJ-BAsBcheKkJ69dAIMJwAjIfY_qcMzFP8mCl3KVASQxGnxJTGBBpVmiQiSW-VsHJPYhhiz0dgLpvtHANOu2ldVNPsLdWSJOpFM82JHPZmixcbLTkITEEAsrcipl_y37BhzQ1KA7Dazs-E2ztYrKMqfqyLsdlJ2c-HXLpB8duAUzBQazMYFTfZpiUn3cG0QzNIF_p2MZnGx20Q83iXxbwreT1d9-m40Uv_BOVEydN0PrB3ElhOin-8GTssZfEamR32sJPWBQCtmac8zL2PIfAZQJr7TRDJMM1aqEFyidw6OQDHXCZ568odGU555VjRys1sRTz-g4wdT--84RrTULinWrrsuCZneXA_TChunoYRSxeHNB8uqy_AdE3x7D3RbIhhi_TthZMI4meaMWj5xRHa7ERUzOM1HRy9kxrFm1-AckHtnTx2DEVteOyrO4kcoHYWzwyDxbGduLqfZ3"  # copie o token válido do DevTools
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
        print("✅ Resposta salva em 'resposta_api.json'")
    except Exception as e:
        print("Erro ao converter para JSON:", e)
else:
    print("Erro:", response.status_code, response.text)