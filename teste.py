import folium
from folium.plugins import HeatMap
import json

# 1. Caminho para o seu arquivo JSON
arquivo_json = 'data/ubs_upa.json'

# 2. Carregar os dados do arquivo JSON
try:
    with open(arquivo_json, 'r', encoding='utf-8') as f:
        dados_ubs_upa = json.load(f)
except FileNotFoundError:
    print(f"Erro: O arquivo '{arquivo_json}' não foi encontrado.")
    exit()
except json.JSONDecodeError:
    print(f"Erro: Não foi possível decodificar o JSON do arquivo '{arquivo_json}'.")
    exit()

# O seu JSON tem uma chave 'd' que contém a lista de objetos
lista_unidades = dados_ubs_upa.get('d', [])

# 3. Extrair as coordenadas de Latitude e Longitude
coordenadas_ubs_upa = []
for unidade in lista_unidades:
    geo_data = unidade.get('Geo')
    if geo_data and 'Latitude' in geo_data and 'Longitude' in geo_data:
        latitude = geo_data['Latitude']
        longitude = geo_data['Longitude']
        coordenadas_ubs_upa.append([latitude, longitude])

# 4. Verificar se há dados para plotar
if not coordenadas_ubs_upa:
    print("Nenhuma coordenada válida encontrada no arquivo JSON para criar o mapa de calor.")
    exit()

# 5. Definir o centro do mapa com a coordenada que você forneceu
# Formato: [latitude, longitude]
centro_mapa = [-23.5504533, -46.6339112]
# Definimos um zoom maior para focar na área, já que a coordenada é específica
zoom_inicial = 15

# 6. Criar o mapa base
mapa_ubs = folium.Map(location=centro_mapa, zoom_start=zoom_inicial)

# 7. Adicionar a camada de mapa de calor
HeatMap(coordenadas_ubs_upa, radius=15, max_zoom=14).add_to(mapa_ubs)

# 8. Salvar o mapa em um arquivo HTML
mapa_ubs.save("mapa_de_calor_ubs_upa_centralizado.html")

print("Mapa de calor das UBS/UPAs gerado com sucesso!")
print("O arquivo 'mapa_de_calor_ubs_upa_centralizado.html' foi criado e está centralizado na sua coordenada.")