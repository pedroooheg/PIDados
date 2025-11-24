import pandas as pd
import folium
from folium.plugins import HeatMap

# =====================================================
# 1. Ler o CSV exportado do SQL Server
# =====================================================
arquivo_csv = 'data/retiradas_unidades_coords.csv'

# Detectar separador automaticamente
with open(arquivo_csv, 'r', encoding='utf-8') as f:
    primeira_linha = f.readline()
sep = ';' if ';' in primeira_linha else ','

# Ler CSV
df = pd.read_csv(arquivo_csv, sep=sep, encoding='utf-8')

# Padronizar nomes das colunas
df.columns = df.columns.str.strip().str.lower()

print("Colunas detectadas:", df.columns.tolist())
print("Total de registros:", len(df))

# =====================================================
# 2. Limpar e converter dados numéricos
# =====================================================
# Garantir que as colunas essenciais existam
colunas_necessarias = ['latitude', 'longitude', 'total_retirado', 'nome']
for col in colunas_necessarias:
    if col not in df.columns:
        raise KeyError(f"Coluna obrigatória '{col}' não encontrada no CSV.")

# Converter tipos
df = df.dropna(subset=['latitude', 'longitude', 'total_retirado'])
df['latitude'] = df['latitude'].astype(str).str.replace(',', '.').astype(float)
df['longitude'] = df['longitude'].astype(str).str.replace(',', '.').astype(float)
df['total_retirado'] = df['total_retirado'].astype(float)

# =====================================================
# 3. Normalizar valores para não "estourar" o mapa
# =====================================================
cap = df['total_retirado'].quantile(0.95)
cap = cap if cap > 0 else df['total_retirado'].max() or 1.0
df['peso'] = df['total_retirado'].clip(upper=cap) / cap

print(f"Normalização feita (cap no percentil 95: {cap:.2f})")

# =====================================================
# 4. Criar o mapa base
# =====================================================
centro = [-23.5504533, -46.6339112]  # Centro de São Paulo
m = folium.Map(location=centro, zoom_start=11, tiles='OpenStreetMap')

# =====================================================
# 5. Adicionar camada de mapa de calor (HeatMap)
# =====================================================
points = df[['latitude', 'longitude', 'peso']].values.tolist()
HeatMap(
    points,
    radius=18,
    blur=22,
    max_zoom=14,
).add_to(m)

# =====================================================
# 6. Adicionar marcadores com popup/tooltip
# =====================================================
for _, r in df.iterrows():
    total_fmt = f"{int(r['total_retirado']):,}".replace(",", ".")
    folium.CircleMarker(
        location=(r['latitude'], r['longitude']),
        radius=4,
        weight=0,
        fill=True,
        fill_opacity=0.85,
        color="#3388ff",
        tooltip=f"{r['nome']}<br>Total retirado: {total_fmt}"
    ).add_to(m)

# =====================================================
# 7. Salvar resultado
# =====================================================
saida_html = 'mapa_retiradas_heatmap.html'
m.save(saida_html)
print(f"✅ Mapa de calor gerado com sucesso: {saida_html}")
